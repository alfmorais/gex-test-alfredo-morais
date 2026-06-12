from fastapi import APIRouter, Request, Response

from src.controllers.event_sales_controller import EventSalesController
from src.controllers.services.event_sales.grummer_service import (
    GrummerEventSalesService,
)
from src.controllers.services.event_sales.lous_service import (
    LousEventSalesService,
)
from src.models.database.config import get_session
from src.models.queue.publisher_event import RabbitPublisher
from src.models.repositories.raw_payload_repository import RawPayloadRepository
from src.views.enum.gateways import Gateway
from src.views.schemas.sales_event_context import SalesEventContext

webhook_router = APIRouter(prefix="/webhook", tags=["Webhook"])


@webhook_router.post("/{gateway}")
async def receive_webhook(
    request: Request, gateway: Gateway, body: dict
) -> Response:
    context = SalesEventContext(
        correlation_id=request.state.correlation_id,
        gateway=gateway.value,
        headers=dict(request.headers),
        original_body=body,
    )
    async with get_session(request.app.state.engine) as session:
        repository = RawPayloadRepository(session=session)
        publisher = RabbitPublisher()
        gateway_strategy_services = {
            Gateway.GRUMMER.value: GrummerEventSalesService,
            Gateway.LOUS.value: LousEventSalesService,
        }
        gateway_service = gateway_strategy_services[gateway.value](
            repository=repository,
            publisher=publisher,
        )
        controller = EventSalesController(service=gateway_service)
        return await controller.execute(context=context)
