import asyncio

from src.application.messages.lead_received_message import LeadReceivedMessage
from src.application.use_cases.process_lead_received import (
    ProcessLeadReceivedUseCase,
)
from src.domain.enum.queue_name import QueueName
from src.domain.publishers.rabbitmq_consumer import RabbitMQConsumer
from src.domain.publishers.rabbitmq_publisher import RabbitMQPublisher


class LeadReceivedWorker:
    def __init__(
        self,
        consumer: RabbitMQConsumer,
        use_case: ProcessLeadReceivedUseCase,
        publisher: RabbitMQPublisher,
    ):
        self.consumer = consumer
        self.use_case = use_case
        self.publisher = publisher

    async def start(self) -> None:
        await self.consumer.consume(
            queue_name=QueueName.LEAD_RECEIVED.value, callback=self.handle
        )

    async def handle(self, payload: dict) -> None:
        last_error = None

        try:
            message = LeadReceivedMessage.from_dict(payload)
        except Exception as exc:
            await self.publisher.publish(
                QueueName.LEAD_DEAD_CONSUMER_FAILED.value,
                {
                    "payload": payload,
                    "error": f"invalid message format: {str(exc)}",
                },
            )
            return

        for delay in [1, 4, 16]:
            try:
                await self.use_case.execute(message)
                return

            except Exception as exc:
                last_error = exc

                await asyncio.sleep(delay)

        await self.publisher.publish(
            QueueName.LEAD_DEAD_CONSUMER_FAILED.value,
            {
                "payload": payload,
                "error": str(last_error),
            },
        )
