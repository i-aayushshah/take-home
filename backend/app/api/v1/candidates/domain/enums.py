"""Candidate domain enumerations."""

from enum import Enum


class CandidateStatus(str, Enum):
    """Lifecycle status for a candidate record."""

    NEW = "new"
    REVIEWED = "reviewed"
    HIRED = "hired"
    REJECTED = "rejected"
