"""Auth domain user entity."""

from dataclasses import dataclass

from app.api.v1.auth.domain.enums import Role


@dataclass(frozen=True)
class UserEntity:
    """Domain representation of an authenticated user."""

    id: str
    email: str
    hashed_password: str
    role: Role
