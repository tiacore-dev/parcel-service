# scope_store.py
from typing import Awaitable, Iterable, Protocol
from uuid import UUID


# ----- Протоколы для типизатора -----
class AsyncPipeline(Protocol):
    def delete(self, key: str) -> "AsyncPipeline": ...
    def sadd(self, key: str, *members: str) -> "AsyncPipeline": ...
    def srem(self, key: str, *members: str) -> "AsyncPipeline": ...
    async def execute(self) -> list: ...
    async def __aenter__(self) -> "AsyncPipeline": ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...


class RedisAsync(Protocol):
    def smembers(self, key: str) -> Awaitable[set[bytes]]: ...
    def sadd(self, key: str, *members: str) -> Awaitable[int]: ...
    def srem(self, key: str, *members: str) -> Awaitable[int]: ...
    def sismember(self, key: str, member: str) -> Awaitable[bool | int]: ...
    def delete(self, key: str) -> Awaitable[int]: ...
    def pipeline(self, *, transaction: bool = True) -> AsyncPipeline: ...


# ----- Ключи -----
def parcel_scope_key(parcel_id: UUID) -> str:
    return f"parcel:scope:{parcel_id}"  # Set[str(UUID)]


def company_index_key(company_id: UUID) -> str:
    return f"company:parcel-index:{company_id}"  # Set[str(parcel_id)]


# ----- Кодирование -----
def uuid_to_str(u: UUID) -> str:
    return str(u)  # с дефисами


def str_to_uuid(x: bytes | str) -> UUID:
    if isinstance(x, (bytes, bytearray)):
        x = x.decode("utf-8")
    return UUID(x)  # type: ignore


# ----- Прочитать scope -----
async def get_parcel_scope(redis_client: RedisAsync, parcel_id: UUID) -> set[UUID]:
    members = await redis_client.smembers(parcel_scope_key(parcel_id))
    return {str_to_uuid(m) for m in members}


# ----- Полная перезапись множества (без TTL) + обратный индекс -----
# scope_store.py
async def set_parcel_scope_with_index(
    redis_client: RedisAsync,
    parcel_id: UUID,
    company_ids: Iterable[UUID | str],
) -> None:
    def _to_uuid_str(x) -> str:
        from uuid import UUID as _UUID

        return str(x) if isinstance(x, _UUID) else str(_UUID(str(x)))

    new_ids = {_to_uuid_str(c) for c in company_ids}
    old_scope = await get_parcel_scope(redis_client, parcel_id)  # set[UUID]
    old_ids = {str(u) for u in old_scope}

    to_remove = old_ids - new_ids
    to_add = new_ids - old_ids

    pkey = parcel_scope_key(parcel_id)
    pipe = redis_client.pipeline(transaction=True)
    async with pipe:
        # пересобираем прямой scope
        pipe.delete(pkey)
        if new_ids:
            pipe.sadd(pkey, *new_ids)
        # обновляем обратный индекс
        for cid in to_remove:
            pipe.srem(company_index_key(UUID(cid)), uuid_to_str(parcel_id))
        for cid in to_add:
            pipe.sadd(company_index_key(UUID(cid)), uuid_to_str(parcel_id))
        await pipe.execute()


# ----- Точечные операции + обратный индекс -----
async def add_companies_with_index(
    redis_client: RedisAsync,
    parcel_id: UUID,
    company_ids: Iterable[UUID],
) -> int:
    ids = [uuid_to_str(c) for c in company_ids]
    if not ids:
        return 0
    pkey = parcel_scope_key(parcel_id)
    pipe = redis_client.pipeline(transaction=True)
    async with pipe:
        pipe.sadd(pkey, *ids)
        for cid in ids:
            pipe.sadd(company_index_key(UUID(cid)), uuid_to_str(parcel_id))
        res = await pipe.execute()
    # res[0] — сколько реально добавлено в прямой set
    return int(res[0]) if res else 0


async def remove_companies_with_index(
    redis_client: RedisAsync,
    parcel_id: UUID,
    company_ids: Iterable[UUID],
) -> int:
    ids = [uuid_to_str(c) for c in company_ids]
    if not ids:
        return 0
    pkey = parcel_scope_key(parcel_id)
    pipe = redis_client.pipeline(transaction=True)
    async with pipe:
        pipe.srem(pkey, *ids)
        for cid in ids:
            pipe.srem(company_index_key(UUID(cid)), uuid_to_str(parcel_id))
        res = await pipe.execute()
    return int(res[0]) if res else 0


# ----- Удаление ключей -----
async def delete_parcel_scope(redis_client: RedisAsync, parcel_id: UUID) -> None:
    # удалим прямой scope и выпилим parcel из всех компаний, где он числится
    current = await get_parcel_scope(redis_client, parcel_id)
    pipe = redis_client.pipeline(transaction=True)
    async with pipe:
        pipe.delete(parcel_scope_key(parcel_id))
        for cid in current:
            pipe.srem(company_index_key(cid), uuid_to_str(parcel_id))
        await pipe.execute()


# ----- Получить список доступных накладных компании -----
async def get_company_visible_parcels(redis_client: RedisAsync, company_id: UUID) -> set[UUID]:
    members = await redis_client.smembers(company_index_key(company_id))
    return {str_to_uuid(m) for m in members}


# ----- Быстрая проверка доступа -----
async def company_has_access(redis_client: RedisAsync, parcel_id: UUID, company_id: UUID) -> bool:
    res = await redis_client.sismember(parcel_scope_key(parcel_id), uuid_to_str(company_id))
    return bool(res)
