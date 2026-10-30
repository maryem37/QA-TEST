import pytest
import requests


@pytest.mark.tc("TC-001-01")
def test_admin_login_and_fetch_messages(base_url: str, admin_token: str):
    # Step 1 – login with valid credentials
    login_resp = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert login_resp.status_code == 200
    login_json = login_resp.json()
    assert "token" in login_json
    assert isinstance(login_json["token"], str) and login_json["token"]

    # Step 2 – fetch messages with a valid token (provided by fixture)
    msgs_resp = requests.get(
        f"{base_url}/api/message",
        cookies={"token": admin_token},
        timeout=10,
    )
    assert msgs_resp.status_code == 200
    msgs_json = msgs_resp.json()
    assert "messages" in msgs_json
    messages = msgs_json["messages"]
    assert isinstance(messages, list)
    assert len(messages) >= 1

    # Verify structure of each message
    for msg in messages:
        assert {"id", "name", "read", "subject"} <= msg.keys()
        assert isinstance(msg["id"], int)
        assert isinstance(msg["name"], str)
        assert isinstance(msg["read"], bool)
        assert isinstance(msg["subject"], str)
