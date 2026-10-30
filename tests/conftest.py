import os

import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    return os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")


@pytest.fixture(scope="session")
def room_direct_url():
    """Service rbp-room en direct, contourne la passerelle (DEF-003)."""
    return os.environ.get("ROOM_DIRECT_URL", "http://localhost:3001")


@pytest.fixture(scope="session")
def admin_token(base_url):
    r = requests.post(
        f"{base_url}/api/auth/login",
        json={"username": "admin", "password": "password"},
        timeout=10,
    )
    assert r.status_code == 200, f"login a échoué: {r.status_code}"
    return r.json()["token"]


@pytest.fixture(scope="session")
def admin(admin_token):
    """Session requests authentifiée (jeton envoyé en en-tête Cookie)."""
    s = requests.Session()
    s.headers.update({"Cookie": f"token={admin_token}"})
    return s