from abc import ABC, abstractmethod

from src.views.schemas.sales_event_context import SalesEventContext


class EventSalesInterface(ABC):
    @abstractmethod
    async def decrypt_event(
        self, context: SalesEventContext
    ) -> SalesEventContext: ...

    @abstractmethod
    async def validate_event(
        self, context: SalesEventContext
    ) -> SalesEventContext: ...

    @abstractmethod
    async def check_idempotency(
        self, context: SalesEventContext
    ) -> SalesEventContext: ...

    @abstractmethod
    async def save_event(self, context: SalesEventContext) -> bool: ...

    @abstractmethod
    async def publish_event(self, queue_name: str, payload: dict) -> bool: ...
