import json
from collections.abc import Awaitable, Callable
from typing import Any

import aio_pika

from src.settings import settings

MessageHandler = Callable[
    [dict[str, Any]],
    Awaitable[None],
]


class RabbitMQConsumer:
    async def consume(self, queue_name: str, callback: MessageHandler) -> None:
        rabbitmq_connection = (
            f"amqp://"
            f"{settings.RABBITMQ_USER}:"
            f"{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}/"
        )

        connection = await aio_pika.connect_robust(rabbitmq_connection)

        channel = await connection.channel()

        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as iterator:
            async for message in iterator:
                async with message.process():
                    payload = json.loads(message.body.decode())
                    await callback(payload)
