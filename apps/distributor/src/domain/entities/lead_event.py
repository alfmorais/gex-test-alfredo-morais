from datetime import datetime

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class LeadEvent(SQLModel, table=True):
    __tablename__ = "lead_events"

    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "event",
            name="uk_order_event",
        ),
        Index(
            "idx_lead_events_transaction_time",
            "gateway_transaction_time",
        ),
        Index(
            "idx_lead_events_correlation",
            "correlation_id",
        ),
    )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    order_id: int = Field(foreign_key="orders.id")

    correlation_id: str

    event: str

    gateway_transaction_time: datetime

    persisted_at: datetime

    lag_seconds: int

    created_at: datetime = Field(default_factory=datetime.now)
