from core.config import redis_settings
from dependencies.redis import get_redis
from redis.asyncio import Redis


async def get_redis_session() -> Redis:
    return await get_redis(
        host=redis_settings.host,
        port=redis_settings.port
    )
