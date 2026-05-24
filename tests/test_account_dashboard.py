import re
import allure
import pytest

from playwright.sync_api import Page, expect


@allure.epic("Account page")
@allure.story("Logged in user should see My Account page")
@pytest.mark.parametrize("user_state", ["logged_in"])
def test_account_page_logged_in_user(page: Page, user_state) -> None:
    """
    Auth performed via API
    Check that the user is logged in and the page header is correct
    """
    page.goto("/index.php?rt=account/account")

    expect(page).to_have_url(re.compile(r"index\.php\?rt=account/account"))

    welcome_header = page.locator(".maintext")
    expect(welcome_header).to_contain_text("My Account")
