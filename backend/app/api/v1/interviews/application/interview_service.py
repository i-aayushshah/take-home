"""Interview scheduling use cases."""

import uuid
from dataclasses import replace
from datetime import datetime

from app.api.v1.candidates.domain.exceptions import CandidateNotFoundError
from app.api.v1.candidates.infrastructure.unit_of_work import CandidateUnitOfWork
from app.api.v1.interviews.domain.interview import InterviewEntity
from app.shared.email_service import EmailService
from app.shared.time import utc_now

ALLOWED_TYPES = {"video", "in_person", "phone"}


class InterviewService:
    """Schedules and manages candidate interviews."""

    def __init__(self, uow: CandidateUnitOfWork, email_service: EmailService | None = None) -> None:
        self._uow = uow
        self._email = email_service

    async def schedule_interview(
        self,
        *,
        candidate_id: str,
        reviewer_id: str,
        scheduled_at: datetime,
        interview_type: str,
        location_or_link: str | None,
        notes: str | None,
        actor_id: str,
    ) -> InterviewEntity:
        """Create a new interview for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")

        normalized_type = interview_type.strip().lower()
        if normalized_type not in ALLOWED_TYPES:
            raise ValueError("Interview type must be video, in_person, or phone.")

        entity = InterviewEntity(
            id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            reviewer_id=reviewer_id,
            scheduled_at=scheduled_at,
            interview_type=normalized_type,
            location_or_link=location_or_link,
            notes=notes,
            created_at=utc_now(),
        )
        saved = await self._uow.interviews.create(entity)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=candidate_id,
            action="interview_scheduled",
            payload={
                "interview_id": saved.id,
                "scheduled_at": saved.scheduled_at.isoformat(),
                "interview_type": saved.interview_type,
            },
        )
        await self._uow.commit()

        if self._email:
            await self._email.send_interview_notification(
                candidate=candidate,
                scheduled_at=saved.scheduled_at,
                interview_type=saved.interview_type,
                location_or_link=saved.location_or_link,
                notes=saved.notes,
            )

        return saved

    async def update_interview(
        self,
        interview_id: str,
        *,
        reviewer_id: str,
        scheduled_at: datetime,
        interview_type: str,
        location_or_link: str | None,
        notes: str | None,
        actor_id: str,
    ) -> InterviewEntity:
        """Update a scheduled interview."""
        interview = await self._uow.interviews.get_by_id(interview_id)
        if interview is None:
            raise CandidateNotFoundError(f"Interview not found: {interview_id}")

        candidate = await self._uow.candidates.get_by_id(interview.candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {interview.candidate_id}")

        normalized_type = interview_type.strip().lower()
        if normalized_type not in ALLOWED_TYPES:
            raise ValueError("Interview type must be video, in_person, or phone.")

        updated = replace(
            interview,
            reviewer_id=reviewer_id,
            scheduled_at=scheduled_at,
            interview_type=normalized_type,
            location_or_link=location_or_link,
            notes=notes,
        )
        saved = await self._uow.interviews.save(updated)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=interview.candidate_id,
            action="interview_updated",
            payload={
                "interview_id": saved.id,
                "scheduled_at": saved.scheduled_at.isoformat(),
                "interview_type": saved.interview_type,
            },
        )
        await self._uow.commit()

        if self._email:
            await self._email.send_interview_notification(
                candidate=candidate,
                scheduled_at=saved.scheduled_at,
                interview_type=saved.interview_type,
                location_or_link=saved.location_or_link,
                notes=saved.notes,
                updated=True,
            )

        return saved

    async def list_for_candidate(self, candidate_id: str) -> list[InterviewEntity]:
        """Return interviews for a candidate."""
        candidate = await self._uow.candidates.get_by_id(candidate_id)
        if candidate is None:
            raise CandidateNotFoundError(f"Candidate not found: {candidate_id}")
        return await self._uow.interviews.list_by_candidate(candidate_id)

    async def list_between(self, start: datetime, end: datetime) -> list[InterviewEntity]:
        """Return interviews in a date range."""
        return await self._uow.interviews.list_between(start, end)

    async def delete_interview(self, interview_id: str, *, actor_id: str) -> None:
        """Remove a scheduled interview."""
        interview = await self._uow.interviews.get_by_id(interview_id)
        if interview is None:
            raise CandidateNotFoundError(f"Interview not found: {interview_id}")
        await self._uow.interviews.delete(interview_id)
        await self._uow.audit.append(
            actor_id=actor_id,
            candidate_id=interview.candidate_id,
            action="interview_cancelled",
            payload={"interview_id": interview_id},
        )
        await self._uow.commit()
