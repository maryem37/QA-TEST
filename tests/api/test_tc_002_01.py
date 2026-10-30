import pytest
import requests


@pytest.mark.tc("TC-002-01")
def test_get_room_list_returns_rooms(base_url):
    # Envoi de la requête GET sur l'endpoint /api/room
    r = requests.get(f"{base_url}/api/room", timeout=10)

    # Vérification du code HTTP attendu
    assert r.status_code == 200

    # Vérification de la présence de la clé "rooms" dans le corps JSON
    json_body = r.json()
    assert "rooms" in json_body
    rooms = json_body["rooms"]
    assert isinstance(rooms, list)

    # Au moins une chambre doit être retournée (les notes indiquent 3 initiales)
    assert len(rooms) >= 1

    # Vérification de la forme de chaque objet chambre
    for room in rooms:
        assert isinstance(room, dict)
        # Les champs requis pour ce cas de test
        assert "type" in room
        assert "roomPrice" in room
        # Valeurs non nulles et du bon type
        assert isinstance(room["type"], str) and room["type"]
        assert isinstance(room["roomPrice"], int)
