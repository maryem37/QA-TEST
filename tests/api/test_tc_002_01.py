import pytest
import requests


@pytest.mark.tc("TC-002-01")
def test_get_room_list_returns_valid_rooms(base_url):
    response = requests.get(f"{base_url}/api/room", timeout=10)
    assert response.status_code == 200

    data = response.json()
    assert "rooms" in data
    rooms = data["rooms"]
    assert isinstance(rooms, list)
    assert len(rooms) >= 1

    for room in rooms:
        # Required fields
        assert "type" in room
        assert "roomPrice" in room

        # Type checks and non‑null values
        assert isinstance(room["type"], str)
        assert room["type"]  # non‑empty string

        assert isinstance(room["roomPrice"], int)
        # Assuming price should be positive
        assert room["roomPrice"] > 0
