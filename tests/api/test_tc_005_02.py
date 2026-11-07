import pytest
import requests


@pytest.mark.tc("TC-005-02")
def test_delete_nonexistent_room(base_url, admin_token):
    """
    Suppression d'une chambre inexistante via l'API.
    Vérifie que la réponse n'est pas un 500.
    """
    url = f"{base_url}/api/room/999999"
    headers = {"Cookie": f"token={admin_token}"}
    response = requests.delete(url, headers=headers, timeout=10)
    assert response.status_code != 500
