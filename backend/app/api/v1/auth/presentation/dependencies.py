"""Auth presentation-layer dependency factories."""

from fastapi import Depends

from app.api.v1.auth.application.auth_service import AuthService
from app.api.v1.auth.application.password_service import PasswordService
from app.api.v1.auth.infrastructure.jwt import AuthUnitOfWork, JwtService, get_auth_uow
from app.config import Settings, get_settings


def get_jwt_service(settings: Settings = Depends(get_settings)) -> JwtService:
    """Return a JWT service configured from application settings."""
    return JwtService(settings)


def get_password_service() -> PasswordService:
    """Return the password hashing service."""
    return PasswordService()


def get_auth_service(
    uow: AuthUnitOfWork = Depends(get_auth_uow),
    password_service: PasswordService = Depends(get_password_service),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> AuthService:
    """Return an auth service wired with its dependencies."""
    return AuthService(uow, password_service, jwt_service)
