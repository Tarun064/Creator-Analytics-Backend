"""Redis client for caching."""
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)
_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Get Redis connection. Creates one if not exists."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def cache_get(key: str) -> Any | None:
    """Get value from cache. Returns None if miss or error."""
    try:
        r = await get_redis()
        val = await r.get(key)
        if val is None:
            return None
        return json.loads(val)
    except Exception as e:
        logger.warning("Redis get error: %s", e)
        return None


async def cache_set(key: str, value: Any, ttl_seconds: int = 300) -> None:
    """Set value in cache with optional TTL."""
    try:
        r = await get_redis()
        await r.set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except Exception as e:
        logger.warning("Redis set error: %s", e)


async def cache_delete(key: str) -> None:
    """Delete key from cache."""
    try:
        r = await get_redis()
        await r.delete(key)
    except Exception as e:
        logger.warning("Redis delete error: %s", e)
