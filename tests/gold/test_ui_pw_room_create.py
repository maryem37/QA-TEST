import uuid

import pytest
from playwright.sync_api import Page


def _login(page: Page) -> None:
    page.goto("/admin")
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("password")
    page.get_by_role("button", name="Login").click()


@pytest.mark.tc("TC-902-01")
def test_admin_creates_room_via_ui(page: Page, base_url, admin):
    name = f"QA{uuid.uuid4().hex[:5]}"
    _login(page)

    page.get_by_test_id("roomName").fill(name)
    page.locator("#accessible").select_option("true")
    page.locator("#roomPrice").fill("234")
    page.get_by_role("checkbox", name="WiFi").check()
    page.get_by_role("checkbox", name="Safe").check()
    page.get_by_role("checkbox", name="TV").check()

    with page.expect_response(
        lambda r: r.request.method == "POST" and "/api/room" in r.url
    ) as created:
        page.get_by_role("button", name="Create").click()
    assert created.value.ok

    room_id = None
    try:
        rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
        found = [r for r in rooms if r["roomName"] == name]
        assert found, f"la chambre {name} n'a pas été créée"
        room_id = found[0]["roomid"]
        assert found[0]["roomPrice"] == 234
        assert found[0]["accessible"] is True
        assert {"WiFi", "Safe", "TV"} <= set(found[0]["features"])
    finally:
        if room_id is not None:
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)