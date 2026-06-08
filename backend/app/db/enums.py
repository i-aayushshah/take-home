"""SQLAlchemy enum helpers for PostgreSQL native enum columns."""

from enum import Enum
from typing import TypeVar

from sqlalchemy import Enum as SAEnum

E = TypeVar("E", bound=Enum)


def pg_enum(enum_class: type[E], name: str) -> SAEnum:
    """Build a PostgreSQL enum column that persists enum values, not names."""
    return SAEnum(
        enum_class,
        name=name,
        values_callable=lambda members: [member.value for member in members],
    )
