from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.domain.enum.queue_name import QueueName
from src.workers.distribution_worker import DistributionWorker


def build_session_context_manager():
    session = AsyncMock()

    context_manager = AsyncMock()
    context_manager.__aenter__.return_value = session
    context_manager.__aexit__.return_value = None

    return session, context_manager


class TestDistributionWorker:
    def setup_method(self) -> None:
        self.consumer = AsyncMock()
        self.publisher = AsyncMock()
        self.engine = MagicMock()

        self.worker = DistributionWorker(
            consumer=self.consumer,
            publisher=self.publisher,
            engine=self.engine,
        )

        self.payload = {
            "order_id": 10,
            "lead_id": 1,
            "channel": "SMS",
            "phone": "5519999999999",
            "correlation_id": "corr-123",
        }

    @pytest.mark.asyncio
    async def test_should_start_consumer(self) -> None:
        await self.worker.start()

        self.consumer.consume.assert_awaited_once_with(
            queue_name=QueueName.DIST_SMS.value,
            callback=self.worker.handle,
        )

    @pytest.mark.asyncio
    async def test_should_process_success_first_try(self) -> None:
        session, context_manager = build_session_context_manager()

        use_case = AsyncMock()

        with (
            patch(
                "src.workers.distribution_worker.get_session",
                return_value=context_manager,
            ),
            patch(
                "src.workers.distribution_worker."
                "DistributionStatusRepositorySQLModel"
            ),
            patch("src.workers.distribution_worker.WebhookSiteIntegration"),
            patch(
                "src.workers.distribution_worker.ProcessDistributionUseCase",
                return_value=use_case,
            ),
        ):
            await self.worker.handle(self.payload)

        use_case.execute.assert_awaited_once()
        self.publisher.publish.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_retry_until_success(self) -> None:
        session, context_manager = build_session_context_manager()

        use_case = AsyncMock()
        use_case.execute.side_effect = [
            RuntimeError("error 1"),
            RuntimeError("error 2"),
            None,
        ]

        import src.workers.distribution_worker as module

        sleep_mock = AsyncMock()

        with (
            patch.object(module.asyncio, "sleep", sleep_mock),
            patch.object(
                module,
                "get_session",
                return_value=context_manager,
            ),
            patch.object(
                module,
                "DistributionStatusRepositorySQLModel",
            ),
            patch.object(
                module,
                "WebhookSiteIntegration",
            ),
            patch.object(
                module,
                "ProcessDistributionUseCase",
                return_value=use_case,
            ),
        ):
            await self.worker.handle(self.payload)

        assert use_case.execute.await_count == 3

        sleep_mock.assert_any_await(1)
        sleep_mock.assert_any_await(4)

        self.publisher.publish.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_send_to_dead_letter_after_failures(
        self,
    ) -> None:
        session, context_manager = build_session_context_manager()

        use_case = AsyncMock()
        use_case.execute.side_effect = RuntimeError("error")

        import src.workers.distribution_worker as module

        sleep_mock = AsyncMock()

        with (
            patch.object(module.asyncio, "sleep", sleep_mock),
            patch.object(
                module,
                "get_session",
                return_value=context_manager,
            ),
            patch.object(
                module,
                "DistributionStatusRepositorySQLModel",
            ),
            patch.object(
                module,
                "WebhookSiteIntegration",
            ),
            patch.object(
                module,
                "ProcessDistributionUseCase",
                return_value=use_case,
            ),
        ):
            await self.worker.handle(self.payload)

        assert use_case.execute.await_count == 3

        assert sleep_mock.await_count == 3

        self.publisher.publish.assert_awaited_once_with(
            QueueName.DIST_DEAD_SMS.value,
            {
                "payload": self.payload,
                "error": "error",
            },
        )

    @pytest.mark.asyncio
    async def test_should_use_expected_backoff_delays(
        self,
    ) -> None:
        session, context_manager = build_session_context_manager()

        use_case = AsyncMock()
        use_case.execute.side_effect = RuntimeError("error")

        import src.workers.distribution_worker as module

        sleep_mock = AsyncMock()

        with (
            patch.object(module.asyncio, "sleep", sleep_mock),
            patch.object(
                module,
                "get_session",
                return_value=context_manager,
            ),
            patch.object(
                module,
                "DistributionStatusRepositorySQLModel",
            ),
            patch.object(
                module,
                "WebhookSiteIntegration",
            ),
            patch.object(
                module,
                "ProcessDistributionUseCase",
                return_value=use_case,
            ),
        ):
            await self.worker.handle(self.payload)

        delays = [call.args[0] for call in sleep_mock.await_args_list]

        assert delays == [1, 4, 16]
