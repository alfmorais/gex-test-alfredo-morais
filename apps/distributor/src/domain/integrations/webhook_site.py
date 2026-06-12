from typing import Protocol


class WebhookSiteIntegration(Protocol):
    async def make_request(self, correlation_id: str) -> bool: ...
