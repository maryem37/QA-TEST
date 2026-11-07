import pytest
import requests


@pytest.mark.tc("TC-006-03")
def test_room_101_is_single_and_available(base_url):
    """Vérifier que la chambre 101 est de type Single et disponible."""
    r = requests.get(f"{base_url}/api/room", timeout=10)
    assert r.status_code == 200, f"Unexpected status {r.status_code}"
    payload = r.json()
    assert "rooms" in payload, "Response JSON does not contain 'rooms' key"
    rooms = payload["rooms"]
    # rechercher la chambre 101
    matches = [room for room in rooms if room.get("roomName") == "101"]
    assert matches, "Room 101 not found in the list"
    room = matches[0]
    # vérifier le type
    assert room.get("type") == "Single", f"Room 101 type is {room.get('type')}, expected 'Single'"
    # aucune indication d'indisponibilité (si le champ existe, il doit être True)
    if "available" in room:
        assert room["available"] is True, "Room 101 is marked as unavailable"
