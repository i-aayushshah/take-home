"""Database engine and session factory singletons."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

_settings = get_settings()
_engine = create_async_engine(_settings.database_url, echo=False)
_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession for use as a FastAPI dependency."""
    async with _session_factory() as session:
        yield session
