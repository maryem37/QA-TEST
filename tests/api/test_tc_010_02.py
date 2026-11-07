import pytest
import requests


@pytest.mark.tc("TC-010-02")
def test_messages_without_token_rejected(base_url):
    """
    Verify that accessing /api/message without authentication returns
    401 Unauthorized or 403 Forbidden.
    """
    response = requests.get(
        f"{base_url}/api/message",
        timeout=10,
    )
    assert response.status_code in (401, 403)
