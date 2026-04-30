from fastapi.testclient import TestClient

from app.main import app


def test_login_and_chat_flow() -> None:
    with TestClient(app) as client:
        login_response = client.post(
            "/auth/login",
            json={"email": "demo.customer1@example.com", "pin": "1111"},
        )
        assert login_response.status_code == 200

        token = login_response.json()["access_token"]

        chat_response = client.post(
            "/chat",
            json={"message": "Do you have keyboards in stock?"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert chat_response.status_code == 200
        assert chat_response.json()["reply"]


def test_chat_requires_auth() -> None:
    with TestClient(app) as client:
        response = client.post("/chat", json={"message": "hello"})
        assert response.status_code == 401


def test_login_rejects_invalid_pin() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/auth/login",
            json={"email": "demo.customer1@example.com", "pin": "0000"},
        )
        assert response.status_code == 401
