from unittest.mock import AsyncMock, patch

import pytest

from src.domain.enum.queue_name import QueueName
from src.workers.consumer_worker import LeadReceivedWorker


class TestLeadReceivedWorker:
    def setup_method(self) -> None:
        self.consumer = AsyncMock()
        self.use_case = AsyncMock()
        self.publisher = AsyncMock()

        self.worker = LeadReceivedWorker(
            consumer=self.consumer,
            use_case=self.use_case,
            publisher=self.publisher,
        )

        self.payload = {
            "gateway": "gateway",
            "headers": {},
            "correlation_id": "corr-123",
            "body": {
                "transaction_id": "tx-123",
                "transaction_time": "2026-06-10T12:30:00",
                "event": "order.approved",
                "idempotency_key": "idem-123",
                "customer": {
                    "first_name": "Alfredo",
                    "last_name": "Morais",
                    "email": "alfredo@email.com",
                    "phone": "5519999999999",
                    "country": "BR",
                    "phone_valid": True,
                    "normalized_phone": "5519999999999",
                    "email_valid": True,
                },
                "product": {
                    "id": "product-1",
                    "name": "Curso Python",
                    "niche": "education",
                    "quantity": 1,
                },
                "payment": {
                    "status": "approved",
                    "amount_usd": 99.9,
                    "method": "credit_card",
                },
            },
        }

    @pytest.mark.asyncio
    async def test_should_start_consumer(
        self,
    ) -> None:
        await self.worker.start()

        self.consumer.consume.assert_awaited_once()

        kwargs = self.consumer.consume.await_args.kwargs

        assert kwargs["queue_name"] == QueueName.LEAD_RECEIVED.value

        assert kwargs["callback"] == self.worker.handle

    @pytest.mark.asyncio
    async def test_should_execute_use_case_successfully(
        self,
    ) -> None:
        with patch(
            "src.workers.consumer_worker.asyncio.sleep",
            AsyncMock(),
        ):
            await self.worker.handle(self.payload)

        self.use_case.execute.assert_awaited_once()
        self.publisher.publish.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_retry_until_success(
        self,
    ) -> None:
        self.use_case.execute.side_effect = [
            RuntimeError("error 1"),
            RuntimeError("error 2"),
            None,
        ]

        sleep_mock = AsyncMock()

        with patch(
            "src.workers.consumer_worker.asyncio.sleep",
            sleep_mock,
        ):
            await self.worker.handle(self.payload)

        assert self.use_case.execute.await_count == 3

        sleep_mock.assert_any_await(1)
        sleep_mock.assert_any_await(4)

        self.publisher.publish.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_should_send_to_dead_letter_after_all_retries(
        self,
    ) -> None:
        self.use_case.execute.side_effect = RuntimeError(
            "processing error",
        )

        sleep_mock = AsyncMock()

        with patch(
            "src.workers.consumer_worker.asyncio.sleep",
            sleep_mock,
        ):
            await self.worker.handle(self.payload)

        assert self.use_case.execute.await_count == 3

        assert sleep_mock.await_count == 3

        self.publisher.publish.assert_awaited_once_with(
            QueueName.LEAD_DEAD_CONSUMER_FAILED.value,
            {
                "payload": self.payload,
                "error": "processing error",
            },
        )

    @pytest.mark.asyncio
    async def test_should_wait_expected_retry_delays(
        self,
    ) -> None:
        self.use_case.execute.side_effect = RuntimeError(
            "error",
        )

        sleep_mock = AsyncMock()

        with patch(
            "src.workers.consumer_worker.asyncio.sleep",
            sleep_mock,
        ):
            await self.worker.handle(self.payload)

        delays = [call.args[0] for call in sleep_mock.await_args_list]

        assert delays == [1, 4, 16]


class TestLeadReceivedWorkerWithInvalidPayload:
    def setup_method(self) -> None:
        self.consumer = AsyncMock()
        self.use_case = AsyncMock()
        self.publisher = AsyncMock()

        self.worker = LeadReceivedWorker(
            consumer=self.consumer,
            use_case=self.use_case,
            publisher=self.publisher,
        )

        self.valid_payload = {
            "gateway": "test",
            "headers": {},
            "correlation_id": "corr-123",
            "body": {
                "transaction_id": "tx-1",
                "transaction_time": "2026-06-11T10:00:00",
                "event": "order.approved",
                "idempotency_key": "key-1",
                "customer": {
                    "first_name": "A",
                    "last_name": "B",
                    "email": "a@b.com",
                    "phone": None,
                    "country": None,
                    "phone_valid": None,
                    "normalized_phone": None,
                    "email_valid": None,
                },
                "product": {
                    "id": "1",
                    "name": "prod",
                    "niche": None,
                    "quantity": 1,
                },
                "payment": {
                    "status": "approved",
                    "amount_usd": 10.0,
                    "method": "card",
                },
            },
        }

    @pytest.mark.asyncio
    async def test_should_send_to_dlq_when_payload_is_invalid(self) -> None:
        payload = {
            "gateway": "test",
            "headers": {},
            "correlation_id": "corr-123",
            "body": {
                "transaction_id": "tx-1",
                "transaction_time": "",
                "event": "order.approved",
                "idempotency_key": "key-1",
                "customer": {},
                "product": {},
                "payment": {},
            },
        }

        await self.worker.handle(payload)

        self.publisher.publish.assert_awaited_once()

        args = self.publisher.publish.await_args.args
        assert args[0] == QueueName.LEAD_DEAD_CONSUMER_FAILED.value
        assert "invalid message format" in args[1]["error"]

    @pytest.mark.asyncio
    async def test_should_retry_and_send_to_dlq_after_failures(self) -> None:
        self.use_case.execute.side_effect = RuntimeError("boom")

        sleep_mock = AsyncMock()

        import src.workers.consumer_worker as module

        original_sleep = module.asyncio.sleep
        module.asyncio.sleep = sleep_mock

        try:
            await self.worker.handle(self.valid_payload)
        finally:
            module.asyncio.sleep = original_sleep

        assert self.use_case.execute.await_count == 3

        sleep_mock.assert_any_await(1)
        sleep_mock.assert_any_await(4)
        sleep_mock.assert_any_await(16)

        self.publisher.publish.assert_awaited_once()

        args = self.publisher.publish.await_args.args
        assert args[0] == QueueName.LEAD_DEAD_CONSUMER_FAILED.value
        assert args[1]["payload"] == self.valid_payload
        assert args[1]["error"] == "boom"

    @pytest.mark.asyncio
    async def test_should_process_success_without_dlq(self) -> None:
        await self.worker.handle(self.valid_payload)

        self.use_case.execute.assert_awaited_once()
        self.publisher.publish.assert_not_awaited()
