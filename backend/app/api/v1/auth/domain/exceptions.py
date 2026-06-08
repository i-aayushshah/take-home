"""Auth domain exceptions."""

from app.shared.exceptions import DomainError


class InvalidCredentialsError(DomainError):
    """Raised when login credentials do not match a stored user."""


class UserAlreadyExistsError(DomainError):
    """Raised when registration is attempted for an existing email."""
