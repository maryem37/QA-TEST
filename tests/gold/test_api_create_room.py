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


@pytest.mark.tc("TC-002-02")
def test_create_room_then_visible_in_list(base_url, admin, room_direct_url):
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
        # Nettoyage via le service direct : la passerelle échoue (DEF-003)
        if room_id is not None:
            admin.delete(f"{room_direct_url}/room/{room_id}", timeout=10)


@pytest.mark.tc("TC-002-03")
def test_create_room_without_token_is_rejected(base_url):
    r = requests.post(f"{base_url}/api/room", json=_payload("QA-NOAUTH"), timeout=10)
    assert r.status_code == 401


@pytest.mark.tc("TC-003-01")
@pytest.mark.xfail(reason="DEF-003 : DELETE /api/room/{id} renvoie 500 via la passerelle", strict=True)
def test_delete_room_succeeds(base_url, admin, room_direct_url):
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
        # La chambre reste en base tant que DEF-003 existe : nettoyage direct
        admin.delete(f"{room_direct_url}/room/{room_id}", timeout=10)