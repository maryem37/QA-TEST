import uuid

import pytest
from playwright.sync_api import Page


def _login(page: Page) -> None:
    page.goto("/admin")
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("password")
    page.get_by_role("button", name="Login").click()


@pytest.mark.tc("TC-003-01")
def test_admin_creates_valid_room_via_ui(page: Page, base_url, admin):
    # generate a unique room name
    room_name = f"QA-{uuid.uuid4().hex[:8]}"

    # login as admin
    _login(page)

    # fill the creation form
    page.get_by_test_id("roomName").fill(room_name)
    page.locator("#accessible").select_option("true")
    page.locator("#roomPrice").fill("120")
    page.get_by_role("checkbox", name="WiFi").check()

    # submit and wait for the POST /api/room response
    with page.expect_response(
        lambda r: r.request.method == "POST" and "/api/room" in r.url
    ) as created:
        page.get_by_role("button", name="Create").click()
    assert created.value.ok, "La requête de création n'a pas renvoyé un statut 200"

    room_id = None
    try:
        # verify via API that the room exists with the expected attributes
        rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        matching = [r for r in rooms if r["roomName"] == room_name]
        assert matching, f"La chambre {room_name} n'a pas été créée côté API"
        room = matching[0]
        room_id = room["roomid"]
        assert room["type"] == "Single", "Le type de la chambre n'est pas Single"
        assert room["roomPrice"] == 120, "Le prix de la chambre n'est pas 120"
        assert room["accessible"] is True, "L'accessibilité n'est pas true"
        assert "WiFi" in room["features"], "L'équipement WiFi n'est pas présent"
    finally:
        # cleanup: delete the created room if we obtained its id
        if room_id is not None:
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)
