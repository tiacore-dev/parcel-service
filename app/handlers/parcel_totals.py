from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import List, Tuple
from uuid import UUID

from fastapi import HTTPException

from app.database.models import Parcel, ParcelCargo


def _to_dec(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def _quantize(x: Decimal, places: int) -> Decimal:
    # places = 2  -> 0.01; places = 9 -> 0.000000001 и т.д.
    quant = Decimal(1).scaleb(-places)
    return x.quantize(quant, rounding=ROUND_HALF_UP)


async def recompute_parcel_totals(parcel_id: UUID) -> None:
    """
    Суммируем quantity/total_weight/total_volume по всем грузам этой накладной,
    квантуем под точность полей Parcel.weight/Parcel.volume и сохраняем.
    Без QuerySet.aggregate().
    """
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        return

    # Заберём только нужные поля, чтобы не тащить целые объекты:
    # вернётся List[Tuple[quantity, total_weight, total_volume]]
    rows: List[Tuple[int, Decimal | None, Decimal | None]] = await ParcelCargo.filter(parcel_id=parcel_id).values_list(
        "quantity", "total_weight", "total_volume"
    )

    places_sum = 0
    weight_sum = Decimal("0")
    volume_sum = Decimal("0")

    for qty, total_weight, total_volume in rows:
        places_sum += int(qty or 0)
        if total_weight is not None:
            weight_sum += _to_dec(total_weight)
        if total_volume is not None:
            volume_sum += _to_dec(total_volume)

    # Подгоняем точность под схему Parcel.*
    weight_places = Parcel._meta.fields_map["weight"].decimal_places  # type: ignore
    volume_places = Parcel._meta.fields_map["volume"].decimal_places  # type: ignore
    weight_sum_q = _quantize(weight_sum, weight_places)
    volume_sum_q = _quantize(volume_sum, volume_places)

    # Защита от переполнения согласно схеме Decimal(max_digits, decimal_places)
    vol_field = Parcel._meta.fields_map["volume"]
    vol_limit = Decimal(10) ** (vol_field.max_digits - vol_field.decimal_places)  # type: ignore
    if abs(volume_sum_q) >= vol_limit:
        max_value = _quantize(vol_limit - Decimal(1).scaleb(-volume_places), volume_places)
        raise HTTPException(
            status_code=400,
            detail=f"Суммарный объём {volume_sum_q} превышает максимально допустимый ({max_value})",
        )

    parcel.places_count = places_sum
    parcel.weight = weight_sum_q
    parcel.volume = volume_sum_q
    await parcel.save(update_fields=["places_count", "weight", "volume"])
