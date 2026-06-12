from enum import Enum

import pytest

from src.views.enum.queues import Queues


class TestQueuesEnum:
    @pytest.mark.asyncio
    async def test_queues_values(self):
        assert Queues.DECRYPT_FAILED.value == "lead.dead.decrypt_failed"
        assert Queues.SCHEMA_FAILED.value == "lead.dead.schema_failed"
        assert Queues.RECEIVED.value == "lead.received"

    @pytest.mark.asyncio
    async def test_queues_inheritance(self):
        assert isinstance(Queues.RECEIVED, str)
        assert isinstance(Queues.RECEIVED, Enum)

    @pytest.mark.asyncio
    async def test_queues_completeness(self):
        assert len(Queues) == 3, (
            "Devem existir exatamente 3 filas definidas no Enum"
        )

    @pytest.mark.asyncio
    async def test_queues_string_integrity(self):
        for queue in Queues:
            assert isinstance(queue.value, str)
            assert len(queue.value) > 0, (
                f"A fila {queue.name} possui valor vazio"
            )
