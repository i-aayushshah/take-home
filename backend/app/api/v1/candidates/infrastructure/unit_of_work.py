"""Candidate unit of work coordinating repositories."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.infrastructure.audit_repository import AuditRepository
from app.api.v1.candidates.infrastructure.candidate_repository import CandidateRepository
from app.api.v1.candidates.infrastructure.score_repository import ScoreRepository
from app.api.v1.interviews.infrastructure.interview_repository import InterviewRepository


class CandidateUnitOfWork:
    """Coordinates candidate and score repositories under one session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.candidates = CandidateRepository(session)
        self.scores = ScoreRepository(session)
        self.audit = AuditRepository(session)
        self.interviews = InterviewRepository(session)

    async def commit(self) -> None:
        """Flush and commit the current transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Roll back the current transaction."""
        await self._session.rollback()
