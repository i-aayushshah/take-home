"""Auth repository interface."""

from typing import Protocol

from app.api.v1.auth.domain.user import UserEntity


class UserRepositoryProtocol(Protocol):
    """Persistence contract for user entities."""

    async def get_by_id(self, entity_id: str) -> UserEntity | None:
        """Return the user with the given identifier or None."""

    async def find_by_email(self, email: str) -> UserEntity | None:
        """Return the user with the given email or None."""

    async def save(self, entity: UserEntity) -> UserEntity:
        """Persist the user and return the saved entity."""
