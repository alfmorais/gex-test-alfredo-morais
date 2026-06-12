from typing import Protocol


class RabbitMQPublisher(Protocol):
    async def publish(self, queue_name: str, payload: dict) -> bool: ...
