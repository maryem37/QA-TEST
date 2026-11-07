import pytest
import requests


@pytest.mark.tc("TC-001-01")
def test_admin_login_and_fetch_messages(base_url):
    # Step 1: login with valid credentials
    login_resp = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert login_resp.status_code == 200
    json_login = login_resp.json()
    assert "token" in json_login
    token = json_login["token"]

    # Step 2: use the token to fetch messages
    messages_resp = requests.get(
        f"{base_url}/api/message",
        headers={"Cookie": f"token={token}"},
        timeout=10,
    )
    assert messages_resp.status_code == 200
    json_msg = messages_resp.json()
    assert "messages" in json_msg
    # Verify at least one message is present (e.g., the initial James Dean message)
    assert isinstance(json_msg["messages"], list)
    assert len(json_msg["messages"]) >= 1
