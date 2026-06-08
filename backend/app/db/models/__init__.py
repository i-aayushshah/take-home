"""ORM model registry."""

from app.db.models.audit_event import AuditEventModel
from app.db.models.candidate import CandidateModel
from app.db.models.interview import InterviewModel
from app.db.models.score import ScoreModel
from app.db.models.user import UserModel

__all__ = ["AuditEventModel", "CandidateModel", "InterviewModel", "ScoreModel", "UserModel"]
