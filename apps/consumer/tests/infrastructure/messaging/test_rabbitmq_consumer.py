import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.messaging.rabbitmq_consumer import (
    RabbitMQConsumer,
)


class MockProcessContext:
    async def __aenter__(self):
        return None

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        return None


class MockMessage:
    def __init__(self, payload: dict) -> None:
        self.body = json.dumps(payload).encode()

    def process(self) -> MockProcessContext:
        return MockProcessContext()


class MockQueueIterator:
    def __init__(
        self,
        messages: list[MockMessage],
    ) -> None:
        self.messages = messages

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):
        return None

    def __aiter__(self):
        async def generator():
            for message in self.messages:
                yield message

        return generator()


class TestRabbitMQConsumer:
    def setup_method(self) -> None:
        self.consumer = RabbitMQConsumer()

    @pytest.mark.asyncio
    async def test_should_consume_message_and_call_callback(
        self,
    ) -> None:
        payload = {
            "lead_id": 1,
            "order_id": 10,
        }

        callback = AsyncMock()

        queue = MagicMock()
        queue.iterator.return_value = MockQueueIterator([MockMessage(payload)])

        channel = AsyncMock()
        channel.declare_queue.return_value = queue

        connection = AsyncMock()
        connection.channel.return_value = channel

        with patch(
            "src.infrastructure.messaging.rabbitmq_consumer."
            "aio_pika.connect_robust",
            AsyncMock(return_value=connection),
        ):
            await self.consumer.consume(
                queue_name="lead.received",
                callback=callback,
            )

        callback.assert_awaited_once_with(payload)

        channel.declare_queue.assert_awaited_once_with(
            "lead.received",
            durable=True,
        )

    @pytest.mark.asyncio
    async def test_should_process_multiple_messages(
        self,
    ) -> None:
        callback = AsyncMock()

        payloads = [
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ]

        queue = MagicMock()
        queue.iterator.return_value = MockQueueIterator([
            MockMessage(payload) for payload in payloads
        ])

        channel = AsyncMock()
        channel.declare_queue.return_value = queue

        connection = AsyncMock()
        connection.channel.return_value = channel

        with patch(
            "src.infrastructure.messaging.rabbitmq_consumer."
            "aio_pika.connect_robust",
            AsyncMock(return_value=connection),
        ):
            await self.consumer.consume(
                queue_name="queue",
                callback=callback,
            )

        assert callback.await_count == 3

    @pytest.mark.asyncio
    async def test_should_create_connection(
        self,
    ) -> None:
        callback = AsyncMock()

        queue = MagicMock()
        queue.iterator.return_value = MockQueueIterator([])

        channel = AsyncMock()
        channel.declare_queue.return_value = queue

        connection = AsyncMock()
        connection.channel.return_value = channel

        connect_mock = AsyncMock(
            return_value=connection,
        )

        with patch(
            "src.infrastructure.messaging.rabbitmq_consumer."
            "aio_pika.connect_robust",
            connect_mock,
        ):
            await self.consumer.consume(
                queue_name="queue",
                callback=callback,
            )

        connect_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_propagate_callback_exception(
        self,
    ) -> None:
        callback = AsyncMock(
            side_effect=RuntimeError(
                "callback error",
            )
        )

        queue = MagicMock()
        queue.iterator.return_value = MockQueueIterator([
            MockMessage(
                {"id": 1},
            )
        ])

        channel = AsyncMock()
        channel.declare_queue.return_value = queue

        connection = AsyncMock()
        connection.channel.return_value = channel

        with patch(
            "src.infrastructure.messaging.rabbitmq_consumer."
            "aio_pika.connect_robust",
            AsyncMock(return_value=connection),
        ):
            with pytest.raises(
                RuntimeError,
                match="callback error",
            ):
                await self.consumer.consume(
                    queue_name="queue",
                    callback=callback,
                )
