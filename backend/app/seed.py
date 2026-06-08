"""Startup seed data for local development and demos."""

import uuid
from app.shared.time import utc_now

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.application.password_service import PasswordService
from app.api.v1.auth.domain.enums import Role
from app.api.v1.auth.domain.user import UserEntity
from app.api.v1.auth.infrastructure.user_repository import UserRepository
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.db.models.candidate import CandidateModel


async def seed_database(session: AsyncSession) -> None:
    """Insert demo users and candidates when the database is empty.

    Args:
        session: Active async database session.
    """
    candidate_count = await session.scalar(select(func.count()).select_from(CandidateModel))
    if candidate_count and candidate_count > 0:
        return
    await _seed_admin_user(session)
    await _seed_candidates(session)
    await session.commit()


async def _seed_admin_user(session: AsyncSession) -> None:
    """Create a default admin account for local testing."""
    repository = UserRepository(session)
    password_service = PasswordService()
    admin = UserEntity(
        id=str(uuid.uuid4()),
        email="admin@techkraft.com",
        hashed_password=password_service.hash_password("admin12345"),
        role=Role.ADMIN,
    )
    await repository.save(admin)


async def _seed_candidates(session: AsyncSession) -> None:
    """Create demo candidates with varied filters for list testing."""
    now = utc_now()
    candidates = [
        CandidateModel(
            id=str(uuid.uuid4()),
            name="Aisha Patel",
            email="aisha.patel@example.com",
            role_applied="Full Stack Engineer",
            status=CandidateStatus.NEW,
            skills=["Python", "React", "PostgreSQL"],
            internal_notes="Strong portfolio.",
            created_at=now,
            deleted_at=None,
        ),
        CandidateModel(
            id=str(uuid.uuid4()),
            name="Marcus Chen",
            email="marcus.chen@example.com",
            role_applied="Backend Engineer",
            status=CandidateStatus.REVIEWED,
            skills=["FastAPI", "Docker", "Redis"],
            internal_notes=None,
            created_at=now,
            deleted_at=None,
        ),
        CandidateModel(
            id=str(uuid.uuid4()),
            name="Sofia Rivera",
            email="sofia.rivera@example.com",
            role_applied="Frontend Engineer",
            status=CandidateStatus.HIRED,
            skills=["React", "TypeScript", "Tailwind CSS"],
            internal_notes="Offer accepted.",
            created_at=now,
            deleted_at=None,
        ),
        CandidateModel(
            id=str(uuid.uuid4()),
            name="James Okafor",
            email="james.okafor@example.com",
            role_applied="DevOps Engineer",
            status=CandidateStatus.REJECTED,
            skills=["Kubernetes", "AWS", "Terraform"],
            internal_notes="Not a culture fit.",
            created_at=now,
            deleted_at=None,
        ),
        CandidateModel(
            id=str(uuid.uuid4()),
            name="Emily Zhang",
            email="emily.zhang@example.com",
            role_applied="Full Stack Engineer",
            status=CandidateStatus.NEW,
            skills=["Python", "Vue", "GraphQL"],
            internal_notes=None,
            created_at=now,
            deleted_at=None,
        ),
    ]
    session.add_all(candidates)


async def run_seed() -> None:
    """Run database seeding as a standalone CLI task."""
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from app.config import get_settings
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await seed_database(session)
    await engine.dispose()


def main() -> None:
    """Entry point for manual seed execution."""
    import asyncio
    asyncio.run(run_seed())
    print("Seed complete (skipped if candidates already exist).")


if __name__ == "__main__":
    main()
