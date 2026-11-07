import uuid

import pytest
import requests


def _room_payload(name, price):
    return {
        "roomName": name,
        "type": "Single",
        "accessible": False,
        "description": "Created by automated test",
        "features": ["WiFi"],
        "image": "https://www.mwtestconsultancy.co.uk/img/room1.jpg",
        "roomPrice": price,
    }


@pytest.mark.tc("TC-004-02")
def test_modify_room_invalid_price(base_url, admin, admin_token, room_direct_url):
    # Crée une chambre de test avec un prix valide
    name = f"QA-{uuid.uuid4().hex[:6]}"
    room_id = None
    try:
        # création
        r = admin.post(
            f"{base_url}/api/room",
            json=_room_payload(name, 123),
            timeout=10,
        )
        assert r.status_code == 200

        # récupération de l'ID
        rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        match = [x for x in rooms if x["roomName"] == name]
        assert len(match) == 1
        room_id = match[0]["roomid"]
        original_price = match[0]["roomPrice"]
        assert original_price == 123

        # tentative de modification avec un prix non numérique
        invalid_payload = _room_payload(name, "invalid_price")
        r_put = requests.put(
            f"{base_url}/api/room/{room_id}",
            json=invalid_payload,
            headers={"Cookie": f"token={admin_token}"},
            timeout=10,
        )
        # le serveur doit refuser la modification (code d'erreur)
        assert r_put.status_code >= 400

        # vérification que le prix n'a pas changé
        rooms_after = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        after_match = [x for x in rooms_after if x["roomid"] == room_id]
        assert len(after_match) == 1
        assert after_match[0]["roomPrice"] == original_price

    finally:
        # suppression de la chambre via la passerelle directe
        if room_id is not None:
            try:
                requests.delete(
                    f"{room_direct_url}/api/room/{room_id}",
                    headers={"Cookie": f"token={admin_token}"},
                    timeout=10,
                )
            except Exception:
                pass
