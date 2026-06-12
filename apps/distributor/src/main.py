import asyncio

import src.domain.entities  # noqa: F401
from src.infrastructure.database.engine import create_engine
from src.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from src.infrastructure.messaging.rabbitmq_publisher import RabbitMQPublisher
from src.workers.distribution_worker import DistributionWorker


async def main() -> None:
    consumer = RabbitMQConsumer()

    publisher = RabbitMQPublisher()

    engine = create_engine()

    worker = DistributionWorker(
        consumer=consumer,
        publisher=publisher,
        engine=engine,
    )

    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
