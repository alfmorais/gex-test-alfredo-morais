from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.distribution_status import DistributionStatusModel


class MySQLDistributionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def bulk_create(
        self, distributions: list[DistributionStatusModel]
    ) -> None:
        self._session.add_all(distributions)
        await self._session.flush()
        await self._session.commit()
