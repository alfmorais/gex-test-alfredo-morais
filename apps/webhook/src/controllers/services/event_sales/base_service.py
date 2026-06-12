import json

from pydantic import ValidationError

from src.controllers.interfaces.event_sales_interface import (
    EventSalesInterface,
)
from src.models.entities.raw_payload import RawPayload
from src.models.queue.publisher_event import RabbitPublisher
from src.models.repositories.raw_payload_repository import (
    RawPayloadRepository,
)
from src.views.schemas.sales_event import SalesEvent
from src.views.schemas.sales_event_context import SalesEventContext


class EventSalesBaseService(EventSalesInterface):
    def __init__(
        self, repository: RawPayloadRepository, publisher: RabbitPublisher
    ) -> None:
        self._repository = repository
        self._publisher = publisher

    async def check_idempotency(
        self, context: SalesEventContext
    ) -> SalesEventContext:
        idempotency_key = (
            context.validated_body.body.idempotency_key
            if context.validated_body
            else None
        )
        if idempotency_key:
            instance_exists = await self._repository.exists(idempotency_key)

            if instance_exists:
                context.duplicate = True
                return context

        context.duplicate = False
        return context

    async def save_event(self, context: SalesEventContext) -> bool:
        idempotency_key = (
            context.validated_body.body.idempotency_key
            if context.validated_body
            else None
        )

        decrypted_body = (
            json.dumps(context.decrypted_body)
            if context.decrypted_body
            else {}
        )
        event = (
            context.validated_body.body.event
            if context.validated_body
            else None
        )
        transaction_id = (
            context.validated_body.body.transaction_id
            if context.validated_body
            else None
        )

        raw_payload_object = RawPayload(
            transaction_id=transaction_id,
            event=event,
            idempotency_key=idempotency_key,
            correlation_id=context.correlation_id,
            gateway=context.gateway,
            headers=json.dumps(context.headers),
            body=json.dumps(context.original_body),
            decrypted_body=decrypted_body,
            raw_payload=json.dumps(context.original_body),
        )
        return await self._repository.save(raw_payload_object)

    async def publish_event(self, queue_name: str, payload: dict) -> bool:
        await self._publisher.publish(queue_name=queue_name, payload=payload)
        return True

    async def validate_event(
        self, context: SalesEventContext
    ) -> SalesEventContext:
        body = {
            "headers": context.headers,
            "gateway": context.gateway,
            "body": context.decrypted_body,
        }

        try:
            validated_body = SalesEvent.model_validate(body)
            context.validated_body = validated_body
            context.schema_valid = True
        except ValidationError as error:
            context.validation_errors.append(error.errors())
            context.schema_valid = False
        return context
