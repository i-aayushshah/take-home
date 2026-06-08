"""Redis client singleton and FastAPI dependency."""

from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from app.config import get_settings

_settings = get_settings()
_pool = ConnectionPool.from_url(_settings.redis_url, decode_responses=True)


def get_redis_client() -> Redis:
    """Return a Redis client backed by the shared connection pool singleton."""
    return Redis(connection_pool=_pool)


async def get_redis() -> AsyncGenerator[Redis, None]:
    """FastAPI dependency that yields a Redis client from the shared pool."""
    client = get_redis_client()
    yield client
