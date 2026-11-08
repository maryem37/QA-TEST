import pytest
import requests


@pytest.mark.tc("TC-002-03")
def test_room_list_accessible_without_auth(base_url):
    """
    Verify that the list of rooms can be retrieved without authentication.
    Expected: 200 response and each room entry contains 'type' and 'roomPrice'.
    """
    response = requests.get(f"{base_url}/api/room", timeout=10)
    assert response.status_code == 200, f"Unexpected status {response.status_code}"
    data = response.json()
    assert "rooms" in data, "Response JSON does not contain 'rooms' key"
    rooms = data["rooms"]
    assert isinstance(rooms, list), "'rooms' should be a list"
    assert len(rooms) > 0, "Rooms list is empty"
    for room in rooms:
        assert isinstance(room, dict), "Each room entry should be a dict"
        assert "type" in room, "Room entry missing 'type' field"
        assert "roomPrice" in room, "Room entry missing 'roomPrice' field"
        # Optional sanity checks on field types
        assert isinstance(room["type"], str), "'type' should be a string"
        assert isinstance(room["roomPrice"], int), "'roomPrice' should be an integer"
