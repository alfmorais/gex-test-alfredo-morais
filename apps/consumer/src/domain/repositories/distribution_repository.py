from typing import Protocol

from src.domain.entities.distribution_status import DistributionStatusModel


class DistributionRepository(Protocol):
    async def bulk_create(
        self, distributions: list[DistributionStatusModel]
    ) -> None: ...
