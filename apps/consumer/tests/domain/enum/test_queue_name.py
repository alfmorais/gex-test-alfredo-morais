import pytest

from src.domain.enum.queue_name import QueueName


class TestQueueName:
    @pytest.mark.asyncio
    async def test_should_have_expected_values(self) -> None:
        assert QueueName.LEAD_RECEIVED.value == "lead.received"
        assert (
            QueueName.LEAD_DEAD_CONSUMER_FAILED.value
            == "lead.dead.consumer_failed"
        )

    @pytest.mark.asyncio
    async def test_should_have_expected_number_of_members(
        self,
    ) -> None:
        assert len(QueueName) == 2

    @pytest.mark.asyncio
    async def test_should_be_accessible_by_name(
        self,
    ) -> None:
        assert QueueName["LEAD_RECEIVED"] is QueueName.LEAD_RECEIVED
        assert (
            QueueName["LEAD_DEAD_CONSUMER_FAILED"]
            is QueueName.LEAD_DEAD_CONSUMER_FAILED
        )

    @pytest.mark.asyncio
    async def test_should_iterate_all_members(
        self,
    ) -> None:
        members = list(QueueName)

        assert QueueName.LEAD_RECEIVED in members
        assert QueueName.LEAD_DEAD_CONSUMER_FAILED in members
