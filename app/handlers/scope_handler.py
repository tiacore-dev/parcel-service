import json
from typing import List
from uuid import UUID

from fastapi_cache import FastAPICache


def get_parcel_scope_cache_key(parcel_id: UUID) -> str:
    return f"parcel:scope:{parcel_id}"


async def save_parcel_scope_to_cache(
    parcel_id: UUID,
    scope: List[str],
):
    key = get_parcel_scope_cache_key(parcel_id)
    data = {"parcel_scope": scope}
    serialized = json.dumps(data)
    await FastAPICache.get_backend().set(key, serialized.encode("utf-8"), expire=600)

    return data


async def invalidate_parcel_scope_cache(parcel_id: UUID):
    key = get_parcel_scope_cache_key(parcel_id)
    await FastAPICache.clear(key)


async def get_cached_parcel_scope_data(parcel_id: UUID) -> dict | None:
    backend = FastAPICache.get_backend()
    key = get_parcel_scope_cache_key(parcel_id)
    cached = await backend.get(key)

    if cached and cached != b"":
        return json.loads(cached)
    # else:
    #     data = await recalculate_parcel_scope(parcel_id)
    #     return data


# async def recalculate_parcel_scope(parcel_id: UUID):
#     await invalidate_parcel_scope_cache(parcel_id)
#     latest_scope = await ParcelScope.filter(parcel_id=parcel_id).order_by("-date").first()

#     if not latest_scope:
#         return None
#     data = await save_parcel_scope_to_cache(**latest_scope.to_cache_dict())
#     return data
