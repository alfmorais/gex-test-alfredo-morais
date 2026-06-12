import pytest
from pydantic import ValidationError

from src.views.schemas.sales_event import (
    BaseHeaders,
    BaseSalesEvent,
    Body,
    Customer,
    EncryptedSalesEvent,
    EncryptedSalesEventBody,
    EncryptedSalesEventHeaders,
    Payment,
    Product,
    SalesEvent,
)


@pytest.fixture
def valid_sales_event_payload():
    return {
        "gateway": "grummer",
        "headers": {"content-type": "application/json"},
        "body": {
            "transaction_id": "TRANS-12345",
            "transaction_time": "2023-10-27T10:00:00Z",
            "event": "ORDER_CREATED",
            "customer": {
                "first_name": "  John  ",
                "last_name": "Doe",
                "email": "  john.doe@example.com  ",
                "phone": "  +1 (555) 123-4567  ",
                "country": "USA",
            },
            "product": {
                "id": "PROD-ABC",
                "name": "Awesome Product",
                "niche": "Electronics",
                "quantity": 2,
            },
            "payment": {
                "status": "approved",
                "amount_usd": 99.99,
                "method": "credit_card",
            },
        },
    }


@pytest.fixture
def valid_encrypted_sales_event_payload():
    return {
        "headers": {
            "content-type": "application/json",
            "X-GR-Encrypted": True,
        },
        "body": {
            "iv": "some_initialization_vector",
            "ciphertext": "encrypted_data_string",
        },
    }


class TestSalesEventSchemas:
    @pytest.mark.asyncio
    async def test_base_sales_event(self):
        event = BaseSalesEvent(gateway="grummer")

        assert event.gateway == "grummer"

        with pytest.raises(ValidationError):
            BaseSalesEvent(gateway=123)

    @pytest.mark.asyncio
    async def test_base_headers(self):
        headers = BaseHeaders(**{"content-type": "application/json"})

        assert headers.content_type == "application/json"

        with pytest.raises(ValidationError):
            BaseHeaders()

    @pytest.mark.asyncio
    async def test_encrypted_sales_event_headers(self):
        headers = EncryptedSalesEventHeaders(
            **{"content-type": "application/json"},
        )

        assert headers.content_type == "application/json"
        assert headers.x_gr_encrypted is False

        headers_encrypted = EncryptedSalesEventHeaders(**{
            "content-type": "application/json",
            "X-GR-Encrypted": True,
        })
        assert headers_encrypted.x_gr_encrypted is True

    @pytest.mark.asyncio
    async def test_encrypted_sales_event_body(self):
        body = EncryptedSalesEventBody(iv="abc", ciphertext="xyz")

        assert body.iv == "abc"
        assert body.ciphertext == "xyz"

        with pytest.raises(ValidationError):
            EncryptedSalesEventBody(iv="abc")

    @pytest.mark.asyncio
    async def test_encrypted_sales_event(
        self,
        valid_encrypted_sales_event_payload,
    ):
        event = EncryptedSalesEvent(
            **valid_encrypted_sales_event_payload,
        )

        assert event.headers.content_type == "application/json"
        assert event.headers.x_gr_encrypted is True
        assert event.body.iv == "some_initialization_vector"

    @pytest.mark.asyncio
    async def test_customer_normalization(self):
        customer = Customer(
            first_name="  TEST  ",
            last_name="User",
            email="  TEST.USER@EXAMPLE.COM  ",
            phone="  (123) 456-7890  ",
            country="BR",
        )

        assert customer.first_name == "TEST"
        assert customer.email == "test.user@example.com"
        assert customer.phone == "1234567890"

        customer_empty_name = Customer(
            first_name="",
            last_name="User",
            email="test.user@example.com",
            phone="1234567890",
            country="BR",
        )

        assert customer_empty_name.first_name == "Customer"

        customer_phone_with_plus = Customer(
            first_name="Test",
            last_name="User",
            email="test.user@example.com",
            phone="+1 (555) 123-4567",
            country="BR",
        )

        assert customer_phone_with_plus.phone == "+15551234567"

    @pytest.mark.asyncio
    async def test_customer_phone_valid_property(self):
        customer_valid_phone = Customer(
            first_name="Test",
            last_name="User",
            email="a@b.com",
            phone="1234567890",
            country="BR",
        )
        assert customer_valid_phone.phone_valid is True

        customer_invalid_phone = Customer(
            first_name="Test",
            last_name="User",
            email="a@b.com",
            phone="123",
            country="BR",
        )
        assert customer_invalid_phone.phone_valid is False

    @pytest.mark.asyncio
    async def test_customer_normalized_phone_property(self):
        customer_normalized = Customer(
            first_name="Test",
            last_name="User",
            email="a@b.com",
            phone="1234567890",
            country="BR",
        )
        assert customer_normalized.normalized_phone == "+1234567890"

        customer_short_phone = Customer(
            first_name="Test",
            last_name="User",
            email="a@b.com",
            phone="123",
            country="BR",
        )
        assert customer_short_phone.normalized_phone == "123"

    @pytest.mark.asyncio
    async def test_customer_email_valid_property(self):
        customer_valid_email = Customer(
            first_name="Test",
            last_name="User",
            email="valid@example.com",
            phone="1234567890",
            country="BR",
        )

        assert customer_valid_email.email_valid is True

        customer_invalid_email = Customer(
            first_name="Test",
            last_name="User",
            email="invalid-email",
            phone="1234567890",
            country="BR",
        )

        assert customer_invalid_email.email_valid is False

    @pytest.mark.asyncio
    async def test_product_model(self):
        product = Product(id="P1", name="Item", niche="General", quantity=1)

        assert product.id == "P1"
        assert product.quantity == 1

        with pytest.raises(ValidationError):
            Product(
                id="P1",
                name="Item",
                niche="General",
                quantity="abc",
            )

    @pytest.mark.asyncio
    async def test_payment_model(self):
        payment = Payment(
            status="paid",
            amount_usd=100.50,
            method="card",
        )

        assert payment.status == "paid"
        assert payment.amount_usd == 100.50

        payment_with_alias = Payment(
            status="paid",
            amount_usd=200.00,
            method="pix",
        )
        assert payment_with_alias.amount_usd == 200.00

        with pytest.raises(ValidationError):
            Payment(status="paid", amount_usd="invalid", method="card")

    @pytest.mark.asyncio
    async def test_body_model(self):
        customer_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "country": "USA",
        }
        product_data = {
            "id": "P1",
            "name": "Item",
            "niche": "General",
            "quantity": 1,
        }
        payment_data = {
            "status": "paid",
            "amount_usd": 100.00,
            "method": "card",
        }

        body = Body(
            transaction_id="TXN-001",
            transaction_time="2023-10-27T11:00:00Z",
            event="ORDER_UPDATED",
            customer=customer_data,
            product=product_data,
            payment=payment_data,
        )

        assert body.idempotency_key == "TXN-001:ORDER_UPDATED"
        assert isinstance(body.customer, Customer)
        assert isinstance(body.product, Product)
        assert isinstance(body.payment, Payment)

    @pytest.mark.asyncio
    async def test_sales_event_model_full_payload(
        self,
        valid_sales_event_payload,
    ):
        sales_event = SalesEvent(**valid_sales_event_payload)

        assert sales_event.gateway == "grummer"
        assert sales_event.headers.content_type == "application/json"
        assert sales_event.body.transaction_id == "TRANS-12345"
        assert sales_event.body.customer.email == "john.doe@example.com"
        assert sales_event.body.product.name == "Awesome Product"
        assert sales_event.body.payment.amount_usd == 99.99
        assert sales_event.body.idempotency_key == "TRANS-12345:ORDER_CREATED"

    @pytest.mark.asyncio
    async def test_sales_event_model_invalid_payload(
        self,
        valid_sales_event_payload,
    ):
        invalid_payload = valid_sales_event_payload.copy()

        del invalid_payload["gateway"]

        with pytest.raises(ValidationError):
            SalesEvent(**invalid_payload)

        invalid_payload_nested = valid_sales_event_payload.copy()
        invalid_payload_nested["body"]["customer"]["email"] = "invalid-email"

        invalid_sales_event = SalesEvent(**invalid_payload_nested)

        assert invalid_sales_event.body.customer.email_valid is False
