from fastapi import Request
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routes.chat import get_chat_engine


async def _fake_engine(request: Request):
    class _Engine:
        async def respond(
            self,
            user_email: str,
            user_message: str,
            history: list[dict[str, str]] | None = None,
        ) -> str:
            return "stub reply"

    return _Engine()


async def _failing_engine(request: Request):
    class _Engine:
        async def respond(
            self,
            user_email: str,
            user_message: str,
            history: list[dict[str, str]] | None = None,
        ) -> str:
            raise RuntimeError("upstream unavailable")

    return _Engine()


@pytest.mark.asyncio
async def test_chat_without_auth() -> None:
    app.dependency_overrides[get_chat_engine] = _fake_engine
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            chat_response = await client.post(
                "/chat",
                json={"customer_email": "user@example.com", "message": "Do you have keyboards in stock?"},
            )
            assert chat_response.status_code == 200
            assert chat_response.json()["reply"] == "stub reply"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_chat_passes_history_to_engine() -> None:
    async def _capturing_engine(request: Request):
        class _Engine:
            async def respond(
                self,
                user_email: str,
                user_message: str,
                history: list[dict[str, str]] | None = None,
            ) -> str:
                assert user_email == "user@example.com"
                assert user_message == "Where is it now?"
                assert history == [{"role": "assistant", "content": "Order 123 shipped."}]
                return "still in transit"

        return _Engine()

    app.dependency_overrides[get_chat_engine] = _capturing_engine
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            chat_response = await client.post(
                "/chat",
                json={
                    "customer_email": "user@example.com",
                    "message": "Where is it now?",
                    "history": [{"role": "assistant", "content": "Order 123 shipped."}],
                },
            )
            assert chat_response.status_code == 200
            assert chat_response.json()["reply"] == "still in transit"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_api_chat_engine_failure_returns_structured_detail() -> None:
    app.dependency_overrides[get_chat_engine] = _failing_engine
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            chat_response = await client.post(
                "/api/chat",
                json={"customer_email": "user@example.com", "message": "Do you have keyboards in stock?"},
            )
            assert chat_response.status_code == 502
            assert chat_response.json()["detail"] == "Unable to process request"
    finally:
        app.dependency_overrides.clear()
