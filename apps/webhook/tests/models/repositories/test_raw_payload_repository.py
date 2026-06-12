from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.models.entities.raw_payload import RawPayload
from src.models.repositories.raw_payload_repository import (
    RawPayloadRepository,
)


class TestRawPayloadRepository:
    @pytest.fixture
    def session(self):
        session = MagicMock()

        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.execute = AsyncMock()

        return session

    @pytest.fixture
    def repository(self, session):
        return RawPayloadRepository(session=session)

    @pytest.mark.asyncio
    async def test_save_success(
        self,
        repository,
        session,
    ):
        raw_payload = MagicMock(spec=RawPayload)

        result = await repository.save(raw_payload)

        assert result is True

        session.add.assert_called_once_with(raw_payload)
        session.commit.assert_awaited_once()
        session.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_integrity_error(
        self,
        repository,
        session,
    ):
        raw_payload = MagicMock(spec=RawPayload)

        session.commit.side_effect = IntegrityError(
            statement="INSERT",
            params={},
            orig=Exception(),
        )

        result = await repository.save(raw_payload)

        assert result is False

        session.add.assert_called_once_with(raw_payload)
        session.commit.assert_awaited_once()
        session.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exists_returns_true(
        self,
        repository,
        session,
    ):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = object()

        session.execute.return_value = result_mock

        result = await repository.exists("idem-123")

        assert result is True

        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exists_returns_false(
        self,
        repository,
        session,
    ):
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None

        session.execute.return_value = result_mock

        result = await repository.exists("idem-123")

        assert result is False

        session.execute.assert_awaited_once()
