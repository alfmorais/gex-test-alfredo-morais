from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.application.messages.lead_received_message import (
    LeadBody,
    LeadCustomer,
    LeadPayment,
    LeadProduct,
    LeadReceivedMessage,
)
from src.application.use_cases.process_lead_received import (
    ProcessLeadReceivedUseCase,
)
from src.domain.entities.distribution_status import (
    DistributionStatus,
)
from src.domain.enum.distribution_channel import CHANNEL_QUEUES


class TestProcessLeadReceivedUseCase:
    def setup_method(self) -> None:
        self.lead_repository = AsyncMock()
        self.distribution_repository = AsyncMock()
        self.publisher = AsyncMock()

        self.use_case = ProcessLeadReceivedUseCase(
            lead_repository=self.lead_repository,
            distribution_repository=self.distribution_repository,
            publisher=self.publisher,
        )

        self.message = LeadReceivedMessage(
            gateway="gateway",
            headers={},
            correlation_id="corr-123",
            body=LeadBody(
                transaction_id="tx-123",
                transaction_time=datetime.now(UTC),
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
    async def test_should_execute_flow(self) -> None:
        self.lead_repository.insert_lead.return_value = (1, 10)

        await self.use_case.execute(self.message)

        self.lead_repository.insert_lead.assert_awaited_once()
        self.distribution_repository.bulk_create.assert_awaited_once()

        assert self.publisher.publish.await_count == len(CHANNEL_QUEUES)

    @pytest.mark.asyncio
    async def test_should_call_store_procedure(self) -> None:
        self.lead_repository.insert_lead.return_value = (1, 10)

        lead_id, order_id = await self.use_case.call_store_procedure(
            self.message
        )

        assert lead_id == 1
        assert order_id == 10

        self.lead_repository.insert_lead.assert_awaited_once()

        kwargs = self.lead_repository.insert_lead.await_args.kwargs

        assert kwargs["message"] == self.message
        assert isinstance(kwargs["lag_seconds"], int)

    @pytest.mark.asyncio
    async def test_should_create_distribution(self) -> None:
        await self.use_case.create_distribution(
            message=self.message,
            order_id=10,
        )

        self.distribution_repository.bulk_create.assert_awaited_once()

        distributions = (
            self.distribution_repository.bulk_create.await_args.args[0]
        )

        assert len(distributions) == 4

        for distribution in distributions:
            assert distribution.order_id == 10
            assert distribution.status == DistributionStatus.PENDING.value

    @pytest.mark.asyncio
    async def test_should_publish_event_for_all_channels(self) -> None:
        await self.use_case.publish_event(
            message=self.message,
            order_id=10,
            lead_id=1,
        )

        assert self.publisher.publish.await_count == len(CHANNEL_QUEUES)

        calls = self.publisher.publish.await_args_list

        for index, (channel, routing_key) in enumerate(CHANNEL_QUEUES.items()):
            args = calls[index].args

            assert args[0] == routing_key

            payload = args[1]

            assert payload["order_id"] == 10
            assert payload["lead_id"] == 1
            assert payload["channel"] == channel.value
            assert payload["phone"] == "5519999999999"
            assert payload["correlation_id"] == "corr-123"
