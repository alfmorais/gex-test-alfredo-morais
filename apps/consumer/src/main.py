import asyncio

import src.domain.entities  # noqa: F401
from src.application.use_cases.process_lead_received import (
    ProcessLeadReceivedUseCase,
)
from src.infrastructure.database.engine import create_engine, get_session
from src.infrastructure.database.mysql_distribution_repository import (
    MySQLDistributionRepository,
)
from src.infrastructure.database.mysql_lead_repository import (
    MySQLLeadRepository,
)
from src.infrastructure.messaging.rabbitmq_consumer import (
    RabbitMQConsumer,
)
from src.infrastructure.messaging.rabbitmq_publisher import (
    RabbitMQPublisher,
)
from src.workers.consumer_worker import (
    LeadReceivedWorker,
)


async def main() -> None:
    engine = create_engine()

    async with get_session(engine) as session:
        consumer = RabbitMQConsumer()
        publisher = RabbitMQPublisher()

        lead_repository = MySQLLeadRepository(session)
        distribution_repository = MySQLDistributionRepository(session)

        use_case = ProcessLeadReceivedUseCase(
            lead_repository=lead_repository,
            distribution_repository=distribution_repository,
            publisher=publisher,
        )

        worker = LeadReceivedWorker(
            consumer=consumer,
            publisher=publisher,
            use_case=use_case,
        )

        await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
