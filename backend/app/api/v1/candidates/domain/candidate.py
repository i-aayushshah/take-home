"""Candidate domain entities and filter value objects."""

from dataclasses import dataclass
from datetime import datetime

from app.api.v1.candidates.domain.enums import CandidateStatus
from app.api.v1.candidates.domain.score import ScoreEntity


@dataclass(frozen=True)
class CandidateFilters:
    """Filter and pagination constraints for candidate list queries."""

    status: CandidateStatus | None = None
    role_applied: str | None = None
    skill: str | None = None
    keyword: str | None = None
    offset: int = 0
    limit: int = 20


@dataclass(frozen=True)
class WorkExperienceEntry:
    """A single role in a candidate's employment history."""

    company: str
    title: str
    start: str
    end: str | None
    summary: str | None = None


@dataclass(frozen=True)
class CandidateAggregate:
    """Domain representation of a candidate and related data."""

    id: str
    name: str
    email: str
    role_applied: str
    status: CandidateStatus
    skills: list[str]
    description: str | None
    work_experience: tuple[WorkExperienceEntry, ...]
    internal_notes: str | None
    ai_summary: str | None
    resume_filename: str | None
    rejection_reason: str | None
    created_at: datetime
    scores: tuple[ScoreEntity, ...] = ()
