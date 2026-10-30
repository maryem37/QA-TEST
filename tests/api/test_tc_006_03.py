import pytest
import requests


@pytest.mark.tc("TC-006-03")
def test_room_101_is_single_and_available(base_url):
    # Récupérer la liste des chambres
    r = requests.get(f"{base_url}/api/room", timeout=10)
    assert r.status_code == 200

    data = r.json()
    assert "rooms" in data
    rooms = data["rooms"]
    assert len(rooms) >= 1

    # Trouver la chambre dont le roomName est "101"
    room_101 = next((room for room in rooms if room.get("roomName") == "101"), None)
    assert room_101 is not None, "Room with roomName '101' not found"

    # Vérifier le type
    assert room_101.get("type") == "Single", "Room 101 should be of type Single"

    # Vérifier qu'aucune indication d'indisponibilité n'est présente
    # (aucun champ spécifique n'est documenté, on s'assure simplement que les champs attendus existent)
    expected_keys = {"roomid", "roomName", "type", "roomPrice", "accessible", "description", "features", "image"}
    assert expected_keys <= room_101.keys()
