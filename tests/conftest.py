import json
import os
from pathlib import Path

import pytest
import requests

_KNOWN = json.loads(
    (Path(__file__).resolve().parent.parent / "spec" / "known_defects.json")
    .read_text(encoding="utf-8")
)


def pytest_collection_modifyitems(config, items):
    """Marque en xfail strict les tests liés à un défaut connu (spec/known_defects.json)."""
    for item in items:
        marker = item.get_closest_marker("tc")
        if marker and marker.args and marker.args[0] in _KNOWN:
            d = _KNOWN[marker.args[0]]
            item.add_marker(
                pytest.mark.xfail(reason=f"{d['def']} : {d['title']}", strict=True)
            )


@pytest.fixture(scope="session")
def base_url():
    return os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")


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
