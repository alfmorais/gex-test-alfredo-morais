from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.integrations.webhook_site import (
    WebhookSiteIntegration,
)


class TestWebhookSiteIntegration:
    def setup_method(self) -> None:
        self.integration = WebhookSiteIntegration(
            url="https://example.com/webhook",
        )

    @pytest.mark.asyncio
    async def test_should_return_true_when_status_is_ok(
        self,
    ) -> None:
        response = MagicMock()
        response.status_code = HTTPStatus.OK

        client = AsyncMock()
        client.post = AsyncMock(return_value=response)

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = client
        async_cm.__aexit__.return_value = None

        with patch(
            "src.infrastructure.integrations.webhook_site.httpx.AsyncClient",
            return_value=async_cm,
        ):
            result = await self.integration.make_request(
                correlation_id="corr-123",
            )

        assert result is True
        client.post.assert_awaited_once_with("https://example.com/webhook")

    @pytest.mark.asyncio
    async def test_should_return_false_when_status_is_not_ok(
        self,
    ) -> None:
        response = MagicMock()
        response.status_code = HTTPStatus.BAD_REQUEST

        client = AsyncMock()
        client.post = AsyncMock(return_value=response)

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = client
        async_cm.__aexit__.return_value = None

        with patch(
            "src.infrastructure.integrations.webhook_site.httpx.AsyncClient",
            return_value=async_cm,
        ):
            result = await self.integration.make_request(
                correlation_id="corr-999",
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_should_use_timeout_and_url_correctly(
        self,
    ) -> None:
        response = MagicMock()
        response.status_code = HTTPStatus.OK

        client = AsyncMock()
        client.post = AsyncMock(return_value=response)

        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = client
        async_cm.__aexit__.return_value = None

        with patch(
            "src.infrastructure.integrations.webhook_site.httpx.AsyncClient",
            return_value=async_cm,
        ) as mock_client_class:
            await self.integration.make_request(
                correlation_id="corr-123",
            )

        mock_client_class.assert_called_once_with(timeout=10.0)
