import copy

import pytest

from app import app
from services.users import USERS


@pytest.fixture(autouse=True)
def restore_users():
    """Reset USERS after each test so tests don't affect each other."""
    snapshot = copy.deepcopy(USERS)
    yield
    USERS.clear()
    USERS.update(snapshot)

@pytest.fixture
def client():
    return app.test_client()


def test_get_user_includes_notification_pref_default_none(client):
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.get_json()["notification_pref"] == "none"
    # The stored record is not changed by reading it.
    assert USERS[1]["notification_pref"] is None

def test_get_user_includes_set_notification_pref(client):
    USERS[1]["notification_pref"] = "sms"
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.get_json()["notification_pref"] == "sms"

def test_get_user_unknown(client):
    response = client.get("/api/users/999")
    assert response.status_code == 404

def test_get_notifications(client):
    USERS[2]["notification_pref"] = "email"
    response = client.get("/api/users/2/notifications")
    assert response.status_code == 200
    assert response.get_json() == {"user_id": 2, "notification_pref": "email"}

def test_get_notifications_default_none(client):
    response = client.get("/api/users/1/notifications")
    assert response.status_code == 200
    assert response.get_json() == {"user_id": 1, "notification_pref": "none"}

def test_get_notifications_unknown_user(client):
    response = client.get("/api/users/999/notifications")
    assert response.status_code == 404

def test_patch_notifications_valid(client):
    response = client.patch("/api/users/1/notifications",
                            json={"notification_pref": "sms"})
    assert response.status_code == 200
    assert response.get_json() == {"user_id": 1, "notification_pref": "sms"}
    # The change persists.
    assert client.get("/api/users/1/notifications").get_json()[
        "notification_pref"] == "sms"
    assert client.get("/api/users/1").get_json()["notification_pref"] == "sms"

def test_patch_notifications_null_becomes_none(client):
    USERS[1]["notification_pref"] = "email"
    response = client.patch("/api/users/1/notifications",
                            json={"notification_pref": None})
    assert response.status_code == 200
    assert response.get_json()["notification_pref"] == "none"

def test_patch_notifications_missing_field(client):
    response = client.patch("/api/users/1/notifications", json={})
    assert response.status_code == 422

def test_patch_notifications_no_body(client):
    response = client.patch("/api/users/1/notifications")
    assert response.status_code == 422

def test_patch_notifications_invalid_value(client):
    response = client.patch("/api/users/1/notifications",
                            json={"notification_pref": "fax"})
    assert response.status_code == 422
    assert USERS[1]["notification_pref"] is None

def test_patch_notifications_unknown_user(client):
    response = client.patch("/api/users/999/notifications",
                            json={"notification_pref": "sms"})
    assert response.status_code == 404

def test_patch_notifications_unknown_user_missing_field(client):
    response = client.patch("/api/users/999/notifications", json={})
    assert response.status_code == 422
