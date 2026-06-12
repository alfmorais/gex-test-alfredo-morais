from http import HTTPStatus

import httpx

from src.infrastructure.log.logger import app_logger as logger


class WebhookSiteIntegration:
    def __init__(self, url: str) -> None:
        self.url = url

    async def make_request(self, correlation_id: str) -> bool:
        logger.info(
            f"[CorrelationID: {correlation_id}] - "
            f"Sent webhook request to {self.url}"
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.url)

            logger.info(
                f"[CorrelationID: {correlation_id}] - "
                f"STATUS_CODE={response.status_code}"
            )

            return True if response.status_code == HTTPStatus.OK else False
