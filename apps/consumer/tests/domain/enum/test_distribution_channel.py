import pytest

from src.domain.enum.distribution_channel import (
    CHANNEL_QUEUES,
    DistributionChannel,
)


class TestDistributionChannel:
    @pytest.mark.asyncio
    async def test_should_have_expected_values(self) -> None:
        assert DistributionChannel.SMS.value == "SMS"
        assert DistributionChannel.EMAIL.value == "EMAIL"
        assert DistributionChannel.CALL_CENTER.value == "CALL_CENTER"
        assert DistributionChannel.WHATSAPP.value == "WHATSAPP"

    @pytest.mark.asyncio
    async def test_should_have_expected_channel_queues(self) -> None:
        assert CHANNEL_QUEUES[DistributionChannel.SMS] == "dist.sms"
        assert CHANNEL_QUEUES[DistributionChannel.EMAIL] == "dist.email"
        assert (
            CHANNEL_QUEUES[DistributionChannel.CALL_CENTER]
            == "dist.callcenter"
        )
        assert CHANNEL_QUEUES[DistributionChannel.WHATSAPP] == "dist.whatsapp"

    @pytest.mark.asyncio
    async def test_should_have_mapping_for_all_channels(
        self,
    ) -> None:
        assert len(CHANNEL_QUEUES) == len(DistributionChannel)

        for channel in DistributionChannel:
            assert channel in CHANNEL_QUEUES

    @pytest.mark.asyncio
    async def test_should_use_distribution_channel_as_keys(
        self,
    ) -> None:
        for key in CHANNEL_QUEUES:
            assert isinstance(
                key,
                DistributionChannel,
            )
