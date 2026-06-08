"""Score submission use-case service."""

import uuid

from app.shared.time import utc_now

from app.api.v1.candidates.application.candidate_service import CandidateService
from app.api.v1.candidates.domain.exceptions import CandidateNotFoundError
from app.api.v1.candidates.domain.score import ScoreEntity, create_score_entity
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.api.v1.candidates.presentation.schemas import to_score_response
from app.shared.sse import score_event_bus


class ScoreService:
    """Orchestrates score submission for candidates."""

    def __init__(self, uow: CandidateUnitOfWork, candidate_service: CandidateService) -> None:
        self._uow = uow
        self._candidate_service = candidate_service

    async def submit_score(
        self,
        candidate_id: str,
        reviewer_id: str,
        category: str,
        score: int,
        note: str | None,
    ) -> ScoreEntity:
        """Submit a reviewer score for a candidate category."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        entity = create_score_entity(
            score_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            category=category,
            score=score,
            reviewer_id=reviewer_id,
            note=note,
            created_at=utc_now(),
        )
        saved = await self._uow.scores.save(entity)
        await self._uow.commit()
        await self._candidate_service.mark_reviewed_if_new(candidate_id)
        await score_event_bus.publish(candidate_id, to_score_response(saved).model_dump(mode="json"))
        return saved
