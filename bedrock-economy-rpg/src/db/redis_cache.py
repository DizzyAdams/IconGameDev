import redis.asyncio as redis


class RedisCache:
    def __init__(self, cfg: dict):
        self._client = redis.Redis(
            host=cfg["host"],
            port=cfg["port"],
            db=cfg["db"],
            decode_responses=True,
        )

    async def close(self):
        await self._client.aclose()

    async def get(self, key: str):
        return await self._client.get(key)

    async def set(self, key: str, value, ttl: int = 300):
        await self._client.set(key, value, ex=ttl)

    async def delete(self, key: str):
        await self._client.delete(key)
