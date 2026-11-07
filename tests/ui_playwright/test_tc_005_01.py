import uuid

import pytest
from playwright.sync_api import Page, expect


def _login(page: Page) -> None:
    page.goto("/admin")
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("password")
    page.get_by_role("button", name="Login").click()


def _create_room(admin, base_url, name: str) -> int:
    """Create a room via the API and return its roomid."""
    resp = admin.post(
        f"{base_url}/api/room",
        json={
            "roomName": name,
            "type": "Single",
            "accessible": True,
            "description": "Room created for UI delete test",
            "image": "/images/room1.jpg",
            "roomPrice": 100,
            "features": ["WiFi"],
        },
        timeout=10,
    )
    assert resp.ok, "API room creation failed"
    rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
    return next(r["roomid"] for r in rooms if r["roomName"] == name)


def _room_exists(admin, base_url, room_id: int) -> bool:
    rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
    return any(r["roomid"] == room_id for r in rooms)


@pytest.mark.tc("TC-005-01")
def test_admin_deletes_room_via_ui(page: Page, base_url, admin):
    # Préparer une chambre de test via l'API
    room_name = f"QA{uuid.uuid4().hex[:6]}"
    room_id = _create_room(admin, base_url, room_name)

    try:
        # Connexion admin
        _login(page)

        # Vérifier que la ligne de la chambre apparaît dans le tableau
        row = page.get_by_test_id("roomlisting").filter(has_text=room_name)
        expect(row).to_be_visible()

        # Supprimer la chambre via l'UI
        with page.expect_response(
            lambda r: r.request.method == "DELETE" and "/api/room" in r.url
        ) as deleted:
            row.locator(".roomDelete").click()
        assert deleted.value.ok, "DELETE request did not succeed"

        # La ligne doit disparaître de l'interface
        expect(row).to_be_hidden()

        # Vérifier côté API que la chambre n'existe plus
        rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        assert not any(r["roomName"] == room_name for r in rooms), "Room still present via API"
    finally:
        # Nettoyage au cas où la suppression UI aurait échoué
        if _room_exists(admin, base_url, room_id):
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)
