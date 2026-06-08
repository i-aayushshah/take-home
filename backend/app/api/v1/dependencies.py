"""Cross-cutting API v1 dependencies composed from feature slices."""

from app.api.v1.auth.infrastructure.jwt import get_current_user, require_admin

__all__ = ["get_current_user", "require_admin"]
