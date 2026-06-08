"""Audit event domain entity."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuditEventEntity:
    """Immutable record of a candidate-related action."""

    id: str
    actor_id: str | None
    candidate_id: str
    action: str
    payload: dict
    created_at: datetime
