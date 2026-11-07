import pytest
import requests


@pytest.mark.tc("TC-001-02")
def test_login_wrong_password_rejected(base_url):
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrongpass"},
        timeout=10,
    )
    assert response.status_code == 401
    json_body = response.json()
    assert "error" in json_body
    assert json_body["error"] == "Invalid credentials"
