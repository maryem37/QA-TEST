import uuid

import pytest
from playwright.sync_api import Page, expect


def _login(page: Page) -> None:
    page.goto("/admin")
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("password")
    page.get_by_role("button", name="Login").click()


def _room_count(admin, base_url) -> int:
    return len(admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"])


@pytest.mark.tc("TC-902-02")
@pytest.mark.parametrize(
    ("name", "price", "message"),
    [
        ("", "100", "Room name must be set"),
        ("QA-invalid", "debhh", "Failed to create room"),
    ],
    ids=["numero_vide", "prix_invalide"],
)
def test_invalid_room_is_rejected_via_ui(page: Page, base_url, admin, name, price, message):
    before = _room_count(admin, base_url)
    _login(page)

    if name:
        page.get_by_test_id("roomName").fill(f"{name}-{uuid.uuid4().hex[:4]}")
    page.locator("#roomPrice").fill(price)
    page.get_by_role("button", name="Create").click()

    expect(page.get_by_text(message)).to_be_visible()
    assert _room_count(admin, base_url) == before