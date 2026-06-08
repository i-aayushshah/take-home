"""Add ai_summary column to candidates.

Revision ID: 20260608_0002
Revises: 20260608_0001
Create Date: 2026-06-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260608_0002"
down_revision: Union[str, None] = "20260608_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add nullable ai_summary text column."""
    op.add_column("candidates", sa.Column("ai_summary", sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove ai_summary column."""
    op.drop_column("candidates", "ai_summary")
