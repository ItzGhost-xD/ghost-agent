from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_health_is_public_and_does_not_expose_a_secret(monkeypatch):
    monkeypatch.delenv("GHOST_AGENT_API_KEY", raising=False)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert response.json()["api_key_configured"] is False
    assert "GHOST_AGENT_API_KEY" not in response.text


def test_file_access_fails_closed_without_api_key(monkeypatch):
    monkeypatch.delenv("GHOST_AGENT_API_KEY", raising=False)

    response = client.get("/files")

    assert response.status_code == 503


def test_file_access_requires_valid_bearer_token(monkeypatch):
    token = "test-token-that-is-long-enough-1234567890"
    monkeypatch.setenv("GHOST_AGENT_API_KEY", token)

    denied = client.get("/files", headers={"Authorization": "Bearer wrong"})
    allowed = client.get("/files", headers={"Authorization": f"Bearer {token}"})

    assert denied.status_code == 401
    assert allowed.status_code == 200
    assert "files" in allowed.json()


def test_placeholder_api_key_does_not_unlock_routes(monkeypatch):
    monkeypatch.setenv("GHOST_AGENT_API_KEY", "replace-with-a-long-random-token")

    response = client.get("/files")

    assert response.status_code == 503