import re
import pytest
import allure

from playwright.sync_api import Page, expect
from urllib.parse import quote

from pages.home_page import HomePage


@allure.epic("Search Workflow")
@allure.story("Search for existing or non existing product")
@pytest.mark.parametrize(
    "search_item, exp_res, exp_text",
    [
        ("Skinsheen", "single", "Skinsheen"),
        ("Shampoo", "multi", "Shampoo"),
        ("XYZ", "error",
         "There is no product that matches the search criteria."),
        ("'; DROP TABLE Products;--", "error",
         "There is no product that matches the search criteria.")
    ]
)
def test_search_products(page: Page, search_item, exp_res, exp_text):
    """
    If exactly 1 item found - the site redirects user to the product page
    If more than 1 item found - the product cards are listed and the URL contains search text
    If no items found - 'There is no product that matches the search criteria.' message displayed
    """
    home_page = HomePage(page)
    home_page.navigate()
    home_page.global_search(search_item)

    encoded_item = quote(search_item)

    if exp_res == 'single':
        expect(page).to_have_url(re.compile(r'product_id='))
        expect(home_page.product_cards).not_to_be_visible()
        expect(home_page.product_details_title).to_contain_text(encoded_item)

    if exp_res == 'multi':
        expect(page).to_have_url(re.compile(
            rf"keyword={re.escape(encoded_item)}"))
        expect(home_page.product_cards.first).to_be_visible()
        first_product_title = home_page.product_cards.first.locator(
            "a.prdocutname")
        expect(first_product_title).to_contain_text(exp_text, ignore_case=True)

    if exp_res == 'error':
        expect(page).to_have_url(re.compile(
            rf"keyword={re.escape(encoded_item)}"))
        expect(home_page.search_error_msg).to_contain_text(exp_text)
        expect(home_page.product_cards).not_to_be_visible()
