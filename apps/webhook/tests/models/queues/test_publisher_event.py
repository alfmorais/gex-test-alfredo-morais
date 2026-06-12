from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.queue.publisher_event import RabbitPublisher


class TestRabbitPublisher:
    @pytest.fixture
    def publisher(self):
        return RabbitPublisher()

    @pytest.mark.asyncio
    async def test_connect_creates_connection(
        self,
        publisher,
    ):
        connection = AsyncMock()
        connection.is_closed = False

        channel = AsyncMock()

        connection.channel.return_value = channel

        with patch(
            "src.models.queue.publisher_event.connect_robust",
            return_value=connection,
        ) as connect_mock:
            await publisher._connect()

        connect_mock.assert_awaited_once()

        assert publisher.connection is connection
        assert publisher.channel is channel

    @pytest.mark.asyncio
    async def test_connect_reuses_existing_connection(
        self,
        publisher,
    ):
        publisher.connection = MagicMock()
        publisher.connection.is_closed = False

        with patch(
            "src.models.queue.publisher_event.connect_robust"
        ) as connect_mock:
            await publisher._connect()

        connect_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_publish_success(
        self,
        publisher,
    ):
        exchange = AsyncMock()

        channel = AsyncMock()
        channel.default_exchange = exchange

        publisher.channel = channel

        with (
            patch.object(
                publisher,
                "_connect",
                new_callable=AsyncMock,
            ),
            patch.object(
                publisher,
                "_close",
                new_callable=AsyncMock,
            ) as close_mock,
        ):
            result = await publisher.publish(
                queue_name="sales",
                payload={"id": "123"},
            )

        assert result is True

        channel.declare_queue.assert_awaited_once_with(
            "sales",
            durable=True,
        )

        exchange.publish.assert_awaited_once()

        close_mock.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_publish_without_channel(
        self,
        publisher,
    ):
        publisher.channel = None

        with patch.object(
            publisher,
            "_connect",
            new_callable=AsyncMock,
        ):
            with pytest.raises(
                RuntimeError,
                match="RabbitMQ channel not initialized",
            ):
                await publisher.publish(
                    queue_name="sales",
                    payload={"id": "123"},
                )

    @pytest.mark.asyncio
    async def test_close_connection(
        self,
        publisher,
    ):
        connection = AsyncMock()
        connection.is_closed = False

        publisher.connection = connection

        await publisher._close()

        connection.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_ignores_closed_connection(
        self,
        publisher,
    ):
        connection = AsyncMock()
        connection.is_closed = True

        publisher.connection = connection

        await publisher._close()

        connection.close.assert_not_called()
