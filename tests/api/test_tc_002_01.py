import pytest
import requests


@pytest.mark.tc("TC-002-01")
def test_get_room_list_contains_type_and_price(base_url):
    r = requests.get(f"{base_url}/api/room", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "rooms" in data
    rooms = data["rooms"]
    assert isinstance(rooms, list)
    assert len(rooms) >= 1
    for room in rooms:
        # required fields must exist and be non‑null
        for key in ("type", "roomPrice"):
            assert key in room
            assert room[key] is not None
        # type must be a non‑empty string
        assert isinstance(room["type"], str)
        assert room["type"]
        # roomPrice must be an integer and positive
        assert isinstance(room["roomPrice"], int)
        assert room["roomPrice"] > 0
