import pytest
import requests


@pytest.mark.tc("TC-012-02")
def test_get_messages_without_token_returns_unauthorized(base_url):
    """
    Vérifie que l'accès à l'endpoint /api/message sans le cookie d'authentification
    renvoie bien un code 401 ou 403, conformément à la spécification REQ-012.
    """
    response = requests.get(
        f"{base_url}/api/message",
        timeout=10,
    )
    assert response.status_code in (401, 403), (
        f"Expected 401 or 403 when no token is provided, got {response.status_code}"
    )
