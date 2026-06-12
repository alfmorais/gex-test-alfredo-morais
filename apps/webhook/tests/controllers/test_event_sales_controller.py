from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.responses import Response

from src.controllers.event_sales_controller import (
    EventSalesController,
)
from src.views.schemas.sales_event_context import (
    SalesEventContext,
)


class TestEventSalesController:
    @pytest.fixture
    def service(self):
        service = AsyncMock()

        service.decrypt_event = AsyncMock()
        service.validate_event = AsyncMock()
        service.check_idempotency = AsyncMock()
        service.save_event = AsyncMock()
        service.publish_event = AsyncMock()

        return service

    @pytest.fixture
    def controller(self, service):
        return EventSalesController(service)

    @pytest.fixture
    def context(self):
        return SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={},
            original_body={},
        )

    @pytest.mark.asyncio
    async def test_execute_decrypt_failed(
        self,
        controller,
        service,
        context,
    ):
        context.decrypt_failed = True

        service.decrypt_event.return_value = context

        response = await controller.execute(context)

        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_200_OK

        service.save_event.assert_awaited_once()
        service.publish_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_schema_validation_failed(
        self,
        controller,
        service,
        context,
    ):
        decrypt_context = context

        validated_context = context
        validated_context.schema_valid = False

        service.decrypt_event.return_value = decrypt_context
        service.validate_event.return_value = validated_context

        response = await controller.execute(context)

        assert response.status_code == status.HTTP_200_OK

        service.save_event.assert_awaited_once()
        service.publish_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_duplicate_event(
        self,
        controller,
        service,
        context,
    ):
        context.schema_valid = True
        context.duplicate = True

        service.decrypt_event.return_value = context
        service.validate_event.return_value = context
        service.check_idempotency.return_value = context

        response = await controller.execute(context)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_200_OK

        service.publish_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_lead_received(
        self,
        controller,
        service,
        context,
    ):
        payload = MagicMock()

        payload.body.event = "order.approved"
        payload.body.payment.status = "approved"

        payload.model_dump.return_value = {"transaction_id": "123"}

        context.schema_valid = True
        context.duplicate = False
        context.validated_body = payload

        service.decrypt_event.return_value = context
        service.validate_event.return_value = context
        service.check_idempotency.return_value = context

        response = await controller.execute(context)

        assert response.status_code == status.HTTP_200_OK

        service.save_event.assert_awaited_once()
        service.publish_event.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_event_not_approved(
        self,
        controller,
        service,
        context,
    ):
        payload = MagicMock()

        payload.body.event = "order.pending"
        payload.body.payment.status = "pending"

        context.schema_valid = True
        context.duplicate = False
        context.validated_body = payload

        service.decrypt_event.return_value = context
        service.validate_event.return_value = context
        service.check_idempotency.return_value = context

        response = await controller.execute(context)

        assert response.status_code == status.HTTP_200_OK

        service.save_event.assert_awaited_once()

        service.publish_event.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_lead_received_without_payload(
        self,
        controller,
    ):
        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={},
            original_body={},
        )

        context.validated_body = None

        response = await controller._handle_lead_received(context)

        assert response.status_code == status.HTTP_200_OK
