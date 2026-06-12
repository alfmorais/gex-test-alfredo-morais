import json
import random
from dataclasses import asdict
from datetime import UTC, datetime
from typing import Optional

from src.application.messages.distribution_message import DistributionMessage
from src.domain.entities.distribution_status import (
    DistributionStatus,
    DistributionStatusModel,
)
from src.domain.entities.lead_dead_letter import LeadDeadLetter
from src.domain.enum.queue_name import QueueName
from src.domain.exceptions.distribution_not_found import (
    DistributionNotFoundError,
)
from src.domain.integrations.webhook_site import WebhookSiteIntegration
from src.domain.publishers.rabbitmq_publisher import RabbitMQPublisher
from src.domain.repositories.distribution_status import (
    DistributionStatusRepository,
)
from src.domain.repositories.lead_dead_letter import LeadDeadLetterRepository
from src.infrastructure.log.logger import app_logger as logger


class ProcessDistributionUseCase:
    def __init__(
        self,
        integration: WebhookSiteIntegration,
        publisher: RabbitMQPublisher,
        repository: DistributionStatusRepository,
        dead_letter_repository: LeadDeadLetterRepository,
    ) -> None:
        self.integration = integration
        self.publisher = publisher
        self.repository = repository
        self.dead_letter_repository = dead_letter_repository

    async def execute(self, data: DistributionMessage) -> None:
        logger.info(
            f"[CorrelationId: {data.correlation_id} "
            "Start process distribution]"
        )

        distribution_instance: (
            DistributionStatusModel | None
        ) = await self.get_distribution(
            order_id=data.order_id,
            channel=data.channel,
        )

        if not distribution_instance:
            logger.info(
                f"[CorrelationId: {data.correlation_id} "
                f"Distribution not found for order_id={data.order_id} "
                f"and channel={data.channel}]"
            )
            raise DistributionNotFoundError(
                order_id=data.order_id,
                channel=data.channel,
            )

        webhook_has_sent: bool = await self.send_webhook(data)

        if webhook_has_sent:
            logger.info(
                f"[CorrelationId: {data.correlation_id} "
                f"Webhook sent successfully order_id={data.order_id} "
                f"and channel={data.channel}]"
            )
            await self.update_distribution(
                distribution_instance,
                status=DistributionStatus.DELIVERED,
            )
            logger.info(f"[CorrelationId: {data.correlation_id} Finished")
            return None

        logger.info(
            f"[CorrelationId: {data.correlation_id} "
            f"Webhook not sent order_id={data.order_id} "
            f"and channel={data.channel}]"
        )
        await self.update_distribution(
            distribution_instance,
            status=DistributionStatus.FAILED,
        )
        await self.save_dead_letter(
            source_queue=QueueName.DIST_DEAD_SMS.value,
            payload=asdict(data),
            error_message="Webhook not sent",
        )
        await self.publish_event(
            queue_name=QueueName.DIST_DEAD_SMS.value,
            payload={
                "order_id": data.order_id,
                "channel": data.channel,
                "message": "Webhook not sent",
            },
        )
        return None

    async def get_distribution(
        self,
        order_id: int,
        channel: str,
    ) -> Optional[DistributionStatusModel] | None:
        logger.info(
            f"Get distribution by order_id={order_id} and channel={channel}]"
        )
        distribution_instance: (
            DistributionStatusModel | None
        ) = await self.repository.get_by_order_id_and_channel(
            order_id=order_id,
            channel=channel,
        )

        logger.info(f"distribution_instance={distribution_instance}]")
        return distribution_instance

    async def send_webhook(self, data: DistributionMessage) -> bool:
        logger.info("Start send webhook")
        if random.random() < 0.1:
            logger.info("Webhook not sent")
            return False

        logger.info("Webhook sent")
        return await self.integration.make_request(data.correlation_id)

    async def update_distribution(
        self,
        distribution_instance: DistributionStatusModel,
        status: DistributionStatus,
    ) -> None:
        logger.info(f"Update distribution Id: {distribution_instance.id}]")

        now = datetime.now(UTC)

        created_at = (
            distribution_instance.created_at.replace(tzinfo=UTC)
            if distribution_instance.created_at.tzinfo is None
            else distribution_instance.created_at
        )

        lag = now - created_at
        lag_seconds = int(lag.total_seconds())
        logger.info(f"lag_seconds={lag_seconds}]")

        distribution_instance.lag_seconds = lag_seconds
        distribution_instance.status = status
        distribution_instance.updated_at = now
        distribution_instance.delivered_at = now

        await self.repository.update(distribution_instance)
        logger.info(f"End update distribution Id: {distribution_instance.id}]")
        return

    async def save_dead_letter(
        self,
        source_queue: str,
        payload: dict,
        error_message: str,
    ) -> None:
        logger.info(
            f"Create LeadDeadLetter: "
            f"{source_queue}, {payload} and {error_message}"
        )

        dead_letter = LeadDeadLetter(
            source_queue=source_queue,
            payload=json.dumps(payload),
            error_message=error_message,
        )

        await self.dead_letter_repository.create(dead_letter)
        logger.info("Created LeadDeadLetter")
        return

    async def publish_event(self, queue_name: str, payload: dict) -> None:
        logger.info(f"Publish event to queue: {queue_name}]payload={payload}")
        await self.publisher.publish(queue_name, payload)
        return
