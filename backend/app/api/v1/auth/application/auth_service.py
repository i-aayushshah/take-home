"""Authentication use-case services."""

import secrets
import uuid
from dataclasses import dataclass
from datetime import timedelta
from urllib.parse import quote

from app.api.v1.auth.application.password_service import PasswordService
from app.api.v1.auth.domain.enums import Role
from app.api.v1.auth.domain.exceptions import (
    EmailNotVerifiedError,
    InvalidCredentialsError,
    InvalidVerificationTokenError,
    UserAlreadyExistsError,
)
from app.api.v1.auth.domain.user import UserEntity
from app.api.v1.auth.infrastructure.jwt import JwtService
from app.api.v1.auth.infrastructure.unit_of_work import AuthUnitOfWork
from app.config import Settings
from app.shared.email_service import EmailService
from app.shared.time import utc_now

VERIFY_TOKEN_TTL = timedelta(hours=24)


@dataclass(frozen=True)
class RegisterResult:
    """Outcome of a reviewer registration attempt."""

    message: str
    requires_verification: bool
    access_token: str | None = None


class AuthService:
    """Orchestrates user registration and login."""

    def __init__(
        self,
        uow: AuthUnitOfWork,
        password_service: PasswordService,
        jwt_service: JwtService,
        settings: Settings,
        email_service: EmailService | None = None,
    ) -> None:
        self._uow = uow
        self._password_service = password_service
        self._jwt_service = jwt_service
        self._settings = settings
        self._email = email_service

    def _verification_required(self) -> bool:
        """Return True when new accounts must verify email before login."""
        return self._settings.email_enabled and bool(self._settings.smtp_host)

    def _public_app_url(self) -> str:
        """Base URL for links in verification emails."""
        configured = (self._settings.public_app_url or "").strip()
        if configured:
            return configured.rstrip("/")
        origins = self._settings.cors_origin_list
        return origins[0].rstrip("/") if origins else "http://localhost:5173"

    async def register(self, email: str, password: str) -> RegisterResult:
        """Register a new reviewer and optionally require email verification."""
        existing = await self._uow.users.find_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError(f"User already exists: {email}")

        require_verify = self._verification_required()
        verify_token = secrets.token_urlsafe(32) if require_verify else None
        verify_expires = utc_now() + VERIFY_TOKEN_TTL if require_verify else None

        user = UserEntity(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=self._password_service.hash_password(password),
            role=Role.REVIEWER,
            email_verified=not require_verify,
            email_verify_token=verify_token,
            email_verify_expires_at=verify_expires,
        )
        saved = await self._uow.users.save(user)
        await self._uow.commit()

        if require_verify and self._email and verify_token:
            verify_url = (
                f"{self._public_app_url()}/verify-email"
                f"?token={verify_token}&email={quote(saved.email)}"
            )
            await self._email.send_verification_email(saved.email, verify_url)
            return RegisterResult(
                message="Account created. Check your email to verify before signing in.",
                requires_verification=True,
            )

        token = self._jwt_service.create_access_token(saved.id, saved.role)
        return RegisterResult(
            message="Account created.",
            requires_verification=False,
            access_token=token,
        )

    async def login(self, email: str, password: str) -> str:
        """Authenticate a user and return an access token."""
        user = await self._uow.users.find_by_email(email)
        if user is None or not self._password_service.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")
        if not user.email_verified:
            raise EmailNotVerifiedError(
                "Please verify your email before signing in. Check your inbox or request a new link."
            )
        return self._jwt_service.create_access_token(user.id, user.role)

    async def verify_email(self, token: str) -> str:
        """Mark a user's email verified and return an access token."""
        user = await self._uow.users.find_by_verify_token(token)
        if user is None:
            raise InvalidVerificationTokenError("Invalid or expired verification link.")

        now = utc_now()
        expires = user.email_verify_expires_at
        if expires is not None and expires < now:
            raise InvalidVerificationTokenError("Verification link has expired. Request a new one.")

        verified = UserEntity(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            email_verified=True,
            email_verify_token=None,
            email_verify_expires_at=None,
        )
        await self._uow.users.save(verified)
        await self._uow.commit()
        return self._jwt_service.create_access_token(verified.id, verified.role)

    async def resend_verification(self, email: str) -> str:
        """Issue a fresh verification email for an unverified account."""
        user = await self._uow.users.find_by_email(email)
        if user is None or user.email_verified:
            return "If an unverified account exists for this email, a new link has been sent."

        verify_token = secrets.token_urlsafe(32)
        updated = UserEntity(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            role=user.role,
            email_verified=False,
            email_verify_token=verify_token,
            email_verify_expires_at=utc_now() + VERIFY_TOKEN_TTL,
        )
        await self._uow.users.save(updated)
        await self._uow.commit()

        if self._email:
            verify_url = (
                f"{self._public_app_url()}/verify-email"
                f"?token={verify_token}&email={quote(updated.email)}"
            )
            await self._email.send_verification_email(updated.email, verify_url)

        return "If an unverified account exists for this email, a new link has been sent."

    async def list_team_members(self) -> list[UserEntity]:
        """Return reviewers and admins for interview assignment."""
        return await self._uow.users.list_team_members()
