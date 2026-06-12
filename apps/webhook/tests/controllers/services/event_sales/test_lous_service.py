from unittest.mock import AsyncMock

import pytest

from src.controllers.services.event_sales.lous_service import (
    LousEventSalesService,
)
from src.views.schemas.sales_event_context import SalesEventContext


class TestLousEventSalesService:
    @pytest.fixture
    def repository(self):
        return AsyncMock()

    @pytest.fixture
    def publisher(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, repository, publisher):
        return LousEventSalesService(
            repository=repository,
            publisher=publisher,
        )

    @pytest.mark.asyncio
    async def test_decrypt_event_success(
        self,
        service,
    ):
        payload = {
            "transaction_id": "tx-123",
            "event": "order.approved",
        }

        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="lous",
            headers={},
            original_body={
                "body": payload,
            },
        )

        result = await service.decrypt_event(context)

        assert result is context
        assert result.decrypted_body == payload
        assert result.decrypt_failed is False
        assert result.validation_errors == []
