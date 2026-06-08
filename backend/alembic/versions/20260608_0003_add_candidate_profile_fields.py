"""Add description and work_experience to candidates.

Revision ID: 20260608_0003
Revises: 20260608_0002
Create Date: 2026-06-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260608_0003"
down_revision: Union[str, None] = "20260608_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add nullable profile fields for candidate bio and work history."""
    op.add_column("candidates", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("candidates", sa.Column("work_experience", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove profile fields."""
    op.drop_column("candidates", "work_experience")
    op.drop_column("candidates", "description")
