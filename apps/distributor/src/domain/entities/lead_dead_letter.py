from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, SQLModel


class LeadDeadLetter(SQLModel, table=True):
    __tablename__ = "lead_dead_letter"

    __table_args__ = (
        Index(
            "idx_dlq_created_at",
            "created_at",
        ),
        Index(
            "idx_dlq_source_queue",
            "source_queue",
        ),
    )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    source_queue: str

    payload: dict[str, Any] = Field(sa_column=Column(JSON, nullable=False))

    error_message: str

    created_at: datetime = Field(default_factory=datetime.now)
