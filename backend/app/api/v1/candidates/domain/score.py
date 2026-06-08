"""Score domain entity."""

from dataclasses import dataclass
from datetime import datetime

from app.api.v1.candidates.domain.exceptions import InvalidScoreError


@dataclass(frozen=True)
class ScoreEntity:
    """Domain representation of a reviewer score."""

    id: str
    candidate_id: str
    category: str
    score: int
    reviewer_id: str
    note: str | None
    created_at: datetime


def create_score_entity(
    score_id: str,
    candidate_id: str,
    category: str,
    score: int,
    reviewer_id: str,
    note: str | None,
    created_at: datetime,
) -> ScoreEntity:
    """Create a score entity after validating invariants.

    Args:
        score_id: Unique score identifier.
        candidate_id: Associated candidate identifier.
        category: Score category label.
        score: Numeric score between 1 and 5.
        reviewer_id: Reviewer who submitted the score.
        note: Optional reviewer note.
        created_at: Creation timestamp.

    Returns:
        A validated score entity.

    Raises:
        InvalidScoreError: When the score is outside the allowed range.
    """
    if score < 1 or score > 5:
        raise InvalidScoreError("Score must be between 1 and 5")
    return ScoreEntity(
        id=score_id,
        candidate_id=candidate_id,
        category=category,
        score=score,
        reviewer_id=reviewer_id,
        note=note,
        created_at=created_at,
    )
