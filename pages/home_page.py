from pages.base_page import BasePage
from playwright.sync_api import expect


class HomePage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    # Core Page Data Constants
    PAGE_TITLE = "Practice Software Testing - Toolshop"
    DOCUMENTATION = "Documentation"
    HOME = "Home"
    CATEGORIES = "Categories"

    # --- Locators Mapping (Using explicit data-test identifiers from the HTML) ---
    # Global Nav
    _nav_home = "nav-home"
    _nav_contact = "nav-contact"
    _nav_user_menu = "nav-menu"

    # Search & Sort Elements
    _search_input = "search-query"
    _search_submit = "search-submit"
    _search_reset = "search-reset"
    _sort_dropdown = "sort"

    # Filter Sidebar Elements
    _price_slider = ".ngx-slider-span"  # Class selector for dual price slider tracks
    _category_checkbox = "label:has-text('{name}') input[type='checkbox']"
    _brand_checkbox = "label:has-text('{name}') input[type='checkbox']"

    # Product Catalog Elements
    _product_grid_cards = "[data-test^='product-']"
    _product_name = "product-name"
    _product_price = "product-price"
    _product_out_of_stock = ".col-sm-12:has-text('Out of stock')"  # Context tracking indicator
    _product_eco_badge = ".badge"  # Captures the green/orange CO2 emission pill indicator

    # Pagination Elements
    _pagination_container = "ul.pagination"
    _pagination_page_item = "li.page-item"

    # --- Page Action & Verification Methods ---

    def verify_home_page_loaded(self):
        self.page.get_by_title(self.PAGE_TITLE).is_visible()

    def navigateToHomePage(self):
        self.navigate("https://practicesoftwaretesting.com")

    def verify_documentation_link_working(self):
        self.page.get_by_role("link", name=self.DOCUMENTATION).click()

    def verify_home_link_working(self):
        self.page.get_by_role("link", name=self.HOME).click()

    def verify_categories_link_working(self):
        self.page.get_by_role("button", name=self.CATEGORIES).click()

    # --- New Functionality: Search & Sort Frameworks ---

    def search_product(self, query: str):
        """Types keyword criteria into search and executes query filtering."""
        search_field = self.page.get_by_test_id(self._search_input)
        search_field.clear()
        search_field.fill(query)
        self.page.get_by_test_id(self._search_submit).click()

    def reset_search_filters(self):
        """Clears current active text query updates using the reset button identifier."""
        self.page.get_by_test_id(self._search_reset).click()

    def select_sort(self, option_value="name,asc"):
        """Changes the ordering sequence rule using the global sort selector box.

        Valid options: 'name,asc', 'name,desc', 'price,asc', 'price,desc'
        """
        self.page.get_by_test_id(self._sort_dropdown).select_option(option_value)

    # --- New Functionality: Left-Side Filter Checkbox Automation ---

    def filter_by_category(self, category_name: str):
        """Dynamically tracks down category label names to assert or flip checked statuses."""
        checkbox = self.page.locator(
            self._category_checkbox.format(name=category_name)
        )
        if not checkbox.is_checked():
            checkbox.click()

    def filter_by_brand(self, brand_name: str):
        """Tracks brand label boxes to securely engage checkbox criteria filters."""
        checkbox = self.page.locator(self._brand_checkbox.format(name=brand_name))
        if not checkbox.is_checked():
            checkbox.click()

    # --- New Functionality: Data Retrieval & Assertions Layout ---

    def get_first_element(self):
        """Extract the text content of the first visible product item container title."""
        return (
            self.page.locator(self._product_grid_cards)
            .get_by_test_id(self._product_name)
            .first.text_content()
        )

    def verify_first_element_displayed(self, expected_name="Adjustable Wrench"):
        """Waits for the grid to update and asserts that the first visible product
        matches the expected product title string.
        """
        # 1. Target the first product name locator explicitly
        first_product_locator = (
            self.page.locator(self._product_grid_cards)
            .get_by_test_id(self._product_name)
            .first
        )

        # 2. Use Playwright's expect tool to robustly handle web loading delays
        expect(first_product_locator).to_have_text(expected_name)

        # Optional: Log the validated text to your test run output console
        print(f"Verified successfully: First element text is '{first_product_locator.text_content().strip()}'")

    def get_all_displayed_product_prices(self) -> list:
        """Scrapes the active grid display array to collect product prices as integers/floats."""
        self.page.wait_for_selector(self._product_grid_cards)
        price_elements = self.page.get_by_test_id(self._product_price).all_text_contents()
        # Converts pricing string structures (e.g. '$14.15') directly to numeric floats for testing sorting logic
        return [float(price.replace("$", "").strip()) for price in price_elements]

    def verify_product_is_out_of_stock(self, product_index=0):
        """Checks if a specified product index shows an explicit 'Out of stock' flag badge context."""
        target_card = self.page.locator(self._product_grid_cards).nth(product_index)
        expect(target_card.locator(self._product_out_of_stock)).to_be_visible()

    # --- New Functionality: UI Component Pagination Operations ---

    def click_pagination_page(self, page_number: str):
        """Target links matching explicit numerical counts on the grid pagination footer bar."""
        pagination_nav = self.page.locator(self._pagination_container)
        page_anchor = pagination_nav.locator(
            self._pagination_page_item, has_text=page_number
        )
        page_anchor.click()