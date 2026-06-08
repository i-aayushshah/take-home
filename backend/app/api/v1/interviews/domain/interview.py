"""Interview domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InterviewEntity:
    """Scheduled interview between a candidate and reviewer."""

    id: str
    candidate_id: str
    reviewer_id: str
    scheduled_at: datetime
    interview_type: str
    location_or_link: str | None
    notes: str | None
    created_at: datetime
