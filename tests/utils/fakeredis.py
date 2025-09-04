from __future__ import annotations

from typing import Dict, Set


class AsyncMemoryPipeline:
    def __init__(self, redis: "AsyncMemoryRedis"):
        self._redis = redis
        self._ops = []

    def delete(self, key: str) -> "AsyncMemoryPipeline":
        self._ops.append(("delete", key))
        return self

    def sadd(self, key: str, *members: str) -> "AsyncMemoryPipeline":
        self._ops.append(("sadd", key, members))
        return self

    def srem(self, key: str, *members: str) -> "AsyncMemoryPipeline":
        self._ops.append(("srem", key, members))
        return self

    async def execute(self) -> list:
        results = []
        for op in self._ops:
            kind = op[0]
            if kind == "delete":
                results.append(await self._redis.delete(op[1]))
            elif kind == "sadd":
                results.append(await self._redis.sadd(op[1], *op[2]))
            elif kind == "srem":
                results.append(await self._redis.srem(op[1], *op[2]))
        self._ops.clear()
        return results

    async def __aenter__(self) -> "AsyncMemoryPipeline":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        pass


class AsyncMemoryRedis:
    """Очень простой in-memory Redis с нужными командами для scope_store."""

    def __init__(self):
        self._sets: Dict[str, Set[str]] = {}

    async def smembers(self, key: str):
        # можно вернуть bytes или str — твой код умеет оба
        return {m.encode("utf-8") for m in self._sets.get(key, set())}

    async def sadd(self, key: str, *members: str) -> int:
        s = self._sets.setdefault(key, set())
        added = 0
        for m in members:
            if m not in s:
                s.add(m)
                added += 1
        return added

    async def srem(self, key: str, *members: str) -> int:
        s = self._sets.setdefault(key, set())
        removed = 0
        for m in members:
            if m in s:
                s.remove(m)
                removed += 1
        return removed

    async def sismember(self, key: str, member: str):
        return 1 if member in self._sets.get(key, set()) else 0

    async def delete(self, key: str) -> int:
        return 1 if self._sets.pop(key, None) is not None else 0

    def pipeline(self, *, transaction: bool = True) -> AsyncMemoryPipeline:
        return AsyncMemoryPipeline(self)
