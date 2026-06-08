"""Shared pagination dataclass and query helpers."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PaginationParams:
    """Offset-based pagination constraints for list queries."""

    offset: int = 0
    limit: int = 20


@dataclass(frozen=True)
class PaginatedResult:
    """Paginated list response wrapper."""

    items: list
    total: int
    offset: int
    limit: int


def normalize_pagination(offset: int, limit: int, max_limit: int = 50) -> PaginationParams:
    """Clamp offset and limit to valid bounds.

    Args:
        offset: Requested row offset.
        limit: Requested page size.
        max_limit: Maximum allowed page size.

    Returns:
        Normalized pagination parameters.
    """
    safe_offset = max(offset, 0)
    safe_limit = min(max(limit, 1), max_limit)
    return PaginationParams(offset=safe_offset, limit=safe_limit)
