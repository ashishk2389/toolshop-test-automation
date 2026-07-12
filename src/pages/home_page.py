from src.pages.base_page import BasePage
from playwright.sync_api import expect
import re


class HomePage(BasePage):

    def __init__(self, page):
        super().__init__(page)


# Core Page Data Constants
    PAGE_TITLE = "Practice Software Testing - Toolshop"
    DOCUMENTATION = "Documentation"
    HOME = "Home"
    CATEGORIES = "Categories"

    # --- Locators Mapping (Using the current accessible UI) ---
    # Global Nav
    _nav_home = "Home"
    _nav_contact = "Contact"
    _nav_user_menu = "Jane Doe"
    _nav_menu = "[data-test='nav-menu']"

    # Search & Sort Elements
    _search_input = "[data-test='search-query']"
    _search_submit = "Search"
    _search_reset = "X"
    _sort_dropdown = "sort"

    # Filter Sidebar Elements
    _price_slider = ".ngx-slider-span"  # Class selector for dual price slider tracks
    _category_checkbox = "label:has-text('{name}') input[type='checkbox']"
    _brand_checkbox = "label:has-text('{name}') input[type='checkbox']"

    # Product Catalog Elements
    _product_grid_cards = "a[href*='/product/']"
    _product_name = "[data-test='product-name']"
    _product_price = "[data-test='product-price']"
    _product_out_of_stock = "text=Out of stock"
    _product_eco_badge = "[data-test='co2-rating-badge']"

    # Pagination Elements
    _pagination_container = "ul.pagination"
    _pagination_page_item = "li.page-item"

    _nav_sign_in = "[data-test='nav-sign-in']"

    # --- Page Action & Verification Methods ---

    def verify_home_page_loaded(self):
        expect(self.page.get_by_role("link", name="Home")).to_be_visible()
        expect(self.page).to_have_title(re.compile(r"Practice Software Testing", re.IGNORECASE))

    def navigateToHomePage(self):
        self.navigate("https://practicesoftwaretesting.com")

    def verify_documentation_link_working(self):
        self.page.get_by_role("link", name=self.DOCUMENTATION).click()

    def verify_home_link_working(self):
        self.page.get_by_role("link", name=self.HOME).click()

    def verify_categories_link_working(self):
        self.page.get_by_role("button", name=self.CATEGORIES).click()

    def verify_user_signed_in(self, user_name: str):
        """Verify that the authenticated user name is visible in the header."""
        user_menu = self.page.locator(self._nav_menu)
        expect(user_menu).to_be_visible(timeout=10000)
        expect(user_menu).to_contain_text(user_name)
        expect(self.page.locator(self._nav_sign_in)).not_to_be_visible()

    def click_nav_home(self):
        """Click the home navigation button in the page header."""
        self.page.get_by_role("link", name=self._nav_home).click()

    def get_displayed_product_names(self) -> list:
        """Return all visible product names displayed in the current catalog grid."""
        product_name_locator = self.page.locator(self._product_name)
        expect(product_name_locator.first).to_be_visible(timeout=10000)
        return [name.strip() for name in product_name_locator.all_text_contents() if name and name.strip()]

    def get_search_input_value(self) -> str:
        """Read the current value of the search input field."""
        return self.page.locator(self._search_input).input_value()

    def count_displayed_products(self) -> int:
        """Count how many product cards are currently visible on the page."""
        product_name_locator = self.page.locator(self._product_name)
        expect(product_name_locator.first).to_be_visible(timeout=10000)
        return product_name_locator.count()

    def get_first_product_eco_badge_text(self) -> str:
        """Return the eco badge text label for the first visible product card."""
        eco_badge = self.page.locator(self._product_grid_cards).first.locator(self._product_eco_badge)
        expect(eco_badge).to_be_visible()
        return eco_badge.text_content().strip()

    def verify_pagination_page_active(self, page_number: str):
        """Assert that a specific pagination item is currently marked as active."""
        page_item = self.page.locator(self._pagination_container).locator(
            self._pagination_page_item,
            has_text=page_number
        )
        expect(page_item).to_have_class(re.compile(r"\bactive\b"))

    # --- New Functionality: Search & Sort Frameworks ---

    def search_product(self, query: str):
        """Types keyword criteria into search and executes query filtering."""
        search_field = self.page.locator(self._search_input)
        search_field.clear()
        search_field.fill(query)
        self.page.get_by_role("button", name=self._search_submit).click()
        self.page.wait_for_load_state("networkidle")
        expect(self.page.locator(self._product_name).first).to_be_visible(timeout=10000)
        expect(
            self.page.locator(self._product_name).filter(has_text=re.compile(query, re.IGNORECASE)).first
        ).to_be_visible(timeout=10000)

    def reset_search_filters(self):
        """Clears the current search query and reloads the catalog to its default state."""
        search_field = self.page.locator(self._search_input)
        search_reset_button = self.page.locator("[data-test='search-reset']")

        if search_reset_button.count() > 0:
            search_reset_button.first.click()
        else:
            search_field.clear()

        self.page.wait_for_timeout(500)
        search_field.clear()
        self.page.get_by_role("button", name=self._search_submit).click()
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)
        expect(search_field).to_have_value("")
        expect(self.page.locator(self._product_name).first).to_be_visible(timeout=10000)

    def select_sort(self, option_value="name,asc"):
        """Changes the ordering sequence rule using the global sort selector box.

        Valid options: 'name,asc', 'name,desc', 'price,asc', 'price,desc'
        """
        self.page.get_by_role("combobox", name=self._sort_dropdown).select_option(option_value)

    # --- New Functionality: Left-Side Filter Checkbox Automation ---

    def filter_by_category(self, category_name: str):
        """Toggle a category checkbox by its visible label text."""
        checkbox = self.page.get_by_role("checkbox", name=category_name)
        if not checkbox.is_checked():
            checkbox.click()

    def filter_by_brand(self, brand_name: str) -> bool:
        """Toggle a brand checkbox by its visible label text and report whether it changed state."""
        checkbox = self.page.get_by_role("checkbox", name=brand_name)
        expect(checkbox).to_be_visible(timeout=10000)

        was_checked = checkbox.is_checked()
        if not was_checked:
            checkbox.click()
            self.page.wait_for_timeout(500)

        expect(checkbox).to_be_checked(timeout=10000)
        return not was_checked

    # --- New Functionality: Data Retrieval & Assertions Layout ---

    def get_first_element(self):
        """Extract the text content of the first visible product item container title."""
        return (
            self.page.locator(self._product_grid_cards)
            .locator(self._product_name)
            .first.text_content()
        )

    def verify_first_element_displayed(self, expected_name="Adjustable Wrench"):
        """Waits for the grid to update and asserts that the first visible product
        matches the expected product title string.
        """
        # 1. Target the first product name locator explicitly
        first_product_locator = (
            self.page.locator(self._product_grid_cards)
            .locator(self._product_name)
            .first
        )

        # 2. Use Playwright's expect tool to robustly handle web loading delays
        expect(first_product_locator).to_have_text(expected_name)

        # Optional: Log the validated text to your test run output console
        print(f"Verified successfully: First element text is '{first_product_locator.text_content().strip()}'")

    def get_all_displayed_product_prices(self) -> list:
        """Scrapes the active grid display array to collect product prices as integers/floats."""
        self.page.wait_for_selector(self._product_grid_cards)
        price_elements = self.page.locator(self._product_price).all_text_contents()
        # Converts pricing string structures (e.g. '$14.15') directly to numeric floats for testing sorting logic
        return [float(price.replace("$", "").strip()) for price in price_elements]

    def verify_product_is_out_of_stock(self, product_index=0):
        """Checks if a specified product index shows an explicit 'Out of stock' flag badge context."""
        product_cards = self.page.locator(self._product_grid_cards)
        expect(product_cards.first).to_be_visible(timeout=10000)

        out_of_stock_cards = product_cards.filter(has_text="Out of stock")
        out_of_stock_count = out_of_stock_cards.count()
        assert out_of_stock_count > 0, "No product cards with an out-of-stock badge were found."

        target_card = out_of_stock_cards.nth(min(product_index, out_of_stock_count - 1))
        expect(target_card).to_be_visible()
        expect(target_card).to_contain_text("Out of stock")

    # --- New Functionality: UI Component Pagination Operations ---

    def click_pagination_page(self, page_number: str):
        """Target links matching explicit numerical counts on the grid pagination footer bar."""
        pagination_nav = self.page.locator(self._pagination_container)
        page_anchor = pagination_nav.locator(
            self._pagination_page_item, has_text=page_number
        )
        page_anchor.click()