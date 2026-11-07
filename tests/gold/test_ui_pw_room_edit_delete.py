import uuid

import pytest
from playwright.sync_api import Page


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
            "description": "Chambre de test automatique",
            "image": "/images/room1.jpg",
            "roomPrice": 100,
            "features": ["WiFi"],
        },
        timeout=10,
    )
    assert r.ok
    rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
    return next(x["roomid"] for x in rooms if x["roomName"] == name)


def _get_room(admin, base_url, room_id: int):
    rooms = admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"]
    return next((x for x in rooms if x["roomid"] == room_id), None)


@pytest.mark.tc("TC-904-01")
def test_admin_deletes_room_via_ui(page: Page, base_url, admin):
    name = f"QA{uuid.uuid4().hex[:5]}"
    room_id = _create_room(admin, base_url, name)
    try:
        _login(page)
        row = page.get_by_test_id("roomlisting").filter(has_text=name)
        with page.expect_response(
            lambda r: r.request.method == "DELETE" and "/api/room" in r.url
        ) as deleted:
            row.locator(".roomDelete").click()
        assert deleted.value.ok
        assert _get_room(admin, base_url, room_id) is None
    finally:
        if _get_room(admin, base_url, room_id):
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)


@pytest.mark.tc("TC-904-02")
def test_admin_edits_room_price_via_ui(page: Page, base_url, admin):
    name = f"QA{uuid.uuid4().hex[:5]}"
    room_id = _create_room(admin, base_url, name)
    try:
        _login(page)
        row = page.get_by_test_id("roomlisting").filter(has_text=name)
        row.get_by_text(name).click()
        page.get_by_role("button", name="Edit").click()
        page.get_by_role("textbox", name="Room price:").fill("345")
        with page.expect_response(
            lambda r: r.request.method == "PUT" and "/api/room/" in r.url
        ) as updated:
            page.get_by_role("button", name="Update").click()
        assert updated.value.ok
        assert _get_room(admin, base_url, room_id)["roomPrice"] == 345
    finally:
        if _get_room(admin, base_url, room_id):
            admin.delete(f"{base_url}/api/room/{room_id}", timeout=10)
