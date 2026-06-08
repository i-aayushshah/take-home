"""Redis-backed rate limiter used as a FastAPI dependency."""

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis

from app.shared.redis import get_redis


class RateLimiter:
    """Fixed-window rate limiter backed by Redis.

    Args:
        max_requests: Maximum allowed requests within the window.
        window_seconds: Duration of the window in seconds.
    """

    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds

    async def __call__(self, request: Request, redis: Redis = Depends(get_redis)) -> None:
        """Enforce the rate limit for the current request.

        Args:
            request: The incoming FastAPI request.
            redis: Injected Redis client.

        Raises:
            HTTPException: 429 if the caller has exceeded the allowed rate.
        """
        key = self._build_key(request)
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, self._window_seconds)
        if count > self._max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self._max_requests} requests per {self._window_seconds}s",
            )

    def _build_key(self, request: Request) -> str:
        """Build a Redis key scoped to the client IP and route path.

        Args:
            request: The incoming request.

        Returns:
            A string key in the format ``rl:<ip>:<path>``.
        """
        client_ip = request.client.host if request.client else "unknown"
        return f"rl:{client_ip}:{request.url.path}"
