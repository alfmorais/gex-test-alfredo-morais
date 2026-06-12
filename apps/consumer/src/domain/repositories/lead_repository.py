from typing import Protocol

from src.application.messages.lead_received_message import LeadReceivedMessage


class LeadRepository(Protocol):
    async def insert_lead(
        self,
        message: LeadReceivedMessage,
        lag_seconds: int,
    ) -> tuple[int, int]:
        """
        Retorna:
            lead_id, order_id
        """
        ...
