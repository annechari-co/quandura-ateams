"""Redis connection for caching and pub/sub."""

from functools import lru_cache

import redis.asyncio as redis

from app.core.config import get_settings


@lru_cache
def get_redis_pool() -> redis.ConnectionPool:
    """Get cached Redis connection pool."""
    settings = get_settings()
    return redis.ConnectionPool.from_url(settings.redis_url)


async def get_redis() -> redis.Redis:
    """Get Redis client from pool."""
    pool = get_redis_pool()
    return redis.Redis(connection_pool=pool)
