from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from typing import Union
from uuid import UUID

from tortoise.functions import Sum

from app.database.models import Parcel, ParcelCargo

NumberLike = Union[Decimal, float, int, str]


def _to_dec(x: NumberLike) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))


def _q2(x: NumberLike) -> Decimal:
    return _to_dec(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _q9(x: NumberLike) -> Decimal:
    return _to_dec(x).quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)


async def recompute_parcel_totals(parcel_id: UUID) -> None:
    """
    Пересчитывает places_count, weight, volume накладной из ParcelCargo.*
    Правит значения под точность БД и проверяет переполнение под (10,2)/(10,9).
    """
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        return

    row = await (
        ParcelCargo.filter(parcel_id=parcel_id)
        .annotate(places_sum=Sum("quantity"), weight_sum=Sum("total_weight"), volume_sum=Sum("total_volume"))
        .values("places_sum", "weight_sum", "volume_sum")
    )
    first = row[0] if row else {}
    places = int(first.get("places_sum") or 0)
    weight = _q2(first.get("weight_sum") or 0)
    volume = _q9(first.get("volume_sum") or 0)

    # Ограничение для Decimal(10,9): |value| < 10
    if abs(volume) >= Decimal("10"):
        # Можно выбросить 400/422 — на ваш выбор
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Суммарный объём превышает максимально допустимый (9.999999999)")

    parcel.places_count = places
    parcel.weight = weight
    parcel.volume = volume
    await parcel.save(update_fields=["places_count", "weight", "volume"])
