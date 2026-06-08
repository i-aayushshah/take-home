"""ORM model registry."""

from app.db.models.candidate import CandidateModel
from app.db.models.score import ScoreModel
from app.db.models.user import UserModel

__all__ = ["CandidateModel", "ScoreModel", "UserModel"]
