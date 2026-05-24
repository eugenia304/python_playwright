import allure
import pytest
import re

from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.cart_page import CartPage

pytestmark = pytest.mark.parametrize("user_state", ["guest", "logged_in"])


@allure.epic("Cart Workflow")
@allure.story("Add item to cart")
def test_add_item_and_verify_dropdown(page: Page, user_state: str) -> None:
    """
    Verify that a guest/logged in user can add an item multiple times
    Steps:
    1. Add an item to the cart
    2. Check that the added_to_cart class is added to the selected item
    3. Check that the cart tab was updated and says 1
    4. Hover over the cart tab and check that it displays correct number of items
    5. Add the same item again and repeat the steps 3 and 4
    """
    print(f"Running test as a: {user_state} user")
    home_page = HomePage(page)
    home_page.navigate()

    # Pre-Conditions: Guest user, Home page, Empty cart
    assert home_page.get_cart_item_count() == 0

    select_product = home_page.get_product_name_by_index(
        index=0, section_name='Featured')

    # Add an item to the cart
    home_page.add_product_to_cart_by_name(
        name=select_product, section_name='Featured')

    feat_product_cards = home_page.get_product_cards(section_name='Featured')

    # Verify added_to_cart class is appended to the element
    product_wrapper = feat_product_cards.filter(has_text=select_product)
    price_container = product_wrapper.locator('div.pricetag')
    expect(price_container).to_have_attribute(
        "class", re.compile(r"added_to_cart"))

    # Verify main header dropdown counter is 1
    assert home_page.get_cart_item_count() == 1

    # Hover on cart dropdown and verify item count
    home_page.hover_over_cart_dropdown()
    expect(home_page.dropdown_cart_quantity.first).to_contain_text("1")

    # Add the same item to the cart one more time
    home_page.add_product_to_cart_by_name(
        name=select_product, section_name='Featured')

    # Verify main header dropdown counter is 2
    assert home_page.get_cart_item_count() == 2

    # Hover on cart dropdown and verify item count
    home_page.hover_over_cart_dropdown()
    expect(home_page.dropdown_cart_quantity.first).to_contain_text("2")


@allure.epic("Cart Workflow")
@allure.story("Change item quantity in the cart")
def test_change_quantity(page: Page, user_state: str) -> None:
    """
    Verify that a guest/logged in user can change the quantity of an item in the cart
    Steps:
    1. Add an item to the cart
    2. Open the Cart page via top menu
    3. Set new product quantity and click Update
    """
    print(f"Running test as a: {user_state} user")
    home_page = HomePage(page)
    cart_page = CartPage(page)
    home_page.navigate()
    select_product = home_page.get_product_name_by_index(
        0, section_name='Featured')

    # Step 1: Add an item to the cart the first time
    home_page.add_product_to_cart_by_name(
        name=select_product, section_name='Featured')

    cart_page.navigate_via_top_bar()
    expect(page).to_have_url(re.compile(r"checkout/cart"))

    product_row = cart_page.get_row_by_product_name(select_product)
    expect(product_row).to_be_visible()

    # update quantity
    new_qty = 3
    cart_page.update_product_quantity(
        product_name=select_product, new_quantity=new_qty)
    assert cart_page.get_cart_item_count() == new_qty

    quantity_input = product_row.locator("input[id^='cart_quantity']")
    expect(quantity_input).to_have_value(str(new_qty))


@allure.epic("Cart Workflow")
@allure.story("Delete item from the cart")
def test_delete_item(page: Page, user_state: str) -> None:
    """
    Verify that a guest/logged in user can delete an item from the cart
    Steps:
    1. Add an item to the cart
    2. Open the Cart page via top menu
    3. Click the bin icon
    """
    print(f"Running test as a: {user_state} user")
    home_page = HomePage(page)
    cart_page = CartPage(page)
    home_page.navigate()
    select_product = home_page.get_product_name_by_index(
        0, section_name='Featured')

    # Step 1: Add an item to the cart the first time
    home_page.add_product_to_cart_by_name(
        name=select_product, section_name='Featured')

    cart_page.navigate_via_top_bar()
    expect(page).to_have_url(re.compile(r"checkout/cart"))

    product_row = cart_page.get_row_by_product_name(select_product)
    expect(product_row).to_be_visible()
    cart_page.delete_product(select_product)

    expect(product_row).not_to_be_visible()
