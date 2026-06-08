"""JWT encoding, decoding, and current-user dependency."""

from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.domain.enums import Role
from app.api.v1.auth.domain.user import UserEntity
from app.api.v1.auth.infrastructure.unit_of_work import AuthUnitOfWork
from app.config import Settings, get_settings
from app.database import get_session

_bearer_scheme = HTTPBearer(auto_error=False)


class JwtService:
    """Encodes and decodes JWT access tokens."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_access_token(self, user_id: str, role: Role) -> str:
        """Return a signed JWT for the given user identifier and role."""
        expire_at = datetime.now(UTC) + timedelta(minutes=self._settings.access_token_expire_minutes)
        payload = {"sub": user_id, "role": role.value, "exp": expire_at}
        return jwt.encode(payload, self._settings.secret_key, algorithm=self._settings.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT, returning its payload."""
        return jwt.decode(token, self._settings.secret_key, algorithms=[self._settings.algorithm])


async def get_auth_uow(session: AsyncSession = Depends(get_session)) -> AuthUnitOfWork:
    """Yield an auth unit of work bound to the request session."""
    return AuthUnitOfWork(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    uow: AuthUnitOfWork = Depends(get_auth_uow),
    settings: Settings = Depends(get_settings),
) -> UserEntity:
    """Resolve and return the authenticated user from the Authorization header.

    Raises:
        HTTPException: 401 when the token is missing, invalid, or stale.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = JwtService(settings).decode_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    user = await uow.users.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(current_user: UserEntity = Depends(get_current_user)) -> UserEntity:
    """Restrict a route to admin users only.

    Raises:
        HTTPException: 403 when the caller is not an admin.
    """
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user
