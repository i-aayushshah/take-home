"""Auth HTTP routes."""

from fastapi import APIRouter, Depends

from app.api.v1.auth.application.auth_service import AuthService
from app.api.v1.auth.presentation.dependencies import get_auth_service
from app.api.v1.auth.presentation.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.shared.rate_limiter import RateLimiter

_login_limiter = RateLimiter(max_requests=10, window_seconds=60)
_register_limiter = RateLimiter(max_requests=5, window_seconds=60)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, dependencies=[Depends(_register_limiter)])
async def register(body: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Register a new reviewer account and return an access token."""
    token = await auth_service.register(body.email, body.password)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(_login_limiter)])
async def login(body: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Authenticate a user and return an access token."""
    token = await auth_service.login(body.email, body.password)
    return TokenResponse(access_token=token)
