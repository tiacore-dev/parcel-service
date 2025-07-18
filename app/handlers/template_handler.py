from uuid import UUID

from fastapi import HTTPException

from app.database.models import Parcel
from app.utils.context_builders import build_parcel_context


async def handle_parcels(parcel_id: UUID):
    parcel = await Parcel.get_or_none(id=parcel_id)

    if not parcel:
        raise HTTPException(status_code=404, detail="Накладная не найдена")

    context = await build_parcel_context(parcel)

    return context, parcel.name
