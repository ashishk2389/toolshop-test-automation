import logging
import re

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """Page Object for the Toolshop home / product catalog page.

    Covers global navigation, search, sorting, category/brand filtering,
    product catalog reads, and pagination.
    """

    HOME_URL = "https://practicesoftwaretesting.com"
    PAGE_TITLE = "Practice Software Testing - Toolshop"

    # Global nav
    NAV_HOME_LINK_NAME = "Home"
    DOCUMENTATION_LINK_NAME = "Documentation"
    CATEGORIES_BUTTON_NAME = "Categories"
    NAV_MENU_TEST_ID = "[data-test='nav-menu']"
    NAV_SIGN_IN_TEST_ID = "[data-test='nav-sign-in']"

    # Search & sort
    SEARCH_INPUT_TEST_ID = "[data-test='search-query']"
    SEARCH_SUBMIT_BUTTON_NAME = "Search"
    SEARCH_RESET_TEST_ID = "[data-test='search-reset']"
    SORT_DROPDOWN_NAME = "sort"

    # Product catalog
    PRODUCT_CARD_LINK_SELECTOR = "a[href*='/product/']"
    PRODUCT_NAME_TEST_ID = "[data-test='product-name']"
    PRODUCT_PRICE_TEST_ID = "[data-test='product-price']"
    PRODUCT_ECO_BADGE_TEST_ID = "[data-test='co2-rating-badge']"
    OUT_OF_STOCK_TEXT = "Out of stock"

    # Pagination
    PAGINATION_CONTAINER_SELECTOR = "ul.pagination"
    PAGINATION_PAGE_ITEM_SELECTOR = "li.page-item"

    def __init__(self, page):
        super().__init__(page)

    # --- Navigation & page-level validation ------------------------------

    def navigate_to_home_page(self):
        """Navigate the browser to the home page."""
        logger.info("Navigating to home page: %s", self.HOME_URL)
        self.navigate(self.HOME_URL)

    def verify_home_page_loaded(self):
        """Verify that the home page has loaded, via the Home nav link and page title."""
        logger.info("Verifying home page is loaded")
        expect(self.page.get_by_role("link", name=self.NAV_HOME_LINK_NAME)).to_be_visible()
        title_pattern = re.compile(re.escape(self.PAGE_TITLE.split(" - ")[0]), re.IGNORECASE)
        expect(self.page).to_have_title(title_pattern)

    def click_home_link(self):
        """Click the Home navigation link in the page header."""
        logger.debug("Clicking Home nav link")
        self.page.get_by_role("link", name=self.NAV_HOME_LINK_NAME).click()

    def click_documentation_link(self):
        """Click the Documentation navigation link in the page header."""
        logger.debug("Clicking Documentation nav link")
        self.page.get_by_role("link", name=self.DOCUMENTATION_LINK_NAME).click()

    def click_categories_button(self):
        """Click the Categories navigation button in the page header."""
        logger.debug("Clicking Categories nav button")
        self.page.get_by_role("button", name=self.CATEGORIES_BUTTON_NAME).click()

    def verify_user_signed_in(self, user_name: str):
        """Verify that the authenticated user name is visible in the header.

        Args:
            user_name: The expected display name of the signed-in user.
        """
        logger.info("Verifying user is signed in: %s", user_name)
        user_menu = self.page.locator(self.NAV_MENU_TEST_ID)
        expect(user_menu).to_be_visible(timeout=10000)
        expect(user_menu).to_contain_text(user_name)
        expect(self.page.locator(self.NAV_SIGN_IN_TEST_ID)).not_to_be_visible()

    def is_user_signed_in(self, user_name: str) -> bool:
        """Check whether the given user currently appears signed in, without asserting.

        Unlike ``verify_user_signed_in``, this does not raise on failure —
        it's intended for setup/fixture code that needs to branch on
        session state (e.g. "log in only if not already logged in").

        Args:
            user_name: The expected display name of the signed-in user.

        Returns:
            bool: True if the user's name or the account nav link is visible.
        """
        try:
            return (
                    self.page.get_by_text(user_name, exact=True).is_visible(timeout=3000)
                    or self.page.get_by_role("link", name="My account").is_visible(timeout=3000)
            )
        except PlaywrightTimeoutError:
            return False

    # --- Product catalog reads --------------------------------------------

    def get_displayed_product_names(self) -> list:
        """Return all visible product names in the current catalog grid.

        Returns:
            list[str]: Non-empty, whitespace-trimmed product names.
        """
        product_name_locator = self.page.locator(self.PRODUCT_NAME_TEST_ID)
        expect(product_name_locator.first).to_be_visible(timeout=10000)
        names = [name.strip() for name in product_name_locator.all_text_contents() if name and name.strip()]
        logger.debug("Displayed product names: %s", names)
        return names

    def get_first_product_name(self) -> str:
        """Return the text content of the first visible product card's name.

        Returns:
            str: The first product's name.
        """
        return (
            self.page.locator(self.PRODUCT_CARD_LINK_SELECTOR)
            .locator(self.PRODUCT_NAME_TEST_ID)
            .first.text_content()
        )

    def verify_first_product_name(self, expected_name="Adjustable Wrench"):
        """Wait for the grid to settle and assert the first product matches the expected name.

        Args:
            expected_name: The expected name of the first product in the grid.
        """
        first_product_locator = (
            self.page.locator(self.PRODUCT_CARD_LINK_SELECTOR)
            .locator(self.PRODUCT_NAME_TEST_ID)
            .first
        )
        expect(first_product_locator).to_have_text(expected_name)
        logger.debug("Verified first product name is '%s'", expected_name)

    def count_displayed_products(self) -> int:
        """Count how many product cards are currently visible on the page.

        Returns:
            int: The number of visible product cards.
        """
        product_name_locator = self.page.locator(self.PRODUCT_NAME_TEST_ID)
        expect(product_name_locator.first).to_be_visible(timeout=10000)
        count = product_name_locator.count()
        logger.debug("Displayed product count: %d", count)
        return count

    def get_all_displayed_product_prices(self) -> list:
        """Read all visible product prices and convert them to floats.

        Returns:
            list[float]: Product prices, e.g. "$14.15" becomes 14.15.
        """
        self.page.wait_for_selector(self.PRODUCT_CARD_LINK_SELECTOR)
        price_elements = self.page.locator(self.PRODUCT_PRICE_TEST_ID).all_text_contents()
        prices = [float(price.replace("$", "").strip()) for price in price_elements]
        logger.debug("Displayed product prices: %s", prices)
        return prices

    def get_first_product_eco_badge_text(self) -> str:
        """Return the eco badge text label for the first visible product card.

        Returns:
            str: The eco badge text.
        """
        eco_badge = self.page.locator(self.PRODUCT_CARD_LINK_SELECTOR).first.locator(self.PRODUCT_ECO_BADGE_TEST_ID)
        expect(eco_badge).to_be_visible()
        return eco_badge.text_content().strip()

    def verify_product_is_out_of_stock(self, product_index: int = 0):
        """Verify that at least one out-of-stock product exists, and check one of them.

        Args:
            product_index: Index into the set of out-of-stock cards to check
                (clamped to the last available card if out of range).
        """
        product_cards = self.page.locator(self.PRODUCT_CARD_LINK_SELECTOR)
        expect(product_cards.first).to_be_visible(timeout=10000)

        out_of_stock_cards = product_cards.filter(has_text=self.OUT_OF_STOCK_TEXT)
        out_of_stock_count = out_of_stock_cards.count()
        assert out_of_stock_count > 0, "No product cards with an out-of-stock badge were found."

        target_card = out_of_stock_cards.nth(min(product_index, out_of_stock_count - 1))
        expect(target_card).to_be_visible()
        expect(target_card).to_contain_text(self.OUT_OF_STOCK_TEXT)

    # --- Search & sort ----------------------------------------------------

    def get_search_input_value(self) -> str:
        """Read the current value of the search input field.

        Returns:
            str: The current search input value.
        """
        return self.page.locator(self.SEARCH_INPUT_TEST_ID).input_value()

    def search_product(self, query: str):
        """Enter a search query and wait for the filtered catalog to render.

        Args:
            query: The search keyword to filter products by.
        """
        logger.info("Searching for product: %s", query)
        search_field = self.page.locator(self.SEARCH_INPUT_TEST_ID)
        search_field.clear()
        search_field.fill(query)
        self.page.get_by_role("button", name=self.SEARCH_SUBMIT_BUTTON_NAME).click()
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(self.PRODUCT_NAME_TEST_ID).first).to_be_visible(timeout=10000)
        expect(
            self.page.locator(self.PRODUCT_NAME_TEST_ID).filter(has_text=re.compile(query, re.IGNORECASE)).first
        ).to_be_visible(timeout=10000)

    def reset_search_filters(self):
        """Clear the current search query and reload the catalog to its default state."""
        logger.info("Resetting search filters")
        search_field = self.page.locator(self.SEARCH_INPUT_TEST_ID)
        search_reset_button = self.page.locator(self.SEARCH_RESET_TEST_ID)

        if search_reset_button.count() > 0:
            search_reset_button.first.click()
            self.page.wait_for_timeout(500)

        search_field.clear()
        self.page.get_by_role("button", name=self.SEARCH_SUBMIT_BUTTON_NAME).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)
        expect(search_field).to_have_value("")
        expect(self.page.locator(self.PRODUCT_NAME_TEST_ID).first).to_be_visible(timeout=10000)

    def select_sort(self, option_value: str = "name,asc"):
        """Change the product ordering using the global sort dropdown.

        Args:
            option_value: One of "name,asc", "name,desc", "price,asc", "price,desc".
        """
        logger.info("Setting sort order: %s", option_value)
        self.page.get_by_role("combobox", name=self.SORT_DROPDOWN_NAME).select_option(option_value)

    # --- Sidebar filters ----------------------------------------------------

    def filter_by_category(self, category_name: str) -> bool:
        """Check a category checkbox by its visible label text, if not already checked.

        Args:
            category_name: The visible label text of the category checkbox.

        Returns:
            bool: True if the checkbox was toggled on by this call, False if
            it was already checked.
        """
        logger.info("Filtering by category: %s", category_name)
        checkbox = self.page.get_by_role("checkbox", name=category_name)
        expect(checkbox).to_be_visible(timeout=10000)

        was_checked = checkbox.is_checked()
        if not was_checked:
            checkbox.click()
            self.page.wait_for_timeout(500)

        expect(checkbox).to_be_checked(timeout=10000)
        return not was_checked

    def filter_by_brand(self, brand_name: str) -> bool:
        """Check a brand checkbox by its visible label text, if not already checked.

        Args:
            brand_name: The visible label text of the brand checkbox.

        Returns:
            bool: True if the checkbox was toggled on by this call, False if
            it was already checked.
        """
        logger.info("Filtering by brand: %s", brand_name)
        checkbox = self.page.get_by_role("checkbox", name=brand_name)
        expect(checkbox).to_be_visible(timeout=10000)

        was_checked = checkbox.is_checked()
        if not was_checked:
            checkbox.click()
            self.page.wait_for_timeout(500)

        expect(checkbox).to_be_checked(timeout=10000)
        return not was_checked

    # --- Pagination ---------------------------------------------------------

    def _get_pagination_item(self, page_number: str):
        """Locate a pagination item by its visible page number.

        Args:
            page_number: The page number label to match (e.g. "2").

        Returns:
            Locator: The pagination item matching the given page number.
        """
        pagination_nav = self.page.locator(self.PAGINATION_CONTAINER_SELECTOR)
        return pagination_nav.locator(self.PAGINATION_PAGE_ITEM_SELECTOR, has_text=page_number)

    def click_pagination_page(self, page_number: str):
        """Click a specific pagination item by its visible page number.

        Args:
            page_number: The page number label to click (e.g. "2").
        """
        logger.info("Clicking pagination page: %s", page_number)
        self._get_pagination_item(page_number).click()

    def verify_pagination_page_active(self, page_number: str):
        """Assert that a specific pagination item is currently marked as active.

        Args:
            page_number: The page number label expected to be active (e.g. "2").
        """
        logger.info("Verifying pagination page is active: %s", page_number)
        expect(self._get_pagination_item(page_number)).to_have_class(re.compile(r"\bactive\b"))