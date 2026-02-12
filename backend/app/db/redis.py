import redis.asyncio as aioredis
import structlog

from app.config import settings

logger = structlog.get_logger()

_redis: aioredis.Redis | None = None


async def connect_redis() -> None:
    global _redis
    _redis = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    await _redis.ping()
    logger.info("redis_connected")


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("redis_disconnected")


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis is not connected. Call connect_redis() first.")
    return _redis
