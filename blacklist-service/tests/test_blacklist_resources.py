from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

import app.resources as resources


def build_blacklist_entry_double(first_result):
    existing_query = MagicMock()
    existing_query.first.return_value = first_result
    filter_by_mock = MagicMock(return_value=existing_query)

    class BlacklistEntryDouble:
        query = SimpleNamespace(filter_by=filter_by_mock)

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    return BlacklistEntryDouble, filter_by_mock


def test_post_blacklists_creates_entry_successfully(client, auth_headers, monkeypatch):
    blacklist_entry_double, filter_by_mock = build_blacklist_entry_double(None)
    add_mock = MagicMock()
    commit_mock = MagicMock()

    monkeypatch.setattr(resources, "BlacklistEntry", blacklist_entry_double)
    monkeypatch.setattr(resources.db.session, "add", add_mock)
    monkeypatch.setattr(resources.db.session, "commit", commit_mock)

    payload = {
        "email": " User@Example.com ",
        "app_uuid": str(uuid4()),
        "blocked_reason": " fraude ",
    }

    response = client.post(
        "/blacklists",
        json=payload,
        headers={**auth_headers, "X-Forwarded-For": "203.0.113.10"},
    )

    assert response.status_code == 201
    assert response.get_json() == {
        "message": "Email agregado exitosamente a la blacklist"
    }
    filter_by_mock.assert_called_once_with(email="user@example.com")
    add_mock.assert_called_once()
    commit_mock.assert_called_once()

    created_entry = add_mock.call_args.args[0]
    assert created_entry.email == "user@example.com"
    assert created_entry.app_uuid == payload["app_uuid"]
    assert created_entry.blocked_reason == "fraude"
    assert created_entry.request_ip == "203.0.113.10"
    assert created_entry.created_at is not None


def test_post_blacklists_returns_400_for_invalid_payload(client, auth_headers):
    response = client.post(
        "/blacklists",
        json={"email": "not-an-email", "app_uuid": "invalid-uuid"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    response_json = response.get_json()
    assert response_json["message"] == "Datos inválidos"
    assert "email" in response_json["errors"]
    assert "app_uuid" in response_json["errors"]


def test_post_blacklists_returns_409_when_email_already_exists(
    client, auth_headers, monkeypatch
):
    blacklist_entry_double, _ = build_blacklist_entry_double(
        SimpleNamespace(email="user@example.com")
    )
    monkeypatch.setattr(resources, "BlacklistEntry", blacklist_entry_double)

    response = client.post(
        "/blacklists",
        json={"email": "user@example.com", "app_uuid": str(uuid4())},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.get_json() == {
        "message": "El email ya se encuentra en la blacklist"
    }


def test_post_blacklists_returns_409_when_commit_raises_integrity_error(
    client, auth_headers, monkeypatch
):
    blacklist_entry_double, _ = build_blacklist_entry_double(None)
    rollback_mock = MagicMock()

    monkeypatch.setattr(resources, "BlacklistEntry", blacklist_entry_double)
    monkeypatch.setattr(resources.db.session, "add", MagicMock())
    monkeypatch.setattr(
        resources.db.session,
        "commit",
        MagicMock(side_effect=IntegrityError("stmt", "params", "orig")),
    )
    monkeypatch.setattr(resources.db.session, "rollback", rollback_mock)

    response = client.post(
        "/blacklists",
        json={"email": "user@example.com", "app_uuid": str(uuid4())},
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.get_json() == {
        "message": "El email ya se encuentra en la blacklist"
    }
    rollback_mock.assert_called_once()


def test_post_blacklists_requires_token(client):
    response = client.post(
        "/blacklists",
        json={"email": "user@example.com", "app_uuid": str(uuid4())},
    )

    assert response.status_code == 401


def test_post_blacklists_rejects_invalid_token(client):
    response = client.post(
        "/blacklists",
        json={"email": "user@example.com", "app_uuid": str(uuid4())},
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 422


def test_get_blacklists_email_returns_true_when_entry_exists(
    client, auth_headers, monkeypatch
):
    blacklist_entry_double, filter_by_mock = build_blacklist_entry_double(
        SimpleNamespace(blocked_reason="fraude")
    )
    monkeypatch.setattr(resources, "BlacklistEntry", blacklist_entry_double)

    response = client.get("/blacklists/User@Example.com ", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {
        "is_blacklisted": True,
        "blocked_reason": "fraude",
    }
    filter_by_mock.assert_called_once_with(email="user@example.com")


def test_get_blacklists_email_returns_false_when_entry_does_not_exist(
    client, auth_headers, monkeypatch
):
    blacklist_entry_double, _ = build_blacklist_entry_double(None)
    monkeypatch.setattr(resources, "BlacklistEntry", blacklist_entry_double)

    response = client.get("/blacklists/missing@example.com", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {
        "is_blacklisted": False,
        "blocked_reason": None,
    }


def test_get_blacklists_email_requires_token(client):
    response = client.get("/blacklists/user@example.com")

    assert response.status_code == 401


def test_get_blacklists_email_rejects_invalid_token(client):
    response = client.get(
        "/blacklists/user@example.com",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 422
