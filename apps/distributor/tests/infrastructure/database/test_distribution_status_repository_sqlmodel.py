from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities.distribution_status import DistributionStatusModel
from src.infrastructure.database.mysql_distribution_status import (
    DistributionStatusRepositorySQLModel,
)


class TestDistributionStatusRepositorySQLModel:
    def setup_method(self) -> None:
        self.session = MagicMock()
        self.session.execute = AsyncMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        self.session.add = MagicMock()

        self.repository = DistributionStatusRepositorySQLModel(
            session=self.session,
        )

        self.distribution = DistributionStatusModel(
            order_id=10,
            channel="SMS",
            status="PENDING",
        )

    @pytest.mark.asyncio
    async def test_should_get_distribution_by_order_id_and_channel(
        self,
    ) -> None:
        result_proxy = MagicMock()
        result_proxy.scalar_one_or_none.return_value = self.distribution

        self.session.execute.return_value = result_proxy

        result = await self.repository.get_by_order_id_and_channel(
            order_id=10,
            channel="SMS",
        )

        assert result == self.distribution

        self.session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_return_none_when_not_found(
        self,
    ) -> None:
        result_proxy = MagicMock()
        result_proxy.scalar_one_or_none.return_value = None

        self.session.execute.return_value = result_proxy

        result = await self.repository.get_by_order_id_and_channel(
            order_id=10,
            channel="SMS",
        )

        assert result is None

        self.session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_update_and_return_distribution(
        self,
    ) -> None:
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await self.repository.update(self.distribution)

        self.session.add.assert_called_once_with(self.distribution)
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(self.distribution)

        assert result == self.distribution

    @pytest.mark.asyncio
    async def test_should_propagate_commit_exception(
        self,
    ) -> None:
        self.session.commit = AsyncMock(
            side_effect=RuntimeError("commit error")
        )

        with pytest.raises(RuntimeError, match="commit error"):
            await self.repository.update(self.distribution)

        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
