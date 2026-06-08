"""SQLAlchemy implementation of the user repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.domain.user import UserEntity
from app.db.models.user import UserModel
from app.shared.base_repository import AbstractRepository


class UserRepository(AbstractRepository[UserEntity]):
    """Persists and retrieves user entities via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, entity_id: str) -> UserEntity | None:
        """Return the user with the given identifier or None."""
        model = await self._session.get(UserModel, entity_id)
        if model is None:
            return None
        return self._to_entity(model)

    async def find_by_email(self, email: str) -> UserEntity | None:
        """Return the user with the given email or None."""
        statement = select(UserModel).where(UserModel.email == email)
        result = await self._session.execute(statement)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def save(self, entity: UserEntity) -> UserEntity:
        """Persist the user and return the saved entity."""
        model = await self._session.get(UserModel, entity.id)
        if model is None:
            model = UserModel(
                id=entity.id,
                email=entity.email,
                hashed_password=entity.hashed_password,
                role=entity.role,
            )
            self._session.add(model)
        else:
            model.email = entity.email
            model.hashed_password = entity.hashed_password
            model.role = entity.role
        await self._session.flush()
        return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> UserEntity:
        """Map an ORM row to a domain entity."""
        return UserEntity(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            role=model.role,
        )
