"""User ORM model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.api.v1.auth.domain.enums import Role
from app.db.base import Base
from app.db.enums import pg_enum


class UserModel(Base):
    """ORM model for the users table."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(pg_enum(Role, "role"), nullable=False)
