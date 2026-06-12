from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Response, status
from httpx import ASGITransport, AsyncClient

from src.views.routers.webhook import webhook_router


class TestWebhookRouter:
    @pytest.fixture
    def app(self):
        app = FastAPI()

        @app.middleware("http")
        async def fake_middleware(request, call_next):
            request.state.correlation_id = "test-correlation-id"
            return await call_next(request)

        app.state.engine = MagicMock()
        app.include_router(webhook_router)

        return app

    @pytest.mark.asyncio
    @patch("src.views.routers.webhook.get_session")
    @patch("src.views.routers.webhook.EventSalesController")
    async def test_receive_webhook_grummer(
        self,
        controller_mock,
        get_session_mock,
        app,
    ):
        session = AsyncMock()

        context_manager = AsyncMock()
        context_manager.__aenter__.return_value = session
        context_manager.__aexit__.return_value = None

        get_session_mock.return_value = context_manager

        controller_instance = AsyncMock()
        controller_instance.execute.return_value = Response(
            status_code=status.HTTP_200_OK
        )

        controller_mock.return_value = controller_instance

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/webhook/grummer",
                json={"body": {}},
            )

        assert response.status_code == status.HTTP_200_OK

        controller_instance.execute.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.views.routers.webhook.get_session")
    @patch("src.views.routers.webhook.EventSalesController")
    async def test_receive_webhook_lous(
        self,
        controller_mock,
        get_session_mock,
        app,
    ):
        session = AsyncMock()

        context_manager = AsyncMock()
        context_manager.__aenter__.return_value = session
        context_manager.__aexit__.return_value = None

        get_session_mock.return_value = context_manager

        controller_instance = AsyncMock()
        controller_instance.execute.return_value = Response(
            status_code=status.HTTP_200_OK
        )

        controller_mock.return_value = controller_instance

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/webhook/lous",
                json={"body": {}},
            )

        assert response.status_code == status.HTTP_200_OK

        controller_instance.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_invalid_gateway(
        self,
        app,
    ):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/webhook/invalid",
                json={"body": {}},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
