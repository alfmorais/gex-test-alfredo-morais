import json
from base64 import b64decode

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from pydantic import ValidationError

from src.controllers.services.event_sales.base_service import (
    EventSalesBaseService,
)
from src.settings import settings
from src.views.schemas.sales_event import EncryptedSalesEvent
from src.views.schemas.sales_event_context import SalesEventContext


class GrummerEventSalesService(EventSalesBaseService):
    async def decrypt_event(
        self, context: SalesEventContext
    ) -> SalesEventContext:
        validated_body = None
        body = {
            "body": context.original_body["body"],
            "headers": context.headers,
            "gateway": context.gateway,
        }

        try:
            validated_body = EncryptedSalesEvent.model_validate(body)
        except ValidationError as error:
            context.decrypt_failed = True
            context.validation_errors.append(error.errors())
            return context

        try:
            iv = b64decode(validated_body.body.iv)
            ciphertext = b64decode(validated_body.body.ciphertext)
            key = bytes.fromhex(settings.GRUMER_SECRET_KEY)

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

            decryptor = cipher.decryptor()
            padded = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = PKCS7(128).unpadder()
            plaintext = unpadder.update(padded) + unpadder.finalize()
            context.decrypted_body = json.loads(plaintext.decode("utf-8"))
        except Exception as error:
            context.decrypt_failed = True
            context.validation_errors.append(str(error))
        return context
