"""Score submission use-case service."""

import uuid
from datetime import UTC, datetime

from app.api.v1.candidates.domain.exceptions import CandidateNotFoundError
from app.api.v1.candidates.domain.score import ScoreEntity, create_score_entity
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork


class ScoreService:
    """Orchestrates score submission for candidates."""

    def __init__(self, uow: CandidateUnitOfWork) -> None:
        self._uow = uow

    async def submit_score(
        self,
        candidate_id: str,
        reviewer_id: str,
        category: str,
        score: int,
        note: str | None,
    ) -> ScoreEntity:
        """Submit a reviewer score for a candidate category.

        Args:
            candidate_id: Target candidate identifier.
            reviewer_id: Authenticated reviewer identifier.
            category: Assessment category name.
            score: Numeric score between 1 and 5.
            note: Optional reviewer note.

        Returns:
            The persisted score entity.

        Raises:
            CandidateNotFoundError: When the candidate does not exist.
        """
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
            created_at=datetime.now(UTC),
        )
        saved = await self._uow.scores.save(entity)
        await self._uow.commit()
        return saved
