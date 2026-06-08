"""Candidate query and mutation use-case services."""

import uuid
from dataclasses import replace

from app.api.v1.candidates.domain.candidate import CandidateAggregate, CandidateFilters, WorkExperienceEntry
from app.api.v1.candidates.domain.enums import CandidateStatus
from app.api.v1.candidates.domain.exceptions import (
    CandidateNotFoundError,
    DuplicateCandidateError,
    InvalidStatusError,
)
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.shared.email_service import EmailService
from app.shared.pagination import PaginatedResult, normalize_pagination
from app.shared.time import utc_now


class CandidateService:
    """Orchestrates candidate list, detail, notes, and soft-delete flows."""

    def __init__(self, uow: CandidateUnitOfWork, email_service: EmailService | None = None) -> None:
        self._uow = uow
        self._email = email_service

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
        actor_id: str | None = None,
        source: str = "admin",
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
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=saved.id,
            action="application_submitted" if source == "public" else "candidate_created",
            payload={"email": email, "role_applied": role_applied, "source": source},
        )
        await self._uow.commit()
        return saved

    async def update_status(
        self,
        candidate_id: str,
        status: CandidateStatus,
        rejection_reason: str | None,
        *,
        actor_id: str | None = None,
    ) -> CandidateAggregate:
        """Update hiring decision status for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")

        previous_status = candidate.status

        if status == CandidateStatus.REJECTED:
            if not rejection_reason or len(rejection_reason.strip()) < 10:
                raise InvalidStatusError("Rejection requires a reason of at least 10 characters.")
            reason = rejection_reason.strip()
        else:
            reason = None

        updated = replace(candidate, status=status, rejection_reason=reason)
        saved = await self._uow.candidates.save(updated)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=candidate_id,
            action="status_changed",
            payload={"from": previous_status.value, "to": status.value},
        )
        await self._uow.commit()

        if self._email and previous_status != status:
            await self._email.send_status_notification(saved, status)

        return saved

    async def attach_resume(
        self,
        candidate_id: str,
        filename: str,
        *,
        actor_id: str | None = None,
    ) -> CandidateAggregate:
        """Persist resume filename metadata for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        updated = replace(candidate, resume_filename=filename)
        saved = await self._uow.candidates.save(updated)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=candidate_id,
            action="resume_uploaded",
            payload={"filename": filename},
        )
        await self._uow.commit()
        return saved

    async def mark_reviewed_if_new(self, candidate_id: str) -> None:
        """Promote a new application to reviewed after the first score."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None or candidate.status != CandidateStatus.NEW:
            return
        updated = replace(candidate, status=CandidateStatus.REVIEWED)
        saved = await self._uow.candidates.save(updated)
        await self._uow.audit.append(
            actor_id=None,
            candidate_id=candidate_id,
            action="status_changed",
            payload={"from": CandidateStatus.NEW.value, "to": CandidateStatus.REVIEWED.value, "auto": True},
        )
        await self._uow.commit()
        if self._email:
            await self._email.send_status_notification(saved, CandidateStatus.REVIEWED)

    async def update_internal_notes(
        self,
        candidate_id: str,
        notes: str | None,
        *,
        actor_id: str | None = None,
    ) -> CandidateAggregate:
        """Update admin-only internal notes for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        updated = replace(candidate, internal_notes=notes)
        saved = await self._uow.candidates.save(updated)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=candidate_id,
            action="notes_updated",
            payload={"has_notes": bool(notes and notes.strip())},
        )
        await self._uow.commit()
        return saved

    async def update_profile(
        self,
        candidate_id: str,
        *,
        skills: list[str],
        description: str | None,
        work_experience: tuple[WorkExperienceEntry, ...],
        actor_id: str | None = None,
    ) -> CandidateAggregate:
        """Update candidate profile fields (skills, description, work history)."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        updated = replace(
            candidate,
            skills=skills,
            description=description,
            work_experience=work_experience,
        )
        saved = await self._uow.candidates.save(updated)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=candidate_id,
            action="profile_updated",
            payload={"skills_count": len(skills), "experience_count": len(work_experience)},
        )
        await self._uow.commit()
        return saved

    async def soft_delete_candidate(self, candidate_id: str, *, actor_id: str | None = None) -> None:
        """Soft-delete a candidate by setting deleted_at."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        await self._uow.candidates.soft_delete(candidate_id)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=candidate_id,
            action="soft_deleted",
            payload={},
        )
        await self._uow.commit()
