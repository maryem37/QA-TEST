import pytest
import requests


@pytest.mark.tc("TC-010-02")
def test_message_fetch_without_auth_returns_unauthorized(base_url):
    """
    Vérifie que l'accès à /api/message sans le cookie d'authentification
    renvoie bien une réponse d'erreur d'authentification (401 ou 403),
    conformément au comportement attendu (REQ-012).
    """
    r = requests.get(f"{base_url}/api/message", timeout=10)
    assert r.status_code in (401, 403)
