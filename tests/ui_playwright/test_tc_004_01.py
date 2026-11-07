import uuid

import pytest
from playwright.sync_api import Page, expect


def _login(page: Page) -> None:
    page.goto("/admin")
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("password")
    page.get_by_role("button", name="Login").click()


def _create_room(admin, base_url, name: str) -> int:
    r = admin.post(
        f"{base_url}/api/room",
        json={
            "roomName": name,
            "type": "Single",
            "accessible": True,
            "description": "Room created for UI edit test",
            "image": "/images/room_test.jpg",
            "roomPrice": 100,
            "features": [],
        },
        timeout=10,
    )
    assert r.ok, "room creation via API failed"
    rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
    return next(x["roomid"] for x in rooms if x["roomName"] == name)


def _get_room(admin, base_url, room_id: int):
    rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
    return next((x for x in rooms if x["roomid"] == room_id), None)


@pytest.mark.tc("TC-004-01")
def test_admin_modifies_room_price_via_ui(page: Page, base_url, admin):
    # Précondition : création d'une chambre de test via l'API
    name = f"QA{uuid.uuid4().hex[:6]}"
    room_id = _create_room(admin, base_url, name)

    try:
        # Étape 1 : connexion et vérification de la présence de la chambre
        _login(page)
        expect(page).to_have_url(f"{base_url}/admin/rooms")
        row = page.get_by_test_id("roomlisting").filter(has_text=name)
        expect(row).to_be_visible()

        # Étape 2 : édition du prix
        row.get_by_text(name).click()
        page.get_by_role("button", name="Edit").click()
        page.get_by_role("textbox", name="Room price:").fill("345")
        with page.expect_response(
            lambda r: r.request.method == "PUT" and "/api/room/" in r.url
        ) as updated:
            page.get_by_role("button", name="Update").click()
        assert updated.value.ok, "PUT /api/room/<id> did not succeed"

        # Vérification côté API du nouveau prix
        updated_room = _get_room(admin, base_url, room_id)
        assert updated_room is not None, "room disappeared after update"
        assert updated_room["roomPrice"] == 345, "price not updated in API"
    finally:
        # Nettoyage : suppression de la chambre de test
        if _get_room(admin, base_url, room_id):
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)
