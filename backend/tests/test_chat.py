from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app
from app.routes.chat import get_chat_engine


def _fake_engine(request: Request):
    class _Engine:
        async def respond(self, user_email: str, user_message: str) -> str:
            return "stub reply"

    return _Engine()


def test_chat_without_auth() -> None:
    app.dependency_overrides[get_chat_engine] = _fake_engine
    try:
        with TestClient(app) as client:
            chat_response = client.post(
                "/chat",
                json={"message": "Do you have keyboards in stock?"},
            )
            assert chat_response.status_code == 200
            assert chat_response.json()["reply"] == "stub reply"
    finally:
        app.dependency_overrides.clear()
