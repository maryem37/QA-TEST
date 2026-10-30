import pytest
import requests


@pytest.mark.tc("TC-001-03")
def test_login_empty_fields(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "", "password": ""},
        timeout=10,
    )
    assert r.status_code == 401
    json_resp = r.json()
    assert "error" in json_resp
    assert json_resp["error"] == "Invalid credentials"
