from datetime import datetime
from enum import StrEnum

from sqlalchemy import Column, Enum, Index
from sqlmodel import Field, SQLModel


class DistributionChannel(StrEnum):
    SMS = "SMS"
    EMAIL = "EMAIL"
    CALL_CENTER = "CALL_CENTER"
    WHATSAPP = "WHATSAPP"


class DistributionStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class DistributionStatusModel(SQLModel, table=True):
    __tablename__ = "distribution_status"

    __table_args__ = (
        Index(
            "idx_distribution_channel_status",
            "channel",
            "status",
        ),
        Index(
            "idx_distribution_delivered",
            "delivered_at",
        ),
        Index(
            "idx_distribution_order",
            "order_id",
        ),
    )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    order_id: int = Field(foreign_key="orders.id")

    channel: DistributionChannel = Field(
        sa_column=Column(
            Enum(
                DistributionChannel,
                native_enum=False,
            ),
            nullable=False,
        )
    )

    status: DistributionStatus = Field(
        sa_column=Column(
            Enum(
                DistributionStatus,
                native_enum=False,
            ),
            nullable=False,
        )
    )

    created_at: datetime = Field(default_factory=datetime.now)

    updated_at: datetime | None = None

    delivered_at: datetime | None = None

    lag_seconds: int | None
