from decimal import Decimal

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    __table_args__ = (
        UniqueConstraint(
            "gateway",
            "transaction_id",
            name="uk_gateway_transaction",
        ),
        Index(
            "idx_orders_lead_id",
            "lead_id",
        ),
    )

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    lead_id: int = Field(foreign_key="leads.id")

    gateway: str

    transaction_id: str

    product_name: str | None = None

    amount: Decimal | None = Field(
        default=None,
        decimal_places=2,
        max_digits=10,
    )
