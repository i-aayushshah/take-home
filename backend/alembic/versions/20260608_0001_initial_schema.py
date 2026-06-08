"""Initial database schema for users, candidates, and scores.

Revision ID: 20260608_0001
Revises:
Create Date: 2026-06-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260608_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = sa.Enum("admin", "reviewer", name="role")
candidate_status_enum = sa.Enum("new", "reviewed", "hired", "rejected", name="candidatestatus")


def upgrade() -> None:
    """Create core tables and indexes."""
    role_enum.create(op.get_bind(), checkfirst=True)
    candidate_status_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", role_enum, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "candidates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role_applied", sa.String(length=100), nullable=False),
        sa.Column("status", candidate_status_enum, nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_candidates_status", "candidates", ["status"], unique=False)
    op.create_index("ix_candidates_role_applied", "candidates", ["role_applied"], unique=False)
    op.create_table(
        "scores",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("candidate_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("reviewer_id", sa.String(length=36), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("score >= 1 AND score <= 5", name="ck_scores_range"),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidates.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scores_candidate_id", "scores", ["candidate_id"], unique=False)


def downgrade() -> None:
    """Drop core tables and enum types."""
    op.drop_index("ix_scores_candidate_id", table_name="scores")
    op.drop_table("scores")
    op.drop_index("ix_candidates_role_applied", table_name="candidates")
    op.drop_index("ix_candidates_status", table_name="candidates")
    op.drop_table("candidates")
    op.drop_table("users")
    candidate_status_enum.drop(op.get_bind(), checkfirst=True)
    role_enum.drop(op.get_bind(), checkfirst=True)
