import pytest
import requests


@pytest.mark.tc("TC-001-02")
def test_login_wrong_password_returns_401(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrongpass"},
        timeout=10,
    )
    assert r.status_code == 401
    json_resp = r.json()
    assert "error" in json_resp
    assert json_resp["error"] == "Invalid credentials"
