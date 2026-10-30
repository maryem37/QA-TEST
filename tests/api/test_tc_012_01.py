import pytest
import requests


@pytest.mark.tc("TC-012-01")
def test_get_messages_with_valid_token(base_url, admin_token):
    """Lecture des messages avec un jeton valide."""
    r = requests.get(
        f"{base_url}/api/message",
        cookies={"token": admin_token},
        timeout=10,
    )
    assert r.status_code == 200
    data = r.json()
    assert "messages" in data
    messages = data["messages"]
    assert isinstance(messages, list)
    assert len(messages) >= 1
    for msg in messages:
        # chaque message doit contenir les champs attendus
        expected_keys = {"id", "name", "read", "subject"}
        assert expected_keys <= msg.keys()
        assert isinstance(msg["id"], int)
        assert isinstance(msg["name"], str)
        assert isinstance(msg["read"], bool)
        assert isinstance(msg["subject"], str)
