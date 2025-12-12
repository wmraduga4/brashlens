"""Redis client configuration."""
from typing import AsyncGenerator

from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings


# Создаем connection pool для Redis
redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None


def get_redis_pool() -> ConnectionPool:
    """Получить или создать connection pool для Redis."""
    global redis_pool
    if redis_pool is None:
        redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=10,
        )
    return redis_pool


def get_redis_client() -> Redis:
    """Получить или создать Redis client."""
    global redis_client
    if redis_client is None:
        pool = get_redis_pool()
        redis_client = Redis(connection_pool=pool)
    return redis_client


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Dependency для получения Redis client в FastAPI.
    
    Yields:
        Redis: Redis client instance
    """
    client = get_redis_client()
    try:
        yield client
    finally:
        # Не закрываем client, так как используем connection pool
        pass


async def close_redis() -> None:
    """Закрыть Redis connection pool."""
    global redis_client, redis_pool
    if redis_client:
        await redis_client.aclose()
        redis_client = None
    if redis_pool:
        await redis_pool.aclose()
        redis_pool = None
