"""Audit logging for candidate mutations."""

from app.api.v1.candidates.domain.audit import AuditEventEntity
from app.api.v1.candidates.infrastructure.audit_repository import AuditRepository


class AuditService:
    """Records append-only audit events."""

    def __init__(self, repository: AuditRepository) -> None:
        self._repository = repository

    async def log(
        self,
        *,
        actor_id: str | None,
        candidate_id: str,
        action: str,
        payload: dict | None = None,
    ) -> AuditEventEntity:
        """Append an audit event for a candidate action."""
        return await self._repository.append(
            actor_id=actor_id,
            candidate_id=candidate_id,
            action=action,
            payload=payload,
        )

    async def list_for_candidate(self, candidate_id: str, limit: int = 50) -> list[AuditEventEntity]:
        """Return recent audit events for a candidate."""
        return await self._repository.list_by_candidate(candidate_id, limit=limit)
