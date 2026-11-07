import pytest
import requests


@pytest.mark.tc("TC-012-03")
def test_message_read_with_invalid_token(base_url):
    # Send request with an invalid token in the cookie
    r = requests.get(
        f"{base_url}/api/message",
        cookies={"token": "invalid_token"},
        timeout=10,
    )
    # Expected behavior: unauthorized (401) or forbidden (403)
    assert r.status_code in (401, 403)
