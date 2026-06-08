"""Candidate query and mutation use-case services."""

from dataclasses import replace

from app.api.v1.candidates.domain.candidate import CandidateAggregate, CandidateFilters
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.api.v1.candidates.domain.exceptions import CandidateNotFoundError
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.shared.pagination import PaginatedResult, normalize_pagination


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
        """Return candidate detail with role-aware scores and notes.

        Args:
            candidate_id: Candidate identifier.
            viewer_id: Authenticated user identifier.
            is_admin: Whether the viewer has admin privileges.

        Returns:
            Candidate aggregate with filtered scores.

        Raises:
            CandidateNotFoundError: When the candidate does not exist.
        """
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        scores = await self._uow.scores.find_by_candidate_id(candidate_id)
        if not is_admin:
            scores = [score for score in scores if score.reviewer_id == viewer_id]
            return replace(candidate, scores=tuple(scores), internal_notes=None)
        return replace(candidate, scores=tuple(scores))

    async def update_internal_notes(self, candidate_id: str, notes: str | None) -> CandidateAggregate:
        """Update admin-only internal notes for a candidate.

        Raises:
            CandidateNotFoundError: When the candidate does not exist.
        """
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        updated = replace(candidate, internal_notes=notes)
        saved = await self._uow.candidates.save(updated)
        await self._uow.commit()
        return saved

    async def soft_delete_candidate(self, candidate_id: str) -> None:
        """Soft-delete a candidate by setting deleted_at.

        Raises:
            CandidateNotFoundError: When the candidate does not exist.
        """
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        await self._uow.candidates.soft_delete(candidate_id)
        await self._uow.commit()
