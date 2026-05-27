"""Redis cache utilities."""

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client instance
redis_client: aioredis.Redis | None = None


async def get_redis_client() -> aioredis.Redis:
    """Get or create Redis client."""
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf-8",
        )
    return redis_client


async def get_cached_questions(key: str) -> list[dict[str, Any]] | None:
    """
    Get cached questions from Redis.

    Args:
        key: Cache key (e.g., "questions:general" or "questions:specialized:F1")

    Returns:
        List of question dicts if found, None otherwise
    """
    try:
        client = await get_redis_client()
        data = await client.get(key)
        if data:
            logger.debug("Cache HIT for key: %s", key)
            return json.loads(data)
        logger.debug("Cache MISS for key: %s", key)
        return None
    except Exception as e:
        logger.error("Redis get error for key %s: %s", key, e)
        return None


async def set_cached_questions(
    key: str, data: list[dict[str, Any]], ttl: int = 300
) -> None:
    """
    Cache questions in Redis.

    Args:
        key: Cache key
        data: List of question dicts to cache
        ttl: Time to live in seconds (default 5 minutes)
    """
    try:
        client = await get_redis_client()
        await client.setex(key, ttl, json.dumps(data))
        logger.debug("Cached data for key: %s (TTL: %ds)", key, ttl)
    except Exception as e:
        logger.error("Redis set error for key %s: %s", key, e)


async def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache keys matching pattern.

    Args:
        pattern: Redis key pattern (e.g., "questions:*")

    Returns:
        Number of keys deleted
    """
    try:
        client = await get_redis_client()
        keys = await client.keys(pattern)
        if keys:
            deleted = await client.delete(*keys)
            logger.info("Invalidated %d cache keys matching: %s", deleted, pattern)
            return deleted
        return 0
    except Exception as e:
        logger.error("Redis invalidate error for pattern %s: %s", pattern, e)
        return 0


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection closed")
