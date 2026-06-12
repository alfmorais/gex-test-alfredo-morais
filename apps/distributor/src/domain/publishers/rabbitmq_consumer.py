from collections.abc import Awaitable, Callable
from typing import Any, Protocol

MessageHandler = Callable[
    [dict[str, Any]],
    Awaitable[None],
]


class RabbitMQConsumer(Protocol):
    async def consume(
        self,
        queue_name: str,
        callback: MessageHandler,
    ) -> None: ...
