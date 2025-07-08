import json
from datetime import datetime
from uuid import UUID

from fastapi_cache import FastAPICache

from app.database.models import ParcelStatus, ParcelStatusEnum


def get_parcel_status_cache_key(parcel_id: UUID) -> str:
    return f"parcel:{parcel_id}"


async def save_parcel_status_to_cache(
    parcel_id: UUID,
    document_id: UUID,
    document_type: str,
    status: ParcelStatusEnum,
    value: UUID | None,
    value_type: str | None,
    date: datetime,
    comment: str | None,
):
    key = get_parcel_status_cache_key(parcel_id)
    data = {
        "parcel_id": str(parcel_id),
        "document_id": str(document_id),
        "document_type": document_type,
        "status": status.value,
        "value": str(value) if value else None,
        "value_type": value_type if value_type else None,
        "date": date.isoformat(),
        "comment": comment,
    }
    serialized = json.dumps(data)
    await FastAPICache.get_backend().set(key, serialized.encode("utf-8"), expire=600)

    return data


async def invalidate_parcel_status_cache(parcel_id: UUID):
    key = get_parcel_status_cache_key(parcel_id)
    await FastAPICache.clear(key)


async def get_cached_parcel_status_data(parcel_id: UUID) -> dict:
    backend = FastAPICache.get_backend()
    key = get_parcel_status_cache_key(parcel_id)
    cached = await backend.get(key)

    if cached and cached != b"":
        return json.loads(cached)
    else:
        return {"error": True}


async def recalculate_parcel_status(parcel_id: UUID):
    await invalidate_parcel_status_cache(parcel_id)
    latest_status = await ParcelStatus.filter(parcel_id=parcel_id).order_by("-date").first()

    if not latest_status:
        return {"error": "No statuses found for this parcel"}
    await save_parcel_status_to_cache(**latest_status.to_cache_dict())
