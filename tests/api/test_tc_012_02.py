import pytest
import requests


@pytest.mark.tc("TC-012-02")
def test_message_read_without_token_returns_unauthorized(base_url):
    """
    Verify that accessing /api/message without the authentication cookie
    returns an unauthorized error (401 or 403) as defined by the requirements.
    """
    response = requests.get(
        f"{base_url}/api/message",
        timeout=10,
    )
    assert response.status_code in (401, 403), (
        f"Expected 401 or 403 when no token is provided, got {response.status_code}"
    )
