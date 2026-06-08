"""Auth unit of work coordinating the user repository."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.infrastructure.user_repository import UserRepository


class AuthUnitOfWork:
    """Coordinates auth repositories under one database session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.users = UserRepository(session)

    async def commit(self) -> None:
        """Flush and commit the current transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        await self._session.rollback()
