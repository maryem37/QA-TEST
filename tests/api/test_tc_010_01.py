import pytest
import requests


@pytest.mark.tc("TC-010-01")
def test_messages_after_successful_auth(base_url, admin_token):
    """Récupérer la liste des messages après authentification réussie."""
    r = requests.get(
        f"{base_url}/api/message",
        cookies={"token": admin_token},
        timeout=10,
    )
    assert r.status_code == 200

    payload = r.json()
    assert "messages" in payload
    messages = payload["messages"]
    assert isinstance(messages, list)
    assert len(messages) >= 1

    # Vérifier la forme minimale de chaque message
    for msg in messages:
        assert {"id", "name", "subject", "read"} <= msg.keys()
        assert isinstance(msg["id"], int)
        assert isinstance(msg["name"], str)
        assert isinstance(msg["subject"], str)
        assert isinstance(msg["read"], bool)

    # Au moins un message doit correspondre aux valeurs attendues
    expected = {"name": "James Dean", "subject": "Booking enquiry", "read": False}
    assert any(
        all(msg.get(k) == v for k, v in expected.items())
        for msg in messages
    )
