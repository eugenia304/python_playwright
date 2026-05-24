from playwright.sync_api import Page, Locator, expect
from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page):
        # Call the parent BasePage constructor to initialize global locators
        super().__init__(page)
        self.url = "/"

        # Product boxes
        self.product_cards: Locator = page.locator(
            ".thumbnails > div")
        # Search page error message (no products found)
        self.search_error_msg = page.locator(".contentpanel")
        # Product details page > Product title
        self.product_details_title = page.locator('h1.productname > span')

        # Home page product sections
        self._section_map = {
            "featured": "#featured",
            "latest": "#latest",
            "bestsellers": "#bestseller",
            "specials": "#special"
        }

    def navigate(self) -> None:
        """
        Go to the home page
        """
        self.page.goto(self.url)

    def get_product_cards(self, section_name: str = '') -> Locator:
        """
        Get product cards from the specified section (on the home page).
        Omit the section_name value if using this method on Search page
        """
        # Lowercase the key input to avoid casing mismatches
        key = section_name.lower().strip()

        if not key or key not in self._section_map:
            return self.product_cards

        # Get the specific container ID string (e.g., "#featured")
        section_id = self._section_map[key]

        # Chain the selectors dynamically to scope down to that exact container block
        return self.page.locator(section_id).locator(".thumbnails > div")

    def click_product_by_name(self, name: str, section_name: str = '') -> None:
        """
        Click product inside the specified section
        Omit the section_name value if using this method on Search page
        """
        cards = self.get_product_cards(section_name)
        target_card = cards.filter(has_text=name)
        target_card.locator("a.prdocutname").click()

    def add_product_to_cart_by_name(self, name: str, section_name: str = '') -> None:
        """
        Add product from the specified section to the cart
        Omit the section_name value if using this method on Search page
        """
        cards = self.get_product_cards(section_name)
        target_card = cards.filter(has_text=name)
        target_card.locator("a.productcart").click()

    def get_product_name_by_index(self, index: int, section_name: str = '') -> str:
        """
        Get product name from the specified section by its index (the 1st product has index 0)
        Omit the section_name value if using this method on Search page
        """
        cards = self.get_product_cards(section_name)
        target_card = cards.nth(index)

        target_title_locator = target_card.locator("a.prdocutname")
        expect(target_title_locator).to_be_visible()
        return target_title_locator.inner_text().strip()

    def get_num_of_items(self, section_name: str = '') -> int:
        """
        Return number of items displayed in the grid
        """
        items_num = self.get_product_cards(self, section_name=section_name)
        return items_num.count()
