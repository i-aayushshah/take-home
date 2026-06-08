"""Shared pytest fixtures for async API tests."""

from __future__ import annotations

import os
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fakeredis import aioredis as fakeredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ.setdefault("TESTING", "true")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-jwt")
os.environ.setdefault("AI_SUMMARY_FALLBACK_MOCK", "true")

from app.api.v1.auth.application.password_service import PasswordService
from app.api.v1.auth.domain.enums import Role
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.config import get_settings
from app.database import get_session
from app.db.base import Base
from app.db.models import AuditEventModel, CandidateModel, InterviewModel, UserModel  # noqa: F401
from app.main import create_app
from app.shared.redis import get_redis
from app.shared.time import utc_now

get_settings.cache_clear()

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Create an in-memory SQLite database for each test."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest_asyncio.fixture
async def fake_redis() -> AsyncGenerator[fakeredis.FakeRedis, None]:
    """Provide an isolated fakeredis instance per test."""
    client = fakeredis.FakeRedis(decode_responses=True)
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
    fake_redis: fakeredis.FakeRedis,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP client with overridden database and Redis dependencies."""
    application = create_app()

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    async def override_get_redis() -> AsyncGenerator[fakeredis.FakeRedis, None]:
        yield fake_redis

    application.dependency_overrides[get_session] = override_get_session
    application.dependency_overrides[get_redis] = override_get_redis

    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client

    application.dependency_overrides.clear()


@pytest_asyncio.fixture
async def seeded_candidate(session_factory: async_sessionmaker[AsyncSession]) -> str:
    """Insert a demo candidate and return its identifier."""
    candidate_id = str(uuid.uuid4())
    async with session_factory() as session:
        session.add(
            CandidateModel(
                id=candidate_id,
                name="Test Candidate",
                email="candidate@example.com",
                role_applied="Backend Engineer",
                status=CandidateStatus.NEW,
                skills=["Python", "FastAPI"],
                description="Experienced backend engineer.",
                work_experience=[
                    {
                        "company": "Acme Corp",
                        "title": "Engineer",
                        "start": "2022",
                        "end": "Present",
                        "summary": "Built APIs.",
                    }
                ],
                internal_notes="Internal only",
                created_at=utc_now(),
                deleted_at=None,
            )
        )
        await session.commit()
    return candidate_id


@pytest_asyncio.fixture
async def admin_headers(session_factory: async_sessionmaker[AsyncSession], client: AsyncClient) -> dict[str, str]:
    """Create an admin user and return authorization headers."""
    password_service = PasswordService()
    async with session_factory() as session:
        session.add(
            UserModel(
                id=str(uuid.uuid4()),
                email="admin@techkraft.com",
                hashed_password=password_service.hash_password("admin12345"),
                role=Role.ADMIN,
            )
        )
        await session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@techkraft.com", "password": "admin12345"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def register_and_login(client: AsyncClient, email: str, password: str = "password123") -> str:
    """Register a reviewer and return an access token."""
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    """Build bearer authorization headers."""
    return {"Authorization": f"Bearer {token}"}
