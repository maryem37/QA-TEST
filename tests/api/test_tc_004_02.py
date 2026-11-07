import uuid

import pytest


def _room_payload(name):
    return {
        "roomName": name,
        "type": "Single",
        "accessible": False,
        "description": "Created by automated test",
        "features": ["WiFi"],
        "image": "/images/room1.jpg",
        "roomPrice": 123,
    }


@pytest.mark.tc("TC-004-02")
def test_modify_room_invalid_price(base_url, admin):
    name = f"QA-{uuid.uuid4().hex[:6]}"
    room_id = None
    try:
        # Create a room
        r = admin.post(f"{base_url}/api/room", json=_room_payload(name), timeout=10)
        assert r.status_code == 200

        # Retrieve its id and original price
        rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        match = next((x for x in rooms if x["roomName"] == name), None)
        assert match is not None
        room_id = match["roomid"]
        original_price = match["roomPrice"]

        # Attempt to modify with a non‑numeric price
        payload = _room_payload(name)
        payload["roomPrice"] = "invalid_price"
        r_put = admin.put(f"{base_url}/api/room/{room_id}", json=payload, timeout=10)

        # The request must be rejected (any non‑success status)
        assert r_put.status_code not in (200, 202)

        # Verify that the price has not changed
        rooms_after = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        room_after = next(x for x in rooms_after if x["roomid"] == room_id)
        assert room_after["roomPrice"] == original_price
    finally:
        if room_id is not None:
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)
