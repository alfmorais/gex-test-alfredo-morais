import pytest

from src.application.messages.distribution_message import (
    DistributionMessage,
)


class TestDistributionMessage:
    @pytest.mark.asyncio
    async def test_should_create_message_from_dict(
        self,
    ) -> None:
        payload = {
            "order_id": 10,
            "lead_id": 1,
            "channel": "SMS",
            "phone": "5519999999999",
            "correlation_id": "corr-123",
        }

        result = DistributionMessage.from_dict(payload)

        assert isinstance(result, DistributionMessage)
        assert result.order_id == 10
        assert result.lead_id == 1
        assert result.channel == "SMS"
        assert result.phone == "5519999999999"
        assert result.correlation_id == "corr-123"

    @pytest.mark.asyncio
    async def test_should_map_all_fields_correctly(
        self,
    ) -> None:
        payload = {
            "order_id": 99,
            "lead_id": 77,
            "channel": "EMAIL",
            "phone": "11988887777",
            "correlation_id": "corr-999",
        }

        result = DistributionMessage.from_dict(payload)

        assert result.order_id == 99
        assert result.lead_id == 77
        assert result.channel == "EMAIL"
        assert result.phone == "11988887777"
        assert result.correlation_id == "corr-999"
