import redis.asyncio as aioredis

from app.core.config import settings

redis_client = aioredis.Redis.from_url(
    str(settings.REDIS_URL),
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30,
)


async def get_redis() -> aioredis.Redis:
    return redis_client


class CacheService:
    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key) > 0

    async def increment(self, key: str, ttl: int = 60) -> int:
        val = await self.redis.incr(key)
        if val == 1:
            await self.redis.expire(key, ttl)
        return val
