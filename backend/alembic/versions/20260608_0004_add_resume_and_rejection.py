"""Add resume and rejection reason fields to candidates.

Revision ID: 20260608_0004
Revises: 20260608_0003
Create Date: 2026-06-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260608_0004"
down_revision: Union[str, None] = "20260608_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add resume filename and rejection reason columns."""
    op.add_column("candidates", sa.Column("resume_filename", sa.String(length=255), nullable=True))
    op.add_column("candidates", sa.Column("rejection_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove resume and rejection columns."""
    op.drop_column("candidates", "rejection_reason")
    op.drop_column("candidates", "resume_filename")
