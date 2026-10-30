import pytest
import requests


@pytest.mark.tc("TC-001-03")
def test_admin_login_with_empty_fields_returns_401(base_url):
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "", "password": ""},
        timeout=10,
    )
    assert response.status_code == 401
    assert response.json() == {"error": "Invalid credentials"}
