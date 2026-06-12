from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.lead_dead_letter import LeadDeadLetter


class LeadDeadLetterRepositorySQLModel:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        dead_letter: LeadDeadLetter,
    ) -> LeadDeadLetter:
        self._session.add(dead_letter)

        await self._session.commit()
        await self._session.refresh(dead_letter)

        return dead_letter
