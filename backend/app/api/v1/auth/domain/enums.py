"""Auth domain enumerations."""

from enum import Enum


class Role(str, Enum):
    """User role values for role-based access control."""

    ADMIN = "admin"
    REVIEWER = "reviewer"
