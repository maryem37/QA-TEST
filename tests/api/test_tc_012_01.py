import pytest
import requests


@pytest.mark.tc("TC-012-01")
def test_read_messages_with_valid_token(base_url, admin_token):
    response = requests.get(
        f"{base_url}/api/message",
        headers={"Cookie": f"token={admin_token}"},
        timeout=10,
    )
    assert response.status_code == 200
    json_body = response.json()
    assert "messages" in json_body
    assert isinstance(json_body["messages"], list)
