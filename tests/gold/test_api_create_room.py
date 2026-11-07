import uuid

import pytest
import requests


def _payload(name):
    return {
        "roomName": name,
        "type": "Single",
        "accessible": False,
        "description": "Created by automated test",
        "features": ["WiFi"],
        "image": "https://www.mwtestconsultancy.co.uk/img/room1.jpg",
        "roomPrice": "123",
    }


@pytest.mark.tc("TC-901-02")
def test_create_room_then_visible_in_list(base_url, admin):
    name = f"QA-{uuid.uuid4().hex[:6]}"
    room_id = None
    try:
        r = admin.post(f"{base_url}/api/room", json=_payload(name), timeout=10)
        assert r.status_code == 200

        rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        matches = [x for x in rooms if x["roomName"] == name]
        assert len(matches) == 1
        room_id = matches[0]["roomid"]
        assert matches[0]["type"] == "Single"
        assert matches[0]["roomPrice"] == 123
    finally:
        if room_id is not None:
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)


@pytest.mark.tc("TC-901-03")
def test_create_room_without_token_is_rejected(base_url):
    r = requests.post(f"{base_url}/api/room", json=_payload("QA-NOAUTH"), timeout=10)
    assert r.status_code == 401


@pytest.mark.tc("TC-901-04")
def test_delete_room_succeeds(base_url, admin):
    name = f"QA-{uuid.uuid4().hex[:6]}"
    admin.post(f"{base_url}/api/room", json=_payload(name), timeout=10)
    rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
    room_id = next(x["roomid"] for x in rooms if x["roomName"] == name)
    try:
        r = admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)
        assert r.status_code in (200, 202)
        rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        assert all(x["roomid"] != room_id for x in rooms)
    finally:
        admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)
