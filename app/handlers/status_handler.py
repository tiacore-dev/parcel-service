import json
from datetime import datetime
from uuid import UUID

from fastapi_cache import FastAPICache

from app.database.models import ParcelStatusEnum


def get_parcel_status_cache_key(parcel_id: UUID) -> str:
    return f"parcel:{parcel_id}"


async def save_parcel_status_to_cache(
    parcel_id: UUID,
    document_id: UUID,
    status: ParcelStatusEnum,
    value: UUID | None,
    date: datetime,
    comment: str | None,
):
    key = get_parcel_status_cache_key(parcel_id)
    data = {
        "parcel_id": str(parcel_id),
        "document_id": str(document_id),
        "status": status.value,
        "value": str(value) if value else None,
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
