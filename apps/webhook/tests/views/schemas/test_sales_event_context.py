import pytest

from src.views.schemas.sales_event import SalesEvent
from src.views.schemas.sales_event_context import SalesEventContext


@pytest.fixture
def sample_sales_event_data():
    return {
        "gateway": "grummer",
        "headers": {"content-type": "application/json"},
        "body": {
            "transaction_id": "TXN-123",
            "transaction_time": "2023-01-01T12:00:00Z",
            "event": "ORDER_CREATED",
            "customer": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "phone": "1234567890",
                "country": "USA",
            },
            "product": {
                "id": "P1",
                "name": "Item",
                "niche": "General",
                "quantity": 1,
            },
            "payment": {
                "status": "paid",
                "amount_usd": 100.00,
                "method": "card",
            },
        },
    }


class TestSalesEventContext:
    @pytest.mark.asyncio
    async def test_sales_event_context_initialization(self):
        context = SalesEventContext(
            correlation_id="corr-123",
            gateway="grummer",
            headers={"Content-Type": "application/json"},
            original_body={"key": "value"},
        )

        assert context.correlation_id == "corr-123"
        assert context.gateway == "grummer"
        assert context.headers == {"Content-Type": "application/json"}
        assert context.original_body == {"key": "value"}
        assert context.validated_body is None
        assert context.decrypted_body is None
        assert context.schema_valid is False
        assert context.decrypt_failed is False
        assert context.duplicate is False
        assert context.validation_errors == []

    @pytest.mark.asyncio
    async def test_sales_event_context_with_all_fields(
        self,
        sample_sales_event_data,
    ):
        validated_event = SalesEvent(**sample_sales_event_data)
        decrypted_data = {"decrypted_key": "decrypted_value"}
        validation_errors = ["Error 1", "Error 2"]

        context = SalesEventContext(
            correlation_id="corr-456",
            gateway="lous",
            headers={"Accept": "application/xml"},
            original_body={"raw_data": "some_raw_data"},
            validated_body=validated_event,
            decrypted_body=decrypted_data,
            schema_valid=True,
            decrypt_failed=True,
            duplicate=True,
            validation_errors=validation_errors,
        )

        assert context.correlation_id == "corr-456"
        assert context.validated_body == validated_event
        assert context.decrypted_body == decrypted_data
        assert context.schema_valid is True
        assert context.decrypt_failed is True
        assert context.duplicate is True
        assert context.validation_errors == validation_errors

    @pytest.mark.asyncio
    async def test_sales_event_context_default_values(self):
        context = SalesEventContext(
            correlation_id="default-corr",
            gateway="default-gw",
            headers={},
            original_body={},
        )

        assert context.validated_body is None
        assert context.decrypted_body is None
        assert context.schema_valid is False
        assert context.decrypt_failed is False
        assert context.duplicate is False
        assert context.validation_errors == []

    @pytest.mark.asyncio
    async def test_sales_event_context_validation_errors_mutability(self):
        context1 = SalesEventContext(
            correlation_id="corr-789",
            gateway="test",
            headers={},
            original_body={},
        )
        context1.validation_errors.append("Error for context 1")

        context2 = SalesEventContext(
            correlation_id="corr-012",
            gateway="test",
            headers={},
            original_body={},
        )

        assert context1.validation_errors == ["Error for context 1"]
        assert context2.validation_errors == [], (
            "validation_errors deve ser uma lista vazia por padrão"
        )

    @pytest.mark.asyncio
    async def test_sales_event_context_type_hints(
        self,
        sample_sales_event_data,
    ):
        validated_event = SalesEvent(**sample_sales_event_data)
        context = SalesEventContext(
            correlation_id="type-check",
            gateway="type-gw",
            headers={"X-Custom": "Value"},
            original_body={"data": 123},
            validated_body=validated_event,
            decrypted_body={"processed": True},
        )

        assert isinstance(context.correlation_id, str)
        assert isinstance(context.gateway, str)
        assert isinstance(context.headers, dict)
        assert isinstance(context.original_body, dict)
        assert isinstance(context.validated_body, SalesEvent)
        assert isinstance(context.decrypted_body, dict)
        assert isinstance(context.schema_valid, bool)
        assert isinstance(context.decrypt_failed, bool)
        assert isinstance(context.duplicate, bool)
        assert isinstance(context.validation_errors, list)
