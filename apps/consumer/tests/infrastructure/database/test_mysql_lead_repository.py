from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.messages.lead_received_message import (
    LeadBody,
    LeadCustomer,
    LeadPayment,
    LeadProduct,
    LeadReceivedMessage,
)
from src.infrastructure.database.mysql_lead_repository import (
    MySQLLeadRepository,
)


class TestMySQLLeadRepository:
    def setup_method(self) -> None:
        self.session = AsyncMock()

        self.repository = MySQLLeadRepository(
            session=self.session,
        )

        self.message = LeadReceivedMessage(
            gateway="gateway",
            headers={},
            correlation_id="corr-123",
            body=LeadBody(
                transaction_id="tx-123",
                transaction_time=datetime(
                    2026,
                    6,
                    10,
                    12,
                    30,
                    tzinfo=UTC,
                ),
                event="order.approved",
                idempotency_key="idem-123",
                customer=LeadCustomer(
                    first_name="Alfredo",
                    last_name="Morais",
                    email="alfredo@email.com",
                    phone="5519999999999",
                    country="BR",
                    phone_valid=True,
                    normalized_phone="5519999999999",
                    email_valid=True,
                ),
                product=LeadProduct(
                    id="product-1",
                    name="Curso Python",
                    niche="education",
                    quantity=1,
                ),
                payment=LeadPayment(
                    status="approved",
                    amount_usd=99.9,
                    method="credit_card",
                ),
            ),
        )

    @pytest.mark.asyncio
    async def test_should_insert_lead_and_return_ids(
        self,
    ) -> None:
        row = SimpleNamespace(
            lead_id=1,
            order_id=10,
        )

        result_proxy = MagicMock()
        result_proxy.fetchone.return_value = row

        self.session.execute.return_value = result_proxy

        result = await self.repository.insert_lead(
            message=self.message,
            lag_seconds=15,
        )

        assert result == (1, 10)

        self.session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_send_expected_parameters_to_stored_procedure(
        self,
    ) -> None:
        row = SimpleNamespace(
            lead_id=1,
            order_id=10,
        )

        result_proxy = MagicMock()
        result_proxy.fetchone.return_value = row

        self.session.execute.return_value = result_proxy

        await self.repository.insert_lead(
            message=self.message,
            lag_seconds=30,
        )

        _, params = self.session.execute.await_args.args

        assert params["name"] == "Alfredo Morais"
        assert params["email"] == "alfredo@email.com"
        assert params["phone"] == "5519999999999"
        assert params["gateway"] == "gateway"
        assert params["transaction_id"] == "tx-123"
        assert params["product_name"] == "Curso Python"
        assert params["amount"] == 99.9
        assert params["event"] == "order.approved"
        assert params["correlation_id"] == "corr-123"
        assert params["lag_seconds"] == 30

        assert params["transaction_time"] == datetime(
            2026,
            6,
            10,
            12,
            30,
        )

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_sp_returns_none(
        self,
    ) -> None:
        result_proxy = MagicMock()
        result_proxy.fetchone.return_value = None

        self.session.execute.return_value = result_proxy

        with pytest.raises(
            RuntimeError,
            match=("Stored procedure sp_insert_lead did not return a result"),
        ):
            await self.repository.insert_lead(
                message=self.message,
                lag_seconds=10,
            )

        self.session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_propagate_execute_exception(
        self,
    ) -> None:
        self.session.execute.side_effect = RuntimeError(
            "database error",
        )

        with pytest.raises(
            RuntimeError,
            match="database error",
        ):
            await self.repository.insert_lead(
                message=self.message,
                lag_seconds=10,
            )

        self.session.execute.assert_awaited_once()
