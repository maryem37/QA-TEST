import pytest
import requests


@pytest.mark.tc("TC-010-01")
def test_messages_list_with_valid_token(base_url, admin_token):
    r = requests.get(
        f"{base_url}/api/message",
        headers={"Cookie": f"token={admin_token}"},
        timeout=10,
    )
    assert r.status_code == 200
    assert "messages" in r.json()


@pytest.mark.tc("TC-010-02")
@pytest.mark.xfail(reason="DEF-002 : GET /api/message accessible sans jeton", strict=True)
def test_messages_without_token_rejected(base_url):
    r = requests.get(f"{base_url}/api/message", timeout=10)
    assert r.status_code in (401, 403)


@pytest.mark.tc("TC-010-03")
@pytest.mark.xfail(reason="DEF-002 : GET /api/message accessible avec jeton invalide", strict=True)
def test_messages_with_invalid_token_rejected(base_url):
    r = requests.get(
        f"{base_url}/api/message",
        headers={"Cookie": "token=invalid_token"},
        timeout=10,
    )
    assert r.status_code in (401, 403)