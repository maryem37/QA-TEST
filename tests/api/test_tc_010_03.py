import pytest
import requests


@pytest.mark.tc("TC-010-03")
def test_messages_with_invalid_token_rejected(base_url):
    """
    Vérifie que l'API refuse l'accès aux messages lorsqu'un token invalide est fourni.
    Le comportement attendu est un statut 401 ou 403.
    """
    r = requests.get(
        f"{base_url}/api/message",
        headers={"Cookie": "token=invalid_token"},
        timeout=10,
    )
    assert r.status_code in (401, 403)
