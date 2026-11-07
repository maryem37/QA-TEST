import pytest
import requests


@pytest.mark.tc("TC-001-01")
def test_login_valid_returns_token(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r.status_code == 200
    assert r.json()["token"]


@pytest.mark.tc("TC-001-02")
def test_login_wrong_password_rejected(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "wrong"},
        timeout=10,
    )
    assert r.status_code == 401


@pytest.mark.tc("TC-901-01")
@pytest.mark.xfail(reason="DEF-001 : JSON invalide sur le login renvoie 500", strict=True)
def test_login_invalid_json_returns_400(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        data="{bad",
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    assert r.status_code == 400