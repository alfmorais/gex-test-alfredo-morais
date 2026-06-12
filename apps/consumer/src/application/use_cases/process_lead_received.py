from datetime import UTC, datetime

from src.application.messages.lead_received_message import (
    LeadReceivedMessage,
)
from src.domain.entities.distribution_status import (
    DistributionStatus,
    DistributionStatusModel,
)
from src.domain.enum.distribution_channel import CHANNEL_QUEUES
from src.domain.publishers.rabbitmq_publisher import RabbitMQPublisher
from src.domain.repositories.distribution_repository import (
    DistributionRepository,
)
from src.domain.repositories.lead_repository import LeadRepository
from src.infrastructure.log.logger import app_logger as logger


class ProcessLeadReceivedUseCase:
    def __init__(
        self,
        lead_repository: LeadRepository,
        distribution_repository: DistributionRepository,
        publisher: RabbitMQPublisher,
    ):
        self.lead_repository = lead_repository
        self.distribution_repository = distribution_repository
        self.publisher = publisher

    async def execute(self, message: LeadReceivedMessage) -> None:
        logger.info(f"[CorrelationID: {message.correlation_id}] Start Lead")

        lead_id, order_id = await self.call_store_procedure(message)

        await self.create_distribution(message, order_id)

        await self.publish_event(message, order_id, lead_id)

    async def call_store_procedure(
        self, message: LeadReceivedMessage
    ) -> tuple[int, int]:
        logger.info(f"[CorrelationID: {message.correlation_id}] Calling SP")

        lag = datetime.now(UTC) - message.body.transaction_time
        lag_in_seconds = int(lag.total_seconds())

        lead_id, order_id = await self.lead_repository.insert_lead(
            message=message,
            lag_seconds=lag_in_seconds,
        )

        logger.info(
            f"[CorrelationID: {message.correlation_id}] "
            f"Returning lead ID: {lead_id} and order ID: {order_id}"
        )
        return lead_id, order_id

    async def create_distribution(
        self,
        message: LeadReceivedMessage,
        order_id: int,
    ) -> None:
        correlation_id = message.correlation_id
        logger.info(f"[CorrelationID: {correlation_id}] Creating distribution")

        channels = ["SMS", "EMAIL", "CALL_CENTER", "WHATSAPP"]

        distributions_objects = [
            DistributionStatusModel(
                order_id=order_id,
                channel=channel,
                status=DistributionStatus.PENDING.value,
                lag_seconds=0,
            )
            for channel in channels
        ]

        await self.distribution_repository.bulk_create(distributions_objects)

        logger.info(f"[CorrelationID: {correlation_id}] Distribution created")

    async def publish_event(
        self,
        message: LeadReceivedMessage,
        order_id: int,
        lead_id: int,
    ) -> None:
        logger.info(f"[CorrelationID: {message.correlation_id}] Publishing")

        for channel, routing_key in CHANNEL_QUEUES.items():
            logger.info(
                f"[CorrelationID: {message.correlation_id}] "
                f"Publishing to {routing_key} channel"
            )

            payload = {
                "order_id": order_id,
                "lead_id": lead_id,
                "channel": channel.value,
                "phone": message.body.customer.phone,
                "correlation_id": message.correlation_id,
            }
            await self.publisher.publish(routing_key, payload)
