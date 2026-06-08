"""Candidate presentation-layer dependency factories."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.application.ai_service import AiService, build_summary_strategy
from app.api.v1.candidates.application.audit_service import AuditService
from app.api.v1.candidates.application.candidate_service import CandidateService
from app.api.v1.candidates.application.resume_service import ResumeService
from app.api.v1.candidates.application.score_service import ScoreService
from app.api.v1.candidates.infrastructure.resume_parse_strategy import build_resume_parse_strategy
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.config import Settings, get_settings
from app.database import get_session
from app.shared.email_service import EmailService


async def get_candidate_uow(session: AsyncSession = Depends(get_session)) -> CandidateUnitOfWork:
    """Yield a candidate unit of work bound to the request session."""
    return CandidateUnitOfWork(session)


def get_email_service(settings: Settings = Depends(get_settings)) -> EmailService:
    """Return the email notification service."""
    return EmailService(settings)


def get_candidate_service(
    uow: CandidateUnitOfWork = Depends(get_candidate_uow),
    email_service: EmailService = Depends(get_email_service),
) -> CandidateService:
    """Return a candidate service wired with its unit of work."""
    return CandidateService(uow, email_service=email_service)


def get_audit_service(uow: CandidateUnitOfWork = Depends(get_candidate_uow)) -> AuditService:
    """Return an audit service."""
    return AuditService(uow.audit)


def get_score_service(
    uow: CandidateUnitOfWork = Depends(get_candidate_uow),
    candidate_service: CandidateService = Depends(get_candidate_service),
) -> ScoreService:
    """Return a score service wired with its unit of work."""
    return ScoreService(uow, candidate_service)


def get_resume_service(settings: Settings = Depends(get_settings)) -> ResumeService:
    """Return a resume storage service."""
    return ResumeService(settings)


def get_ai_service(
    uow: CandidateUnitOfWork = Depends(get_candidate_uow),
    settings: Settings = Depends(get_settings),
    resume_service: ResumeService = Depends(get_resume_service),
) -> AiService:
    """Return an AI summary service with the configured strategy."""
    strategy = build_summary_strategy(settings)
    parse_strategy = build_resume_parse_strategy(settings)
    return AiService(uow, strategy, resume_parse_strategy=parse_strategy, resume_service=resume_service)
