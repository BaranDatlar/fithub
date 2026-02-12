import json
import structlog

from app.db.redis import get_redis

logger = structlog.get_logger()


class RedisService:
    """Centralized Redis operations for caching, counters, and session state."""

    # --- Generic Cache ---

    @staticmethod
    async def get_cached(key: str) -> dict | list | None:
        redis = get_redis()
        data = await redis.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    async def set_cached(key: str, value: dict | list, ttl: int) -> None:
        redis = get_redis()
        await redis.set(key, json.dumps(value, default=str), ex=ttl)

    @staticmethod
    async def invalidate(key: str) -> None:
        redis = get_redis()
        await redis.delete(key)

    @staticmethod
    async def invalidate_pattern(pattern: str) -> None:
        redis = get_redis()
        async for key in redis.scan_iter(match=pattern):
            await redis.delete(key)

    # --- Atomic Counters (Class Capacity) ---

    @staticmethod
    async def set_capacity(class_id: str, capacity: int, ttl: int) -> None:
        redis = get_redis()
        key = f"class:{class_id}:spots_left"
        await redis.set(key, capacity, ex=ttl)

    @staticmethod
    async def decrement_capacity(class_id: str) -> int:
        """Atomically decrement class capacity. Returns new value."""
        redis = get_redis()
        key = f"class:{class_id}:spots_left"
        result = await redis.decr(key)
        return result

    @staticmethod
    async def increment_capacity(class_id: str) -> int:
        """Atomically increment class capacity. Returns new value."""
        redis = get_redis()
        key = f"class:{class_id}:spots_left"
        result = await redis.incr(key)
        return result

    @staticmethod
    async def get_capacity(class_id: str) -> int | None:
        redis = get_redis()
        key = f"class:{class_id}:spots_left"
        val = await redis.get(key)
        return int(val) if val is not None else None
