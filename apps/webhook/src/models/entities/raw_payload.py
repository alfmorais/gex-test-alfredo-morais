from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel, UniqueConstraint


class RawPayload(SQLModel, table=True):
    __tablename__ = "raw_payloads"

    id: Optional[int] | None = Field(
        default=None,
        primary_key=True,
        description="Unique identifier of the raw payload record",
    )

    transaction_id: Optional[str] = Field(
        description="Transaction ID extracted from the payload",
    )

    event: Optional[str] = Field(
        description="Event type",
    )

    idempotency_key: Optional[str] = Field(
        description="Idempotency key for deduplication",
        unique=True,
        index=True,
    )

    correlation_id: str = Field(
        description="Request correlation identifier",
    )

    gateway: str = Field(
        description="Gateway name",
    )

    received_at: datetime = Field(
        description="UTC timestamp when the webhook was received",
        default_factory=lambda: datetime.now(UTC),
    )

    headers: dict[str, Any] = Field(
        description="HTTP request headers",
        sa_column=Column(JSON),
    )

    body: dict[str, Any] = Field(
        description="Original request body",
        sa_column=Column(JSON),
    )

    decrypted_body: dict[str, Any] | None = Field(
        default=None,
        description="Decrypted payload when applicable",
        sa_column=Column(JSON),
    )

    raw_payload: dict[str, Any] = Field(
        description="Complete payload exactly as received",
        sa_column=Column(JSON),
    )

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "event",
            name="uq_transaction_event",
        ),
    )
