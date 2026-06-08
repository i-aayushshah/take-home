"""Authentication use-case services."""

import uuid

from app.api.v1.auth.application.password_service import PasswordService
from app.api.v1.auth.domain.enums import Role
from app.api.v1.auth.domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.api.v1.auth.domain.user import UserEntity
from app.api.v1.auth.infrastructure.jwt import JwtService
from app.api.v1.auth.infrastructure.unit_of_work import AuthUnitOfWork


class AuthService:
    """Orchestrates user registration and login."""

    def __init__(
        self,
        uow: AuthUnitOfWork,
        password_service: PasswordService,
        jwt_service: JwtService,
    ) -> None:
        self._uow = uow
        self._password_service = password_service
        self._jwt_service = jwt_service

    async def register(self, email: str, password: str) -> str:
        """Register a new reviewer and return an access token.

        Args:
            email: Unique user email address.
            password: Plain-text password to hash and store.

        Returns:
            A signed JWT access token.

        Raises:
            UserAlreadyExistsError: When the email is already registered.
        """
        existing = await self._uow.users.find_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError(f"User already exists: {email}")
        user = UserEntity(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=self._password_service.hash_password(password),
            role=Role.REVIEWER,
        )
        saved = await self._uow.users.save(user)
        await self._uow.commit()
        return self._jwt_service.create_access_token(saved.id, saved.role)

    async def login(self, email: str, password: str) -> str:
        """Authenticate a user and return an access token.

        Args:
            email: Registered user email.
            password: Plain-text password to verify.

        Returns:
            A signed JWT access token.

        Raises:
            InvalidCredentialsError: When credentials are invalid.
        """
        user = await self._uow.users.find_by_email(email)
        if user is None or not self._password_service.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")
        return self._jwt_service.create_access_token(user.id, user.role)
