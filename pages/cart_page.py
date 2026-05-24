from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_table_rows = page.locator("table.table-striped tr")
        self.update_button = page.get_by_role("button", name="Update")
        self.delete_button = 'a[href*="remove"]'

    def navigate_via_top_bar(self) -> None:
        """
        Go to the Cart page from the top menu
        """
        self.cart_total_dropdown.click()

    def get_row_by_product_name(self, product_name: str) -> Locator:
        """
        Return the table row locator for the product
        """
        return self.cart_table_rows.filter(has_text=product_name)

    def update_product_quantity(self, product_name: str, new_quantity: int) -> None:
        """
        Find the row with the specified product name and set a new quantity
        """
        target_row = self.get_row_by_product_name(product_name)
        quantity_input = target_row.locator("input[id^='cart_quantity']")
        quantity_input.clear()
        quantity_input.fill(str(new_quantity))

        self.update_button.click()

    def delete_product(self, product_name: str) -> None:
        """
        Delete specified product from the cart
        """
        target_row = self.get_row_by_product_name(product_name)
        target_row.locator(self.delete_button).click()
