import pytest
from playwright.sync_api import Page, expect


def _login(page: Page) -> None:
    page.goto("/admin")
    page.get_by_role("textbox", name="Username").fill("admin")
    page.get_by_role("textbox", name="Password").fill("password")
    page.get_by_role("button", name="Login").click()


def _room_count(admin, base_url: str) -> int:
    return len(admin.get(f"{base_url}/api/room", timeout=10).json()["rooms"])


@pytest.mark.tc("TC-003-02")
def test_refuse_creation_empty_number_invalid_price(page: Page, base_url, admin):
    before = _room_count(admin, base_url)

    _login(page)

    # numéro laissé vide
    page.locator("#roomPrice").fill("abc")
    page.get_by_role("button", name="Create").click()

    expect(page.get_by_text("Failed to create room")).to_be_visible()
    assert _room_count(admin, base_url) == before
