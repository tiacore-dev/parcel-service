from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.database.models import Parcel, Service


def _calc_base_value(parcel: Parcel) -> float:
    w = float(parcel.weight or 0.0)
    v = float(parcel.volume or 0.0)
    return max(w, v * 200.0)


async def recompute_services_base_value_for_parcel(parcel_id: UUID, modified_by: Optional[UUID] = None) -> int:
    """
    Пересчитывает base_value для всех услуг указанной накладной.
    Возвращает количество обновлённых строк.
    """
    parcel = await Parcel.get_or_none(id=parcel_id)
    if not parcel:
        return 0

    base_value = _calc_base_value(parcel)

    q = Service.filter(parcel_id=parcel_id)
    # одно UPDATE для всех услуг накладной
    if modified_by is not None and "modified_by" in Service._meta.fields_map:
        return await q.update(base_value=base_value, modified_by=modified_by)
    return await q.update(base_value=base_value)
