from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from src.controllers.services.event_sales.base_service import (
    EventSalesBaseService,
)
from src.views.schemas.sales_event_context import SalesEventContext


class ConcreteService(EventSalesBaseService):
    async def decrypt_event(
        self,
        context: SalesEventContext,
    ) -> SalesEventContext:
        return context


class TestEventSalesBaseService:
    @pytest.fixture
    def repository(self):
        return AsyncMock()

    @pytest.fixture
    def publisher(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, repository, publisher):
        return ConcreteService(
            repository=repository,
            publisher=publisher,
        )

    @staticmethod
    def make_validated_body(
        idempotency_key: str = "idem-123",
        event: str = "order.approved",
        transaction_id: str = "tx-123",
    ):
        return type(
            "ValidatedBody",
            (),
            {
                "body": type(
                    "Body",
                    (),
                    {
                        "idempotency_key": idempotency_key,
                        "event": event,
                        "transaction_id": transaction_id,
                    },
                )()
            },
        )()

    @pytest.mark.asyncio
    async def test_check_idempotency_duplicate(
        self,
        service,
        repository,
    ):
        repository.exists.return_value = True

        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={},
            original_body={},
            validated_body=self.make_validated_body(),
        )

        result = await service.check_idempotency(context)

        assert result.duplicate is True

        repository.exists.assert_awaited_once_with("idem-123")

    @pytest.mark.asyncio
    async def test_check_idempotency_not_duplicate(
        self,
        service,
        repository,
    ):
        repository.exists.return_value = False

        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={},
            original_body={},
            validated_body=self.make_validated_body(),
        )

        result = await service.check_idempotency(context)

        assert result.duplicate is False

        repository.exists.assert_awaited_once_with("idem-123")

    @pytest.mark.asyncio
    async def test_check_idempotency_without_validated_body(
        self,
        service,
        repository,
    ):
        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={},
            original_body={},
        )

        result = await service.check_idempotency(context)

        assert result.duplicate is False

        repository.exists.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_event(
        self,
        service,
        repository,
    ):
        repository.save.return_value = True

        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={"content-type": "application/json"},
            original_body={"foo": "bar"},
            decrypted_body={"foo": "bar"},
            validated_body=self.make_validated_body(),
        )

        result = await service.save_event(context)

        assert result is True

        repository.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_publish_event(
        self,
        service,
        publisher,
    ):
        payload = {"transaction_id": "123"}

        result = await service.publish_event(
            queue_name="sales-events",
            payload=payload,
        )

        assert result is True

        publisher.publish.assert_awaited_once_with(
            queue_name="sales-events",
            payload=payload,
        )

    @pytest.mark.asyncio
    async def test_validate_event_success(
        self,
        service,
    ):
        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={"content-type": "application/json"},
            original_body={},
            decrypted_body={
                "transaction_id": "123",
            },
        )

        fake_model = object()
        path = (
            "src"
            ".controllers"
            ".services"
            ".event_sales"
            ".base_service"
            ".SalesEvent"
            ".model_validate"
        )

        with patch(path, return_value=fake_model):
            result = await service.validate_event(context)

        assert result.schema_valid is True
        assert result.validated_body is fake_model
        assert result.validation_errors == []

    @pytest.mark.asyncio
    async def test_validate_event_validation_error(
        self,
        service,
    ):
        context = SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={"content-type": "application/json"},
            original_body={},
            decrypted_body={},
        )

        validation_error = ValidationError.from_exception_data(
            "SalesEvent",
            [
                {
                    "type": "missing",
                    "loc": ("body", "product"),
                    "msg": "Field required",
                    "input": {},
                }
            ],
        )
        path = (
            "src"
            ".controllers"
            ".services"
            ".event_sales"
            ".base_service"
            ".SalesEvent"
            ".model_validate"
        )

        with patch(path, side_effect=validation_error):
            result = await service.validate_event(context)

        assert result.schema_valid is False
        assert len(result.validation_errors) == 1
