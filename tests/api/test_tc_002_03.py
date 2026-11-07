import pytest
import requests


@pytest.mark.tc("TC-002-03")
def test_login_invalid_credentials(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        timeout=10,
    )
    assert r.status_code == 401
    json_body = r.json()
    assert "error" in json_body
    assert json_body["error"] == "Invalid credentials"
