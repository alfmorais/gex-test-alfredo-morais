from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class LeadCustomer:
    first_name: str
    last_name: str
    email: str
    phone: str | None
    country: str | None

    phone_valid: bool | None
    normalized_phone: str | None
    email_valid: bool | None


@dataclass(frozen=True)
class LeadProduct:
    id: str
    name: str
    niche: str | None
    quantity: int


@dataclass(frozen=True)
class LeadPayment:
    status: str
    amount_usd: float
    method: str


@dataclass(frozen=True)
class LeadBody:
    transaction_id: str
    transaction_time: datetime
    event: str

    customer: LeadCustomer
    product: LeadProduct
    payment: LeadPayment

    idempotency_key: str


@dataclass(frozen=True)
class LeadReceivedMessage:
    gateway: str
    headers: dict[str, Any]
    body: LeadBody
    correlation_id: str

    @staticmethod
    def from_dict(data: dict) -> "LeadReceivedMessage":
        body = data["body"]
        transaction_time = datetime.fromisoformat(body["transaction_time"])

        return LeadReceivedMessage(
            gateway=data["gateway"],
            headers=data["headers"],
            correlation_id=data["correlation_id"],
            body=LeadBody(
                transaction_id=body["transaction_id"],
                transaction_time=transaction_time,
                event=body["event"],
                idempotency_key=body["idempotency_key"],
                customer=LeadCustomer(**body["customer"]),
                product=LeadProduct(**body["product"]),
                payment=LeadPayment(**body["payment"]),
            ),
        )
