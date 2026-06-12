from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from src.controllers.services.event_sales.grummer_service import (
    GrummerEventSalesService,
)
from src.views.schemas.sales_event_context import SalesEventContext


class TestGrummerEventSalesService:
    @pytest.fixture
    def repository(self):
        return AsyncMock()

    @pytest.fixture
    def publisher(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, repository, publisher):
        return GrummerEventSalesService(
            repository=repository,
            publisher=publisher,
        )

    @pytest.fixture
    def context(self):
        return SalesEventContext(
            correlation_id="corr-id",
            gateway="grummer",
            headers={
                "Content-Type": "application/json",
                "X-GR-Encrypted": "true",
            },
            original_body={
                "body": {
                    "iv": "aXY=",
                    "ciphertext": "Y2lwaGVy",
                }
            },
        )

    @pytest.mark.asyncio
    async def test_decrypt_event_validation_error(
        self,
        service,
        context,
    ):
        validation_error = ValidationError.from_exception_data(
            "EncryptedSalesEvent",
            [
                {
                    "type": "missing",
                    "loc": ("body", "iv"),
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
            ".grummer_service"
            ".EncryptedSalesEvent"
            ".model_validate"
        )

        with patch(path, side_effect=validation_error):
            result = await service.decrypt_event(context)

        assert result.decrypt_failed is True
        assert len(result.validation_errors) == 1

    @pytest.mark.asyncio
    async def test_decrypt_event_success(
        self,
        service,
        context,
    ):
        validated_body = MagicMock()
        validated_body.body.iv = "aXY="
        validated_body.body.ciphertext = "Y2lwaGVy"

        plaintext = b'{"transaction_id":"123","event":"approved"}'

        decryptor = MagicMock()
        decryptor.update.return_value = b"padded"
        decryptor.finalize.return_value = b""

        unpadder = MagicMock()
        unpadder.update.return_value = plaintext
        unpadder.finalize.return_value = b""

        cipher = MagicMock()
        cipher.decryptor.return_value = decryptor

        model_path = (
            "src"
            ".controllers"
            ".services"
            ".event_sales"
            ".grummer_service"
            ".EncryptedSalesEvent"
            ".model_validate"
        )

        base_path = "src.controllers.services.event_sales.grummer_service"

        ciper_path = f"{base_path}.Cipher"
        pkcs7_path = f"{base_path}.PKCS7"

        with (
            patch(model_path, return_value=validated_body),
            patch(ciper_path, return_value=cipher),
            patch(pkcs7_path) as pkcs7_mock,
        ):
            pkcs7_mock.return_value.unpadder.return_value = unpadder

            result = await service.decrypt_event(context)

        assert result.decrypt_failed is False
        assert result.decrypted_body == {
            "transaction_id": "123",
            "event": "approved",
        }

    @pytest.mark.asyncio
    async def test_decrypt_event_crypto_error(
        self,
        service,
        context,
    ):
        validated_body = MagicMock()
        validated_body.body.iv = "aXY="
        validated_body.body.ciphertext = "Y2lwaGVy"

        model_path = (
            "src"
            ".controllers"
            ".services"
            ".event_sales"
            ".grummer_service"
            ".EncryptedSalesEvent"
            ".model_validate"
        )

        base_path = "src.controllers.services.event_sales.grummer_service"
        ciper_path = f"{base_path}.Cipher"

        with (
            patch(model_path, return_value=validated_body),
            patch(ciper_path, side_effect=Exception("invalid key")),
        ):
            result = await service.decrypt_event(context)

        assert result.decrypt_failed is True
        assert "invalid key" in result.validation_errors[0]
