import pytest

from src.domain.enum.queue_name import QueueName


class TestQueueName:
    @pytest.mark.asyncio
    async def test_should_have_expected_values(
        self,
    ) -> None:
        assert QueueName.DIST_SMS.value == "dist.sms"

        assert QueueName.DIST_DEAD_SMS.value == "dist.dead.sms"

    @pytest.mark.asyncio
    async def test_should_have_expected_number_of_members(
        self,
    ) -> None:
        assert len(QueueName) == 2

    @pytest.mark.asyncio
    async def test_should_be_accessible_by_name(
        self,
    ) -> None:
        assert QueueName["DIST_SMS"] is QueueName.DIST_SMS

        assert QueueName["DIST_DEAD_SMS"] is QueueName.DIST_DEAD_SMS

    @pytest.mark.asyncio
    async def test_should_iterate_all_members(
        self,
    ) -> None:
        members = list(QueueName)

        assert QueueName.DIST_SMS in members
        assert QueueName.DIST_DEAD_SMS in members

    @pytest.mark.asyncio
    async def test_should_have_unique_values(
        self,
    ) -> None:
        values = {member.value for member in QueueName}

        assert len(values) == len(QueueName)
