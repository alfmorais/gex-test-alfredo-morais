from unittest.mock import AsyncMock, MagicMock

import pytest

from src.infrastructure.database.mysql_distribution_repository import (
    MySQLDistributionRepository,
)


class TestMySQLDistributionRepository:
    def setup_method(self) -> None:
        self.session = MagicMock()
        self.session.flush = AsyncMock()
        self.session.commit = AsyncMock()

        self.repository = MySQLDistributionRepository(
            session=self.session,
        )

    @pytest.mark.asyncio
    async def test_should_bulk_create_distributions(
        self,
    ) -> None:
        distributions = [
            MagicMock(),
            MagicMock(),
        ]

        result = await self.repository.bulk_create(
            distributions,
        )

        self.session.add_all.assert_called_once_with(
            distributions,
        )
        self.session.flush.assert_awaited_once()
        self.session.commit.assert_awaited_once()

        assert result is None

    @pytest.mark.asyncio
    async def test_should_bulk_create_empty_list(
        self,
    ) -> None:
        distributions: list = []

        result = await self.repository.bulk_create(
            distributions,
        )

        self.session.add_all.assert_called_once_with(
            distributions,
        )
        self.session.flush.assert_awaited_once()
        self.session.commit.assert_awaited_once()

        assert result is None

    @pytest.mark.asyncio
    async def test_should_propagate_flush_exception(
        self,
    ) -> None:
        self.session.flush.side_effect = RuntimeError(
            "database error",
        )

        with pytest.raises(
            RuntimeError,
            match="database error",
        ):
            await self.repository.bulk_create(
                [MagicMock()],
            )

        self.session.add_all.assert_called_once()
        self.session.flush.assert_awaited_once()
