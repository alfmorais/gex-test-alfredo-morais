from src.controllers.services.event_sales.base_service import (
    EventSalesBaseService,
)
from src.views.schemas.sales_event_context import SalesEventContext


class LousEventSalesService(EventSalesBaseService):
    async def decrypt_event(
        self, context: SalesEventContext
    ) -> SalesEventContext:
        context.decrypted_body = context.original_body["body"]
        return context
