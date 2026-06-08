"""Candidate ORM model."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.api.v1.candidates.domain.enums import CandidateStatus
from app.db.base import Base
from app.db.enums import pg_enum


class CandidateModel(Base):
    """ORM model for the candidates table."""

    __tablename__ = "candidates"
    __table_args__ = (
        Index("ix_candidates_status", "status"),
        Index("ix_candidates_role_applied", "role_applied"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role_applied: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[CandidateStatus] = mapped_column(pg_enum(CandidateStatus, "candidatestatus"), nullable=False)
    skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
