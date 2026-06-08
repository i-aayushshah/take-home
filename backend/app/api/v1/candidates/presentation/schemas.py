"""Candidate request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.api.v1.candidates.domain.candidate import CandidateAggregate
from app.api.v1.candidates.domain.score import ScoreEntity


class ScoreResponse(BaseModel):
    """Serialized score entity."""

    id: str
    candidate_id: str
    category: str
    score: int
    reviewer_id: str
    note: str | None
    created_at: datetime


class CandidateListItemResponse(BaseModel):
    """Serialized candidate for list views without internal notes."""

    id: str
    name: str
    email: str
    role_applied: str
    status: str
    skills: list[str]
    created_at: datetime


class WorkExperienceResponse(BaseModel):
    """Serialized work history entry."""

    company: str
    title: str
    start: str
    end: str | None = None
    summary: str | None = None


class CandidateDetailResponse(BaseModel):
    """Serialized candidate detail with scores and optional summary."""

    id: str
    name: str
    email: str
    role_applied: str
    status: str
    skills: list[str]
    description: str | None = None
    work_experience: list[WorkExperienceResponse] = []
    ai_summary: str | None
    internal_notes: str | None = None
    scores: list[ScoreResponse]
    created_at: datetime


class CandidateListResponse(BaseModel):
    """Paginated candidate list response."""

    items: list[CandidateListItemResponse]
    total: int
    offset: int
    limit: int


class ScoreSubmitRequest(BaseModel):
    """Payload for submitting a candidate score."""

    category: str = Field(min_length=1, max_length=100)
    score: int = Field(ge=1, le=5)
    note: str | None = None


class SummaryResponse(BaseModel):
    """AI summary generation response."""

    summary: str


class UpdateNotesRequest(BaseModel):
    """Payload for updating admin internal notes."""

    internal_notes: str | None = None


def to_score_response(entity: ScoreEntity) -> ScoreResponse:
    """Map a score entity to its response schema."""
    return ScoreResponse(
        id=entity.id,
        candidate_id=entity.candidate_id,
        category=entity.category,
        score=entity.score,
        reviewer_id=entity.reviewer_id,
        note=entity.note,
        created_at=entity.created_at,
    )


def to_list_item(entity: CandidateAggregate) -> CandidateListItemResponse:
    """Map a candidate aggregate to a list item response."""
    return CandidateListItemResponse(
        id=entity.id,
        name=entity.name,
        email=entity.email,
        role_applied=entity.role_applied,
        status=entity.status.value,
        skills=entity.skills,
        created_at=entity.created_at,
    )


def to_detail_response(entity: CandidateAggregate) -> CandidateDetailResponse:
    """Map a candidate aggregate to a detail response."""
    return CandidateDetailResponse(
        id=entity.id,
        name=entity.name,
        email=entity.email,
        role_applied=entity.role_applied,
        status=entity.status.value,
        skills=entity.skills,
        description=entity.description,
        work_experience=[
            WorkExperienceResponse(
                company=entry.company,
                title=entry.title,
                start=entry.start,
                end=entry.end,
                summary=entry.summary,
            )
            for entry in entity.work_experience
        ],
        ai_summary=entity.ai_summary,
        internal_notes=entity.internal_notes,
        scores=[to_score_response(score) for score in entity.scores],
        created_at=entity.created_at,
    )
