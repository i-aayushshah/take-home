"""Auth HTTP routes."""

from fastapi import APIRouter, Depends, Query

from app.api.v1.auth.application.auth_service import AuthService
from app.api.v1.auth.presentation.dependencies import get_auth_service
from app.api.v1.auth.presentation.schemas import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    TeamListResponse,
    TeamMemberResponse,
    TokenResponse,
)
from app.api.v1.dependencies import require_admin
from app.shared.rate_limiter import RateLimiter

_login_limiter = RateLimiter(max_requests=10, window_seconds=60)
_register_limiter = RateLimiter(max_requests=5, window_seconds=60)
_verify_limiter = RateLimiter(max_requests=10, window_seconds=60)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, dependencies=[Depends(_register_limiter)])
async def register(body: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> RegisterResponse:
    """Register a new reviewer account; may require email verification when SMTP is enabled."""
    result = await auth_service.register(body.email, body.password)
    return RegisterResponse(
        message=result.message,
        requires_verification=result.requires_verification,
        access_token=result.access_token,
    )


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(_login_limiter)])
async def login(body: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Authenticate a user and return an access token."""
    token = await auth_service.login(body.email, body.password)
    return TokenResponse(access_token=token)


@router.get("/verify-email", response_model=TokenResponse, dependencies=[Depends(_verify_limiter)])
async def verify_email(
    token: str = Query(..., min_length=16),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Confirm a reviewer's email address and return an access token."""
    access_token = await auth_service.verify_email(token)
    return TokenResponse(access_token=access_token)


@router.post("/resend-verification", response_model=MessageResponse, dependencies=[Depends(_verify_limiter)])
async def resend_verification(
    body: ResendVerificationRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Resend the verification email for an unverified reviewer account."""
    message = await auth_service.resend_verification(body.email)
    return MessageResponse(message=message)


@router.get("/team", response_model=TeamListResponse)
async def list_team(
    _: object = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> TeamListResponse:
    """List reviewers and admins for interview scheduling (admin only)."""
    members = await auth_service.list_team_members()
    return TeamListResponse(
        items=[
            TeamMemberResponse(id=member.id, email=member.email, role=member.role.value)
            for member in members
        ]
    )
