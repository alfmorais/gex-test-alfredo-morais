import json
from typing import Any

from aio_pika import (
    DeliveryMode,
    Message,
    connect_robust,
)
from aio_pika.abc import AbstractChannel, AbstractRobustConnection

from src.settings import settings


class RabbitPublisher:
    def __init__(self) -> None:
        self.url: str = (
            f"amqp://{settings.RABBITMQ_USER}:"
            f"{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}/"
        )

        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None

    async def _connect(self) -> None:
        if self.connection and not self.connection.is_closed:
            return

        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()

    async def publish(
        self,
        queue_name: str,
        payload: dict[str, Any],
    ) -> bool:
        await self._connect()

        if self.channel is None:
            raise RuntimeError("RabbitMQ channel not initialized")

        await self.channel.declare_queue(
            queue_name,
            durable=True,
        )

        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(payload).encode("utf-8"),
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )

        await self._close()

        return True

    async def _close(self) -> None:
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
