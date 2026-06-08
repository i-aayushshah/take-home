"""Candidate domain exceptions."""

from app.shared.exceptions import DomainError


class CandidateNotFoundError(DomainError):
    """Raised when a candidate record cannot be found."""


class InvalidScoreError(DomainError):
    """Raised when a score value violates domain constraints."""


class AISummaryError(DomainError):
    """Raised when AI summary generation fails."""


class InvalidStatusError(DomainError):
    """Raised when a hiring status update violates business rules."""


class DuplicateCandidateError(DomainError):
    """Raised when creating a candidate with an existing email."""
