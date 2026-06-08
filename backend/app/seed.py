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

DEMO_PROFILES: dict[str, dict] = {
    "aisha.patel@example.com": {
        "description": (
            "Full-stack engineer with 5 years building scalable web applications. "
            "Passionate about clean architecture, developer experience, and mentoring junior engineers. "
            "Looking for a product-focused team where she can own features end-to-end."
        ),
        "work_experience": [
            {
                "company": "NovaStack Labs",
                "title": "Senior Full Stack Engineer",
                "start": "Mar 2022",
                "end": "Present",
                "summary": "Led migration from monolith to microservices; built React dashboards and FastAPI services serving 200k users.",
            },
            {
                "company": "BrightPath Digital",
                "title": "Software Engineer",
                "start": "Jun 2019",
                "end": "Feb 2022",
                "summary": "Developed customer portals with React and Django REST; introduced CI/CD pipelines reducing deploy time by 60%.",
            },
        ],
    },
    "marcus.chen@example.com": {
        "description": (
            "Backend specialist focused on high-throughput APIs and distributed systems. "
            "Experienced with async Python, event-driven architectures, and observability. "
            "Seeks a backend-heavy role with ownership of core platform services."
        ),
        "work_experience": [
            {
                "company": "CloudRelay Inc.",
                "title": "Backend Engineer",
                "start": "Jan 2021",
                "end": "Present",
                "summary": "Designed FastAPI services handling 10k req/s; integrated Redis caching and rate limiting across 12 microservices.",
            },
            {
                "company": "DataForge",
                "title": "Junior Backend Developer",
                "start": "Aug 2018",
                "end": "Dec 2020",
                "summary": "Built ETL pipelines and REST APIs in Python; maintained PostgreSQL schemas for analytics workloads.",
            },
        ],
    },
    "sofia.rivera@example.com": {
        "description": (
            "Frontend engineer who cares deeply about accessibility, design systems, and performance. "
            "Shipped component libraries used across multiple product teams. "
            "Interested in design-engineering collaboration and modern React patterns."
        ),
        "work_experience": [
            {
                "company": "PixelCraft Studio",
                "title": "Senior Frontend Engineer",
                "start": "Apr 2020",
                "end": "Present",
                "summary": "Built a Tailwind-based design system adopted by 4 squads; improved Core Web Vitals scores by 35%.",
            },
            {
                "company": "WebFlow Agency",
                "title": "Frontend Developer",
                "start": "Jul 2017",
                "end": "Mar 2020",
                "summary": "Delivered responsive SPAs for fintech clients using React, TypeScript, and Storybook.",
            },
        ],
    },
    "james.okafor@example.com": {
        "description": (
            "DevOps engineer with strong AWS and Kubernetes expertise. "
            "Automated infrastructure for teams of 50+ engineers. "
            "Prefers platform engineering roles with focus on reliability and developer self-service."
        ),
        "work_experience": [
            {
                "company": "InfraScale",
                "title": "DevOps Engineer",
                "start": "Sep 2019",
                "end": "Present",
                "summary": "Managed EKS clusters across 3 regions; implemented GitOps with ArgoCD and Terraform modules.",
            },
            {
                "company": "HostBridge",
                "title": "Systems Administrator",
                "start": "May 2016",
                "end": "Aug 2019",
                "summary": "Migrated on-prem workloads to AWS; set up monitoring with Prometheus and Grafana.",
            },
        ],
    },
    "emily.zhang@example.com": {
        "description": (
            "Versatile engineer comfortable across the stack with a recent focus on GraphQL APIs and Vue frontends. "
            "Strong communicator who has led cross-functional discovery sessions. "
            "Excited about greenfield projects and rapid iteration."
        ),
        "work_experience": [
            {
                "company": "LaunchPad Tech",
                "title": "Full Stack Engineer",
                "start": "Feb 2022",
                "end": "Present",
                "summary": "Shipped MVP features weekly using Vue 3 and Python GraphQL; integrated third-party payment providers.",
            },
            {
                "company": "CodeSpring",
                "title": "Software Developer Intern",
                "start": "Jun 2020",
                "end": "Jan 2022",
                "summary": "Contributed to internal tooling and API documentation; converted legacy jQuery pages to Vue components.",
            },
        ],
    },
}


DEMO_USERS: list[tuple[str, str, Role]] = [
    ("admin@techkraft.com", "admin12345", Role.ADMIN),
    ("reviewer1@techkraft.com", "reviewer12345", Role.REVIEWER),
    ("reviewer2@techkraft.com", "reviewer12345", Role.REVIEWER),
]

REJECTION_REASONS: dict[str, str] = {
    "james.okafor@example.com": (
        "Insufficient platform experience for senior DevOps role; team prioritizing candidates "
        "with multi-region Kubernetes ownership."
    ),
}


async def seed_database(session: AsyncSession) -> None:
    """Insert demo users and candidates when the database is empty.

    Args:
        session: Active async database session.
    """
    await _seed_demo_users(session)
    candidate_count = await session.scalar(select(func.count()).select_from(CandidateModel))
    if candidate_count and candidate_count > 0:
        await _backfill_candidate_profiles(session)
        await session.commit()
        return
    await _seed_candidates(session)
    await session.commit()


async def _seed_demo_users(session: AsyncSession) -> None:
    """Ensure demo admin and reviewer accounts exist."""
    repository = UserRepository(session)
    password_service = PasswordService()
    for email, password, role in DEMO_USERS:
        existing = await repository.find_by_email(email)
        if existing is not None:
            continue
        await repository.save(
            UserEntity(
                id=str(uuid.uuid4()),
                email=email,
                hashed_password=password_service.hash_password(password),
                role=role,
            )
        )


async def _seed_candidates(session: AsyncSession) -> None:
    """Create demo candidates with varied filters for list testing."""
    now = utc_now()
    candidates = [
        _build_candidate(
            name="Aisha Patel",
            email="aisha.patel@example.com",
            role_applied="Full Stack Engineer",
            status=CandidateStatus.NEW,
            skills=["Python", "React", "PostgreSQL"],
            internal_notes="Strong portfolio.",
            created_at=now,
        ),
        _build_candidate(
            name="Marcus Chen",
            email="marcus.chen@example.com",
            role_applied="Backend Engineer",
            status=CandidateStatus.REVIEWED,
            skills=["FastAPI", "Docker", "Redis"],
            internal_notes=None,
            created_at=now,
        ),
        _build_candidate(
            name="Sofia Rivera",
            email="sofia.rivera@example.com",
            role_applied="Frontend Engineer",
            status=CandidateStatus.HIRED,
            skills=["React", "TypeScript", "Tailwind CSS"],
            internal_notes="Offer accepted.",
            created_at=now,
        ),
        _build_candidate(
            name="James Okafor",
            email="james.okafor@example.com",
            role_applied="DevOps Engineer",
            status=CandidateStatus.REJECTED,
            skills=["Kubernetes", "AWS", "Terraform"],
            internal_notes="Not a culture fit.",
            created_at=now,
        ),
        _build_candidate(
            name="Emily Zhang",
            email="emily.zhang@example.com",
            role_applied="Full Stack Engineer",
            status=CandidateStatus.NEW,
            skills=["Python", "Vue", "GraphQL"],
            internal_notes=None,
            created_at=now,
        ),
    ]
    session.add_all(candidates)


def _build_candidate(
    *,
    name: str,
    email: str,
    role_applied: str,
    status: CandidateStatus,
    skills: list[str],
    internal_notes: str | None,
    created_at,
) -> CandidateModel:
    """Build a candidate ORM row with demo profile fields."""
    profile = DEMO_PROFILES.get(email, {})
    return CandidateModel(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        role_applied=role_applied,
        status=status,
        skills=skills,
        description=profile.get("description"),
        work_experience=profile.get("work_experience"),
        internal_notes=internal_notes,
        rejection_reason=REJECTION_REASONS.get(email),
        created_at=created_at,
        deleted_at=None,
    )


async def _backfill_candidate_profiles(session: AsyncSession) -> None:
    """Populate description and work experience for existing demo candidates."""
    result = await session.execute(select(CandidateModel))
    for model in result.scalars().all():
        profile = DEMO_PROFILES.get(model.email)
        if profile is None:
            continue
        if model.description is None:
            model.description = profile["description"]
        if model.work_experience is None:
            model.work_experience = profile["work_experience"]
        if model.rejection_reason is None and model.email in REJECTION_REASONS:
            model.rejection_reason = REJECTION_REASONS[model.email]


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
    print("Seed complete (new data inserted or demo profiles backfilled).")


if __name__ == "__main__":
    main()
