"""Interview request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.api.v1.interviews.domain.interview import InterviewEntity


class ScheduleInterviewRequest(BaseModel):
    """Payload for scheduling an interview."""

    reviewer_id: str = Field(min_length=1)
    scheduled_at: datetime
    interview_type: str = Field(min_length=1, max_length=32)
    location_or_link: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class UpdateInterviewRequest(BaseModel):
    """Payload for updating a scheduled interview."""

    reviewer_id: str = Field(min_length=1)
    scheduled_at: datetime
    interview_type: str = Field(min_length=1, max_length=32)
    location_or_link: str | None = Field(default=None, max_length=500)
    notes: str | None = None


class InterviewResponse(BaseModel):
    """Serialized interview."""

    id: str
    candidate_id: str
    reviewer_id: str
    scheduled_at: datetime
    interview_type: str
    location_or_link: str | None
    notes: str | None
    created_at: datetime


class InterviewListResponse(BaseModel):
    """List of interviews."""

    items: list[InterviewResponse]


def to_interview_response(entity: InterviewEntity) -> InterviewResponse:
    """Map interview entity to response schema."""
    return InterviewResponse(
        id=entity.id,
        candidate_id=entity.candidate_id,
        reviewer_id=entity.reviewer_id,
        scheduled_at=entity.scheduled_at,
        interview_type=entity.interview_type,
        location_or_link=entity.location_or_link,
        notes=entity.notes,
        created_at=entity.created_at,
    )
