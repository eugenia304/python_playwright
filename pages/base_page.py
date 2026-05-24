from playwright.sync_api import Page, Locator, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

        # Header elements accessible from ANY page
        self.top_search_input: Locator = page.get_by_placeholder(
            "Search Keywords")
        self.top_search_button: Locator = page.locator("div.button-in-search")
        self.cart_total_dropdown: Locator = page.locator(
            ".block_7 .dropdown-toggle")
        self.main_menu_links: Locator = page.locator(
            "#categorymenu > nav > ul > li")
        self.cart_dropdown_trigger = page.locator(".block_7")
        # Items listed inside the cart dropdown
        self.dropdown_cart_items = page.locator(
            ".block_7 ul.dropdown-menu li .name")
        self.dropdown_cart_quantity = page.locator(
            ".block_7 ul.dropdown-menu li .quantity")

    def global_search(self, product_name: str) -> None:
        """
        Type product_name into the Search field and click the Search button
        """
        self.top_search_input.clear()
        self.top_search_input.fill(product_name)
        self.top_search_button.click()

    def verify_page_title(self, expected_title: str) -> None:
        """
        Verify that the page title is expected_title
        """
        expect(self.page).to_have_title(expected_title)

    def get_cart_item_count(self) -> int:
        """
        Get number of items in the cart dropdown
        """
        cart_text = self.cart_total_dropdown.inner_text()
        # Extract the first segment before the space to get the count digit
        try:
            return int(cart_text.split()[0])
        except (ValueError, IndexError):
            return 0

    def hover_over_cart_dropdown(self) -> None:
        """
        Hover over the cart dropdown
        """
        self.cart_dropdown_trigger.hover()
