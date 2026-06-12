import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine

from src.application.messages.distribution_message import DistributionMessage
from src.application.use_cases.process_distribution import (
    ProcessDistributionUseCase,
)
from src.domain.enum.queue_name import QueueName
from src.domain.publishers.rabbitmq_consumer import RabbitMQConsumer
from src.domain.publishers.rabbitmq_publisher import RabbitMQPublisher
from src.infrastructure.database.engine import get_session
from src.infrastructure.database.mysql_distribution_status import (
    DistributionStatusRepositorySQLModel,
)
from src.infrastructure.database.mysql_lead_dead_letter import (
    LeadDeadLetterRepositorySQLModel,
)
from src.infrastructure.integrations.webhook_site import WebhookSiteIntegration
from src.infrastructure.log.logger import app_logger as logger
from src.settings import settings


class DistributionWorker:
    def __init__(
        self,
        consumer: RabbitMQConsumer,
        publisher: RabbitMQPublisher,
        engine: AsyncEngine,
    ):
        self.consumer = consumer
        self.publisher = publisher
        self.engine = engine

    async def start(self) -> None:
        await self.consumer.consume(
            queue_name=QueueName.DIST_SMS.value, callback=self.handle
        )

    async def handle(self, payload: dict) -> None:
        last_error = None
        message = DistributionMessage.from_dict(payload)

        for delay in [1, 4, 16]:
            try:
                async with get_session(self.engine) as session:
                    repository = DistributionStatusRepositorySQLModel(session)
                    dead_letter_repository = LeadDeadLetterRepositorySQLModel(
                        session
                    )

                    integration = WebhookSiteIntegration(
                        url=settings.WEBHOOK_URL
                    )

                    use_case = ProcessDistributionUseCase(
                        integration=integration,
                        publisher=self.publisher,
                        repository=repository,
                        dead_letter_repository=dead_letter_repository,
                    )

                    await use_case.execute(message)
                    return

            except Exception as exc:
                logger.info(f"Error: {exc}")
                last_error = exc

                await asyncio.sleep(delay)

        await self.publisher.publish(
            QueueName.DIST_DEAD_SMS.value,
            {
                "payload": payload,
                "error": str(last_error),
            },
        )
        return
