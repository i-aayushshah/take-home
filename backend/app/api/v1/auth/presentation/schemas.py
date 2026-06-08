"""Auth request and response schemas."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Payload for user registration."""

    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    """Payload for user login."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    """Registration outcome — may require email verification before login."""

    message: str
    requires_verification: bool = False
    access_token: str | None = None
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic success message."""

    message: str


class ResendVerificationRequest(BaseModel):
    """Payload to resend an email verification link."""

    email: EmailStr


class TeamMemberResponse(BaseModel):
    """Reviewer or admin available for interview assignment."""

    id: str
    email: str
    role: str


class TeamListResponse(BaseModel):
    """List of team members."""

    items: list[TeamMemberResponse]
