"""Session ORM model."""

from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class SessionORM(SQLModel, table=True):
    """Session table ORM model."""

    __tablename__ = "sessions"  # type: ignore[reportAssignmentType]

    id: str = Field(primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
