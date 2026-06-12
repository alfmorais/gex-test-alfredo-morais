from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities.lead_dead_letter import LeadDeadLetter
from src.infrastructure.database.mysql_lead_dead_letter import (
    LeadDeadLetterRepositorySQLModel,
)


class TestLeadDeadLetterRepositorySQLModel:
    @pytest.fixture
    def session(self):
        session = MagicMock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        return session

    @pytest.fixture
    def repository(self, session):
        return LeadDeadLetterRepositorySQLModel(session)

    @pytest.mark.asyncio
    async def test_should_create_dead_letter(
        self,
        repository,
        session,
    ):
        dead_letter = LeadDeadLetter(
            source_queue="orders",
            payload={"order_id": 123},
            error_message="Webhook timeout",
        )

        result = await repository.create(dead_letter)

        session.add.assert_called_once_with(dead_letter)
        session.commit.assert_awaited_once()
        session.refresh.assert_awaited_once_with(dead_letter)

        assert result == dead_letter

    @pytest.mark.asyncio
    async def test_should_raise_exception_when_commit_fails(self):
        session = MagicMock()
        session.commit = AsyncMock(side_effect=Exception("Database error"))
        session.refresh = AsyncMock()

        repository = LeadDeadLetterRepositorySQLModel(session)

        dead_letter = LeadDeadLetter(
            source_queue="orders",
            payload={"order_id": 123},
            error_message="Webhook timeout",
        )

        with pytest.raises(Exception, match="Database error"):
            await repository.create(dead_letter)

        session.add.assert_called_once_with(dead_letter)
        session.commit.assert_awaited_once()
        session.refresh.assert_not_awaited()
