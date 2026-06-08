"""SQLAlchemy audit event repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.candidates.domain.audit import AuditEventEntity
from app.db.models.audit_event import AuditEventModel
from app.shared.time import utc_now


class AuditRepository:
    """Persists append-only audit events."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(
        self,
        *,
        actor_id: str | None,
        candidate_id: str,
        action: str,
        payload: dict | None = None,
    ) -> AuditEventEntity:
        """Insert a new audit event."""
        model = AuditEventModel(
            id=str(uuid.uuid4()),
            actor_id=actor_id,
            candidate_id=candidate_id,
            action=action,
            payload=payload or {},
            created_at=utc_now(),
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def list_by_candidate(self, candidate_id: str, limit: int = 50) -> list[AuditEventEntity]:
        """Return recent audit events for a candidate."""
        statement = (
            select(AuditEventModel)
            .where(AuditEventModel.candidate_id == candidate_id)
            .order_by(AuditEventModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [self._to_entity(model) for model in result.scalars().all()]

    def _to_entity(self, model: AuditEventModel) -> AuditEventEntity:
        """Map ORM row to domain entity."""
        return AuditEventEntity(
            id=model.id,
            actor_id=model.actor_id,
            candidate_id=model.candidate_id,
            action=model.action,
            payload=dict(model.payload or {}),
            created_at=model.created_at,
        )
