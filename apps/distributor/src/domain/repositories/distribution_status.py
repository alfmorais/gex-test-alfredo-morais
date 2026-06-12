from typing import Protocol

from src.domain.entities.distribution_status import (
    DistributionStatusModel,
)


class DistributionStatusRepository(Protocol):
    async def get_by_order_id_and_channel(
        self,
        order_id: int,
        channel: str,
    ) -> DistributionStatusModel | None: ...

    async def update(
        self,
        distribution_status: DistributionStatusModel,
    ) -> DistributionStatusModel: ...
