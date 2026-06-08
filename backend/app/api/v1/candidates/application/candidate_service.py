"""Candidate query and mutation use-case services."""

import uuid
from dataclasses import replace

from app.api.v1.candidates.domain.candidate import CandidateAggregate, CandidateFilters
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.api.v1.candidates.domain.exceptions import (
    CandidateNotFoundError,
    DuplicateCandidateError,
    InvalidStatusError,
)
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.shared.pagination import PaginatedResult, normalize_pagination
from app.shared.time import utc_now


class CandidateService:
    """Orchestrates candidate list, detail, notes, and soft-delete flows."""

    def __init__(self, uow: CandidateUnitOfWork) -> None:
        self._uow = uow

    async def list_candidates(
        self,
        status: CandidateStatus | None,
        role_applied: str | None,
        skill: str | None,
        keyword: str | None,
        offset: int,
        limit: int,
    ) -> PaginatedResult:
        """Return a paginated list of candidates matching SQL-level filters."""
        pagination = normalize_pagination(offset, limit)
        filters = CandidateFilters(
            status=status,
            role_applied=role_applied,
            skill=skill,
            keyword=keyword,
            offset=pagination.offset,
            limit=pagination.limit,
        )
        items, total = await self._uow.candidates.list_filtered(filters)
        return PaginatedResult(items=items, total=total, offset=pagination.offset, limit=pagination.limit)

    async def get_candidate(self, candidate_id: str, viewer_id: str, is_admin: bool) -> CandidateAggregate:
        """Return candidate detail with role-aware scores and notes."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        scores = await self._uow.scores.find_by_candidate_id(candidate_id)
        if not is_admin:
            scores = [score for score in scores if score.reviewer_id == viewer_id]
            return replace(
                candidate,
                scores=tuple(scores),
                internal_notes=None,
                rejection_reason=None,
            )
        return replace(candidate, scores=tuple(scores))

    async def create_candidate(
        self,
        *,
        name: str,
        email: str,
        role_applied: str,
        skills: list[str],
        description: str | None = None,
    ) -> CandidateAggregate:
        """Create a new application in the pipeline."""
        existing = await self._uow.candidates.find_by_email(email)
        if existing is not None:
            raise DuplicateCandidateError(f"Candidate already exists: {email}")

        entity = CandidateAggregate(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            role_applied=role_applied,
            status=CandidateStatus.NEW,
            skills=skills,
            description=description,
            work_experience=(),
            internal_notes=None,
            ai_summary=None,
            resume_filename=None,
            rejection_reason=None,
            created_at=utc_now(),
        )
        saved = await self._uow.candidates.create(entity)
        await self._uow.commit()
        return saved

    async def update_status(
        self,
        candidate_id: str,
        status: CandidateStatus,
        rejection_reason: str | None,
    ) -> CandidateAggregate:
        """Update hiring decision status for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")

        if status == CandidateStatus.REJECTED:
            if not rejection_reason or len(rejection_reason.strip()) < 10:
                raise InvalidStatusError("Rejection requires a reason of at least 10 characters.")
            reason = rejection_reason.strip()
        else:
            reason = None

        updated = replace(candidate, status=status, rejection_reason=reason)
        saved = await self._uow.candidates.save(updated)
        await self._uow.commit()
        return saved

    async def attach_resume(self, candidate_id: str, filename: str) -> CandidateAggregate:
        """Persist resume filename metadata for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        updated = replace(candidate, resume_filename=filename)
        saved = await self._uow.candidates.save(updated)
        await self._uow.commit()
        return saved

    async def mark_reviewed_if_new(self, candidate_id: str) -> None:
        """Promote a new application to reviewed after the first score."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None or candidate.status != CandidateStatus.NEW:
            return
        updated = replace(candidate, status=CandidateStatus.REVIEWED)
        await self._uow.candidates.save(updated)
        await self._uow.commit()

    async def update_internal_notes(self, candidate_id: str, notes: str | None) -> CandidateAggregate:
        """Update admin-only internal notes for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        updated = replace(candidate, internal_notes=notes)
        saved = await self._uow.candidates.save(updated)
        await self._uow.commit()
        return saved

    async def soft_delete_candidate(self, candidate_id: str) -> None:
        """Soft-delete a candidate by setting deleted_at."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        await self._uow.candidates.soft_delete(candidate_id)
        await self._uow.commit()
