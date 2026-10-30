import pytest
import requests


@pytest.mark.tc("TC-010-04")
def test_initial_message_is_unread(base_url, admin_token):
    # Récupérer les messages avec le token d'administration
    r = requests.get(
        f"{base_url}/api/message",
        cookies={"token": admin_token},
        timeout=10,
    )
    # Le serveur doit répondre 200 et fournir le tableau "messages"
    assert r.status_code == 200
    json_body = r.json()
    assert "messages" in json_body

    messages = json_body["messages"]
    # Au moins un message doit être présent (données initiales)
    assert len(messages) >= 1

    first_msg = messages[0]
    # Le premier message doit contenir le champ "read" et être non lu
    assert "read" in first_msg
    assert first_msg["read"] is False
