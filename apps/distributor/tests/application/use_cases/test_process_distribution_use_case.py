from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.application.messages.distribution_message import DistributionMessage
from src.application.use_cases.process_distribution import (
    ProcessDistributionUseCase,
)
from src.domain.entities.distribution_status import DistributionStatus
from src.domain.enum.queue_name import QueueName
from src.domain.exceptions.distribution_not_found import (
    DistributionNotFoundError,
)


class TestProcessDistributionUseCase:
    def setup_method(self) -> None:
        self.integration = AsyncMock()
        self.publisher = AsyncMock()
        self.repository = AsyncMock()
        self.dead_letter_repository = AsyncMock()

        self.use_case = ProcessDistributionUseCase(
            integration=self.integration,
            publisher=self.publisher,
            repository=self.repository,
            dead_letter_repository=self.dead_letter_repository,
        )

        self.message = DistributionMessage(
            order_id=10,
            lead_id=1,
            channel="SMS",
            phone="5519999999999",
            correlation_id="corr-123",
        )

        self.distribution_instance = MagicMock()
        self.distribution_instance.created_at = MagicMock()

    @pytest.mark.asyncio
    async def test_should_raise_distribution_not_found_error(
        self,
    ) -> None:
        self.repository.get_by_order_id_and_channel.return_value = None

        with pytest.raises(
            DistributionNotFoundError,
            match=("Distribution not found for order_id=10 and channel=SMS"),
        ):
            await self.use_case.execute(self.message)

    @pytest.mark.asyncio
    async def test_should_update_as_delivered_when_webhook_success(
        self,
    ) -> None:
        self.repository.get_by_order_id_and_channel.return_value = (
            self.distribution_instance
        )

        self.use_case.send_webhook = AsyncMock(return_value=True)

        await self.use_case.execute(self.message)

        self.repository.update.assert_awaited_once()

        updated_instance = self.repository.update.await_args.args[0]

        assert updated_instance.status == DistributionStatus.DELIVERED

        self.publisher.publish.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_mark_failed_and_send_to_dead_letter(
        self,
    ) -> None:
        self.repository.get_by_order_id_and_channel.return_value = (
            self.distribution_instance
        )

        self.use_case.send_webhook = AsyncMock(return_value=False)

        await self.use_case.execute(self.message)

        self.repository.update.assert_awaited_once()

        updated_instance = self.repository.update.await_args.args[0]

        assert updated_instance.status == DistributionStatus.FAILED

        self.publisher.publish.assert_awaited_once_with(
            QueueName.DIST_DEAD_SMS.value,
            {
                "order_id": 10,
                "channel": "SMS",
                "message": "Webhook not sent",
            },
        )

    @pytest.mark.asyncio
    async def test_should_call_send_webhook_with_correct_data(
        self,
    ) -> None:
        self.repository.get_by_order_id_and_channel.return_value = (
            self.distribution_instance
        )

        self.use_case.send_webhook = AsyncMock(return_value=True)

        await self.use_case.execute(self.message)

        self.use_case.send_webhook.assert_awaited_once_with(self.message)

    @pytest.mark.asyncio
    async def test_should_call_repository_with_correct_params(
        self,
    ) -> None:
        self.repository.get_by_order_id_and_channel.return_value = (
            self.distribution_instance
        )

        self.use_case.send_webhook = AsyncMock(return_value=True)

        await self.use_case.execute(self.message)

        self.repository.get_by_order_id_and_channel.assert_awaited_once_with(
            order_id=10,
            channel="SMS",
        )

    @patch(
        "src.application.use_cases.process_distribution.random.random",
        return_value=0.05,
    )
    @pytest.mark.asyncio
    async def test_should_fail_webhook_due_to_random(self, mock_random):
        result = await self.use_case.send_webhook(self.message)

        assert result is False

    @patch(
        "src.application.use_cases.process_distribution.random.random",
        return_value=1.8,
    )
    @pytest.mark.asyncio
    async def test_should_pass_webhook_due_to_random(self, mock_random):
        self.integration.make_request = AsyncMock(return_value=True)

        result = await self.use_case.send_webhook(self.message)

        assert result is True
