import pytest
import requests


@pytest.mark.tc("TC-010-03")
def test_message_retrieval_fails_with_invalid_token(base_url):
    # Use an obviously invalid token
    r = requests.get(
        f"{base_url}/api/message",
        cookies={"token": "invalid_token"},
        timeout=10,
    )
    # Expected behavior: unauthorized access
    assert r.status_code == 401
