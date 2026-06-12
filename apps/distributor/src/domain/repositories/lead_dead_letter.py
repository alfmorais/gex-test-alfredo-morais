from typing import Protocol

from src.domain.entities.lead_dead_letter import LeadDeadLetter


class LeadDeadLetterRepository(Protocol):
    async def create(
        self,
        dead_letter: LeadDeadLetter,
    ) -> LeadDeadLetter: ...
