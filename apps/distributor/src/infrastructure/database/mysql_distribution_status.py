from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.domain.entities.distribution_status import (
    DistributionStatusModel,
)
from src.infrastructure.log.logger import app_logger as logger


class DistributionStatusRepositorySQLModel:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_by_order_id_and_channel(
        self,
        order_id: int,
        channel: str,
    ) -> DistributionStatusModel | None:
        logger.info(
            f"SessionId: {id(self._session)} "
            f"order_id={order_id} "
            f"channel={channel}"
        )
        statement = select(DistributionStatusModel).where(
            DistributionStatusModel.order_id == order_id,
            DistributionStatusModel.channel == channel,
        )
        result = await self._session.execute(statement)
        logger.info(f"result: {result}")

        data = result.scalar_one_or_none()
        logger.info(f"data: {data}")

        return data

    async def update(
        self,
        distribution_status: DistributionStatusModel,
    ) -> DistributionStatusModel:
        self._session.add(distribution_status)
        await self._session.commit()
        await self._session.refresh(distribution_status)

        return distribution_status
