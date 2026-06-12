from datetime import datetime

import pytest

from src.application.messages.lead_received_message import (
    LeadBody,
    LeadCustomer,
    LeadPayment,
    LeadProduct,
    LeadReceivedMessage,
)


class TestLeadReceivedMessage:
    @pytest.mark.asyncio
    async def test_should_create_message_from_dict(self) -> None:
        payload = {
            "gateway": "gateway_a",
            "headers": {
                "content-type": "application/json",
            },
            "correlation_id": "corr-123",
            "body": {
                "transaction_id": "tx-123",
                "transaction_time": "2026-06-10T12:30:00",
                "event": "order.approved",
                "idempotency_key": "idem-123",
                "customer": {
                    "first_name": "Alfredo",
                    "last_name": "Morais",
                    "email": "alfredo@email.com",
                    "phone": "19999999999",
                    "country": "BR",
                    "phone_valid": True,
                    "normalized_phone": "5519999999999",
                    "email_valid": True,
                },
                "product": {
                    "id": "prod-1",
                    "name": "Curso Python",
                    "niche": "education",
                    "quantity": 1,
                },
                "payment": {
                    "status": "approved",
                    "amount_usd": 99.9,
                    "method": "credit_card",
                },
            },
        }

        result = LeadReceivedMessage.from_dict(payload)

        assert isinstance(result, LeadReceivedMessage)
        assert result.gateway == "gateway_a"
        assert result.correlation_id == "corr-123"

        assert isinstance(result.body, LeadBody)
        assert result.body.transaction_id == "tx-123"
        assert result.body.transaction_time == datetime(
            2026,
            6,
            10,
            12,
            30,
            0,
        )
        assert result.body.event == "order.approved"
        assert result.body.idempotency_key == "idem-123"

        assert isinstance(result.body.customer, LeadCustomer)
        assert result.body.customer.first_name == "Alfredo"
        assert result.body.customer.email == "alfredo@email.com"
        assert result.body.customer.phone_valid is True

        assert isinstance(result.body.product, LeadProduct)
        assert result.body.product.id == "prod-1"
        assert result.body.product.quantity == 1

        assert isinstance(result.body.payment, LeadPayment)
        assert result.body.payment.status == "approved"
        assert result.body.payment.amount_usd == 99.9
        assert result.body.payment.method == "credit_card"
