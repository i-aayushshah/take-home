"""Auth API integration tests."""

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.v1.auth.domain.enums import Role
from app.config import get_settings
from app.db.models.user import UserModel
from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_register_always_creates_reviewer_role(
    client: AsyncClient,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Registration ignores any attempt to self-assign admin privileges."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "wannabe-admin@techkraft.com",
            "password": "password123",
            "role": "admin",
        },
    )
    assert response.status_code == 200

    async with session_factory() as session:
        result = await session.execute(
            select(UserModel).where(UserModel.email == "wannabe-admin@techkraft.com")
        )
        user = result.scalar_one()
        assert user.role == Role.REVIEWER

    settings = get_settings()
    payload = jwt.decode(
        response.json()["access_token"],
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    assert payload["role"] == Role.REVIEWER.value


@pytest.mark.asyncio
async def test_login_rate_limit_returns_429(client: AsyncClient, fake_redis) -> None:
    """Login endpoint enforces Redis-backed rate limiting."""
    email = "ratelimit@techkraft.com"
    await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})

    for _ in range(10):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "wrong-password"},
        )
        assert response.status_code == 401

    blocked = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "wrong-password"},
    )
    assert blocked.status_code == 429
