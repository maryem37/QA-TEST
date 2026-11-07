import pytest
import requests


@pytest.mark.tc("TC-010-04")
def test_initial_message_is_unread(base_url):
    # Step 1: login and obtain token
    login_resp = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("token")
    assert token, "Login response must contain a token"

    # Step 2: retrieve messages with the obtained token
    msgs_resp = requests.get(
        f"{base_url}/api/message",
        headers={"Cookie": f"token={token}"},
        timeout=10,
    )
    assert msgs_resp.status_code == 200
    data = msgs_resp.json()
    assert "messages" in data, "Response must contain 'messages' field"
    messages = data["messages"]
    assert isinstance(messages, list) and len(messages) > 0, "Messages list must not be empty"

    # Verify the first message is marked as unread
    first_msg = messages[0]
    assert "read" in first_msg, "Message object must contain 'read' field"
    assert first_msg["read"] is False, "The initial message should be unread"
