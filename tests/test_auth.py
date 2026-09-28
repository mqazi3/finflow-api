from app.auth import create_access_token
from app.config import settings

from tests.helpers import API, register_and_login


def test_register_returns_user_without_password(client):
    response = client.post(
        f"{API}/register",
        json={"username": "alice", "password": "password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "alice"
    assert "id" in body
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_rejects_duplicate_username(client):
    register_and_login(client, "alice")

    response = client.post(
        f"{API}/register",
        json={"username": "alice", "password": "different123"},
    )

    assert response.status_code == 400


def test_register_validates_input(client):
    response = client.post(
        f"{API}/register",
        json={"username": "al", "password": "123"},
    )

    assert response.status_code == 422


def test_login_rejects_wrong_password(client):
    register_and_login(client, "alice")

    response = client.post(
        f"{API}/login",
        data={"username": "alice", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_login_rejects_unknown_user(client):
    response = client.post(
        f"{API}/login",
        data={"username": "nobody", "password": "password123"},
    )

    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get(f"{API}/accounts/")

    assert response.status_code == 401


def test_tampered_token_is_rejected(client):
    headers = register_and_login(client, "alice")
    token = headers["Authorization"].removeprefix("Bearer ")

    # Replace the last four signature characters so the signature no longer matches
    replacement = "AAAA" if token[-4:] != "AAAA" else "BBBB"
    tampered = token[:-4] + replacement

    response = client.get(
        f"{API}/accounts/",
        headers={"Authorization": f"Bearer {tampered}"},
    )

    assert response.status_code == 401


def test_token_signed_with_another_key_is_rejected(client, monkeypatch):
    register_and_login(client, "alice")

    monkeypatch.setattr(settings, "secret_key", "attacker-key")
    forged = create_access_token({"sub": "alice"})
    monkeypatch.setattr(settings, "secret_key", "test-secret-key")

    response = client.get(
        f"{API}/accounts/",
        headers={"Authorization": f"Bearer {forged}"},
    )

    assert response.status_code == 401


def test_expired_token_is_rejected(client, monkeypatch):
    register_and_login(client, "alice")

    monkeypatch.setattr(settings, "access_token_expire_minutes", -1)
    expired = create_access_token({"sub": "alice"})

    response = client.get(
        f"{API}/accounts/",
        headers={"Authorization": f"Bearer {expired}"},
    )

    assert response.status_code == 401


def test_token_for_deleted_or_unknown_user_is_rejected(client):
    token = create_access_token({"sub": "ghost"})

    response = client.get(
        f"{API}/accounts/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
