"""Add email verification fields to users.

Revision ID: 20260608_0006
Revises: 20260608_0005
Create Date: 2026-06-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260608_0006"
down_revision: Union[str, None] = "20260608_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add verification columns; existing users are treated as verified."""
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.add_column("users", sa.Column("email_verify_token", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("email_verify_expires_at", sa.DateTime(), nullable=True))
    op.create_index("ix_users_email_verify_token", "users", ["email_verify_token"], unique=True)


def downgrade() -> None:
    """Remove email verification columns."""
    op.drop_index("ix_users_email_verify_token", table_name="users")
    op.drop_column("users", "email_verify_expires_at")
    op.drop_column("users", "email_verify_token")
    op.drop_column("users", "email_verified")
