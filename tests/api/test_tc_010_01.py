import pytest
import requests


@pytest.mark.tc("TC-010-01")
def test_retrieve_message_list_after_successful_authentication(base_url):
    # Step 1 – login and obtain token
    login_resp = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("token")
    assert token, "Login response does not contain a token"

    # Step 2 – retrieve messages with token in cookie
    msgs_resp = requests.get(
        f"{base_url}/api/message",
        headers={"Cookie": f"token={token}"},
        timeout=10,
    )
    assert msgs_resp.status_code == 200
    payload = msgs_resp.json()
    assert "messages" in payload, "Response JSON missing 'messages' key"

    messages = payload["messages"]
    assert isinstance(messages, list), "'messages' should be a list"

    # Verify at least one expected message is present
    expected = [
        m
        for m in messages
        if m.get("name") == "James Dean"
        and m.get("subject") == "Booking enquiry"
        and m.get("read") is False
    ]
    assert expected, "Expected message (James Dean) not found in the list"
