import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.messaging.rabbitmq_publisher import (
    RabbitMQPublisher,
)


class TestRabbitMQPublisher:
    def setup_method(self) -> None:
        self.publisher = RabbitMQPublisher()

    @pytest.mark.asyncio
    async def test_should_connect_when_connection_is_none(
        self,
    ) -> None:
        channel = AsyncMock()

        connection = AsyncMock()
        connection.is_closed = False
        connection.channel.return_value = channel

        with patch(
            "src.infrastructure.messaging.rabbitmq_publisher.connect_robust",
            AsyncMock(return_value=connection),
        ) as connect_mock:
            await self.publisher._connect()

        connect_mock.assert_awaited_once_with(
            self.publisher.url,
        )

        assert self.publisher.connection == connection
        assert self.publisher.channel == channel

    @pytest.mark.asyncio
    async def test_should_not_connect_when_connection_is_open(
        self,
    ) -> None:
        connection = MagicMock()
        connection.is_closed = False

        self.publisher.connection = connection

        with patch(
            "src.infrastructure.messaging.rabbitmq_publisher.connect_robust",
            AsyncMock(),
        ) as connect_mock:
            await self.publisher._connect()

        connect_mock.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_publish_message(
        self,
    ) -> None:
        default_exchange = AsyncMock()

        channel = AsyncMock()
        channel.default_exchange = default_exchange

        self.publisher.channel = channel
        self.publisher.connection = MagicMock()

        self.publisher._connect = AsyncMock()
        self.publisher._close = AsyncMock()

        payload = {
            "lead_id": 1,
            "order_id": 10,
        }

        result = await self.publisher.publish(
            queue_name="dist.sms",
            payload=payload,
        )

        assert result is True

        self.publisher._connect.assert_awaited_once()

        channel.declare_queue.assert_awaited_once_with(
            "dist.sms",
            durable=True,
        )

        default_exchange.publish.assert_awaited_once()

        _, kwargs = default_exchange.publish.await_args

        assert kwargs["routing_key"] == "dist.sms"

        self.publisher._close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_publish_serialized_payload(
        self,
    ) -> None:
        default_exchange = AsyncMock()

        channel = AsyncMock()
        channel.default_exchange = default_exchange

        self.publisher.channel = channel
        self.publisher.connection = MagicMock()

        self.publisher._connect = AsyncMock()
        self.publisher._close = AsyncMock()

        payload = {
            "lead_id": 1,
        }

        await self.publisher.publish(
            queue_name="dist.sms",
            payload=payload,
        )

        args, kwargs = default_exchange.publish.await_args

        message = args[0]

        assert message.body == json.dumps(
            payload,
        ).encode("utf-8")

        assert kwargs["routing_key"] == "dist.sms"

    @pytest.mark.asyncio
    async def test_should_raise_when_channel_is_none(
        self,
    ) -> None:
        self.publisher.channel = None

        self.publisher._connect = AsyncMock()

        with pytest.raises(
            RuntimeError,
            match="RabbitMQ channel not initialized",
        ):
            await self.publisher.publish(
                queue_name="dist.sms",
                payload={},
            )

    @pytest.mark.asyncio
    async def test_should_close_connection(
        self,
    ) -> None:
        connection = AsyncMock()
        connection.is_closed = False

        self.publisher.connection = connection

        await self.publisher._close()

        connection.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_not_close_closed_connection(
        self,
    ) -> None:
        connection = AsyncMock()
        connection.is_closed = True

        self.publisher.connection = connection

        await self.publisher._close()

        connection.close.assert_not_awaited()
