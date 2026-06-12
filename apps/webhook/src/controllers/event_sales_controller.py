from fastapi import Response, status
from fastapi.responses import JSONResponse

from src.controllers.interfaces.event_sales_interface import (
    EventSalesInterface,
)
from src.logger import app_logger as logger
from src.views.enum.queues import Queues
from src.views.schemas.sales_event_context import SalesEventContext


class EventSalesController:
    def __init__(self, service: EventSalesInterface) -> None:
        self._service = service

    async def execute(
        self, context: SalesEventContext
    ) -> Response | JSONResponse:
        logger.info(
            f"[CorrelationID: {context.correlation_id}] - "
            f"Received event for gateway: {context.gateway}"
        )

        context = await self._service.decrypt_event(context)

        if context.decrypt_failed:
            return await self._handle_decrypt_failed(context)

        context = await self._service.validate_event(context)

        if not context.schema_valid:
            return await self._handle_schema_validation_failed(context)

        context = await self._service.check_idempotency(context)

        if context.duplicate:
            return await self._handle_duplicate_event(context)

        logger.info(
            f"[CorrelationID: {context.correlation_id}] - "
            f"Event passed decryption, validation, and idempotency checks"
        )
        await self._service.save_event(context)

        logger.info(
            f"[CorrelationID: {context.correlation_id}] - "
            f"Event saved successfully, proceeding to publish if criteria met"
        )
        return await self._handle_lead_received(context)

    async def _handle_decrypt_failed(
        self,
        context: SalesEventContext,
    ) -> Response:
        logger.info(
            f"[CorrelationID: {context.correlation_id}] - Decryption failed"
        )

        await self._service.save_event(context)

        payload = {
            "errors": context.validation_errors,
            "correlation_id": context.correlation_id,
        }

        await self._service.publish_event(
            queue_name=Queues.DECRYPT_FAILED.value,
            payload=payload,
        )

        return Response(status_code=status.HTTP_200_OK)

    async def _handle_schema_validation_failed(
        self,
        context: SalesEventContext,
    ) -> Response:
        logger.info(
            f"[CorrelationID: {context.correlation_id}] - "
            f"Schema validation failed"
        )

        await self._service.save_event(context)

        payload = {
            "errors": context.validation_errors,
            "correlation_id": context.correlation_id,
        }

        await self._service.publish_event(
            queue_name=Queues.SCHEMA_FAILED.value,
            payload=payload,
        )

        return Response(status_code=status.HTTP_200_OK)

    async def _handle_duplicate_event(
        self, context: SalesEventContext
    ) -> JSONResponse:
        logger.info(
            f"[CorrelationID: {context.correlation_id}] - "
            f"Duplicate event detected"
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "duplicate"},
        )

    async def _handle_lead_received(
        self, context: SalesEventContext
    ) -> Response:
        logger.info(
            f"[CorrelationID: {context.correlation_id}] - Lead received"
        )

        payload = context.validated_body

        if payload is None:
            return Response(status_code=status.HTTP_200_OK)

        if (
            context.schema_valid
            and payload.body.event == "order.approved"
            and payload.body.payment.status == "approved"
        ):
            logger.info(
                f"[CorrelationID: {context.correlation_id}] - "
                f"Publishing lead received event"
            )

            event_payload = payload.model_dump(mode="json")
            event_payload["correlation_id"] = context.correlation_id

            await self._service.publish_event(
                queue_name=Queues.RECEIVED.value,
                payload=event_payload,
            )

            return Response(status_code=status.HTTP_200_OK)

        logger.info(
            f"[CorrelationID: {context.correlation_id}] - "
            f"Event not meeting criteria for lead publishing"
        )
        return Response(status_code=status.HTTP_200_OK)
