"""Candidate presentation-layer dependency factories."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.application.ai_service import AiService, build_summary_strategy
from app.api.v1.candidates.application.candidate_service import CandidateService
from app.api.v1.candidates.application.score_service import ScoreService
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.config import Settings, get_settings
from app.database import get_session


async def get_candidate_uow(session: AsyncSession = Depends(get_session)) -> CandidateUnitOfWork:
    """Yield a candidate unit of work bound to the request session."""
    return CandidateUnitOfWork(session)


def get_candidate_service(uow: CandidateUnitOfWork = Depends(get_candidate_uow)) -> CandidateService:
    """Return a candidate service wired with its unit of work."""
    return CandidateService(uow)


def get_score_service(uow: CandidateUnitOfWork = Depends(get_candidate_uow)) -> ScoreService:
    """Return a score service wired with its unit of work."""
    return ScoreService(uow)


def get_ai_service(
    uow: CandidateUnitOfWork = Depends(get_candidate_uow),
    settings: Settings = Depends(get_settings),
) -> AiService:
    """Return an AI summary service with the configured strategy."""
    strategy = build_summary_strategy(settings)
    return AiService(uow, strategy)
