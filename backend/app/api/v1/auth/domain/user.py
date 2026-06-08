"""Auth domain user entity."""

from dataclasses import dataclass
from datetime import datetime

from app.api.v1.auth.domain.enums import Role


@dataclass(frozen=True)
class UserEntity:
    """Domain representation of an authenticated user."""

    id: str
    email: str
    hashed_password: str
    role: Role
    email_verified: bool = True
    email_verify_token: str | None = None
    email_verify_expires_at: datetime | None = None
