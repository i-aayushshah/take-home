"""SQLAlchemy interview repository."""

import uuid
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.interviews.domain.interview import InterviewEntity
from app.db.models.interview import InterviewModel
from app.shared.time import utc_now


class InterviewRepository:
    """Persists and queries scheduled interviews."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, entity: InterviewEntity) -> InterviewEntity:
        """Insert a new interview."""
        model = InterviewModel(
            id=entity.id,
            candidate_id=entity.candidate_id,
            reviewer_id=entity.reviewer_id,
            scheduled_at=entity.scheduled_at,
            interview_type=entity.interview_type,
            location_or_link=entity.location_or_link,
            notes=entity.notes,
            created_at=entity.created_at,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, interview_id: str) -> InterviewEntity | None:
        """Return an interview by id."""
        model = await self._session.get(InterviewModel, interview_id)
        return self._to_entity(model) if model else None

    async def list_by_candidate(self, candidate_id: str) -> list[InterviewEntity]:
        """Return interviews for a candidate ordered by schedule time."""
        statement = (
            select(InterviewModel)
            .where(InterviewModel.candidate_id == candidate_id)
            .order_by(InterviewModel.scheduled_at.asc())
        )
        result = await self._session.execute(statement)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def list_between(self, start: datetime, end: datetime) -> list[InterviewEntity]:
        """Return interviews scheduled within a date range."""
        statement = (
            select(InterviewModel)
            .where(
                and_(
                    InterviewModel.scheduled_at >= start,
                    InterviewModel.scheduled_at <= end,
                )
            )
            .order_by(InterviewModel.scheduled_at.asc())
        )
        result = await self._session.execute(statement)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def save(self, entity: InterviewEntity) -> InterviewEntity:
        """Update an existing interview."""
        model = await self._session.get(InterviewModel, entity.id)
        if model is None:
            raise ValueError(f"Interview not found: {entity.id}")
        model.reviewer_id = entity.reviewer_id
        model.scheduled_at = entity.scheduled_at
        model.interview_type = entity.interview_type
        model.location_or_link = entity.location_or_link
        model.notes = entity.notes
        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, interview_id: str) -> None:
        """Remove an interview record."""
        model = await self._session.get(InterviewModel, interview_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

    def _to_entity(self, model: InterviewModel) -> InterviewEntity:
        """Map ORM row to domain entity."""
        return InterviewEntity(
            id=model.id,
            candidate_id=model.candidate_id,
            reviewer_id=model.reviewer_id,
            scheduled_at=model.scheduled_at,
            interview_type=model.interview_type,
            location_or_link=model.location_or_link,
            notes=model.notes,
            created_at=model.created_at,
        )
