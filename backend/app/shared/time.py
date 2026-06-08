"""Shared datetime helpers."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current UTC time as a naive datetime for PostgreSQL TIMESTAMP columns."""
    return datetime.now(UTC).replace(tzinfo=None)
