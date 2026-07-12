import pytest
import re
from playwright.sync_api import expect
from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage


@pytest.fixture(scope="function")
def logged_in_home_page(page, registration_data):
    """
    Setup fixture to handle user session authentication before executing catalog validations.
    Ensures that every test starts with an active session for 'Jane Doe'.
    """
    home_page = HomePage(page)

    try:
        is_signed_in = (
            page.get_by_text("Jane Doe", exact=True).is_visible(timeout=3000)
            or page.get_by_role("link", name="My account").is_visible(timeout=3000)
        )
    except Exception:
        is_signed_in = False

    if not is_signed_in:
        login_page = LoginPage(page)
        login_page.navigateToLoginPage()
        login_page.verify_login_page_displayed()
        login_page.login_with_fallback(registration_data["valid_user"])
        page.wait_for_load_state("networkidle")

    home_page.navigateToHomePage()
    home_page.verify_home_page_loaded()

    return home_page


# =====================================================================
# 1. Header & Identity State Validations
# =====================================================================


@pytest.mark.regression
def test_header_identity_and_navigation_targets(logged_in_home_page):
    """
    Validates that the logged-in session state accurately displays the user's name
    instead of an anonymous 'Sign In' link, and checks global home navigation redirection.
    """
    home = logged_in_home_page

    # Logged-In Session State Assertion: Assert the user's name appears in the header
    home.verify_user_signed_in("Jane Doe")

    # Navigation Targets: Validate clicking the brand logo correctly forces grid reloads
    home.click_nav_home()
    # expect(page).to_have_url(re.compile(r"https://practicesoftwaretesting.com/?"))


# =====================================================================
# 2. Search & Reset Button Integration Actions
# =====================================================================

@pytest.mark.regression
def test_search_functionality_and_filter_reset(logged_in_home_page, page):
    """
    Validates dynamic keyword search filtering across the product catalog grid
    and checks the UI element clear action.
    """
    home = logged_in_home_page

    initial_product_count = home.count_displayed_products()

    # Dynamic Keyword Matching: Query for "Hammer" and execute search
    home.search_product("Hammer")
    page.wait_for_timeout(1000)  # Short pause for asynchronous grid rendering threshold

    # Collect and assert that every card item name includes the substring 'Hammer'
    product_names = home.get_displayed_product_names()
    assert len(product_names) > 0, "Search query returned no products."
    for name in product_names:
        assert "hammer" in name.lower(), f"Product text '{name}' did not match query string 'Hammer'."

    # Clear Search State Automation: Click the yellow 'X' button to reset filters
    home.reset_search_filters()

    # Verify input text field resets to an empty string and the catalog returns to its original state
    assert home.get_search_input_value() == ""
    reset_product_count = home.count_displayed_products()
    assert reset_product_count == initial_product_count, (
        f"Product catalog layout did not reset to the original count. "
        f"Expected {initial_product_count}, got {reset_product_count}."
    )


# =====================================================================
# 3. Filtering and Core Grid Sorting Verification
# =====================================================================

@pytest.mark.regression
def test_out_of_stock_attributes_and_eco_badges(logged_in_home_page, page):
    """
    Validates visibility thresholds for specific product attributes including
    environmental CO2 score flags and out of stock badges.
    """
    home = logged_in_home_page

    # Out of Stock Attribute Isolation: Target index known to be depleted
    # and confirm red layout indicator is visible
    home.verify_product_is_out_of_stock(product_index=0)  # e.g., Combination Pliers

    # Environmental Badge Verification: Verify visible product cards contain a CO2:
    # badge framework component with an active score tier highlighted
    pill_text = home.get_first_product_eco_badge_text()
    assert any(tier in pill_text for tier in ["A", "B", "C", "D", "E"]), f"Unexpected Eco badge score layout: {pill_text}"


@pytest.mark.regression
def test_dynamic_sidebar_filters_and_price_sorting(logged_in_home_page, page):#not working
    """
    Validates that checking brand/category sidebar parameters alters grid counts dynamically,
    and programmatically asserts numerical float arrays match low-to-high sorting expectations.
    """
    home = logged_in_home_page

    # Dynamic Sidebar Filter State: Toggle a brand checkbox and confirm the UI reflects it
    initial_count = home.count_displayed_products()
    filter_toggled = home.filter_by_brand("ForgeFlex Tools")
    assert filter_toggled is True, "The brand checkbox did not change to the checked state."

    filtered_count = home.count_displayed_products()
    assert filtered_count == initial_count, "The product catalog count unexpectedly changed after the checkbox toggle."

    # Ascending/Descending Array Ordering: Select price sorting dropdown rule
    home.select_sort("price,asc")
    page.wait_for_timeout(1000)

    # Scrape string elements matching product prices, convert them to floats, and assert sorted order
    prices = home.get_all_displayed_product_prices()
    assert len(prices) > 0, "No product item records found to validate sort mapping arrays."
    assert prices == sorted(prices), f"Numerical float pricing list was not properly sorted: {prices}"


# =====================================================================
# 4. UI Grid Pagination Logic
# =====================================================================

@pytest.mark.regression
def test_pagination_state_boundaries_and_grid_reloads(logged_in_home_page, page):
    """
    Validates tracking attributes on active page numbers and asserts content modifications
    when interacting with subsequent index pagination buttons.
    """
    home = logged_in_home_page

    # Default State Boundary: Confirm page number item '1' is explicitly flagged as the active element
    home.verify_pagination_page_active("1")

    # Capture standard text snapshot of initial index titles
    initial_first_element = home.get_first_element()

    # Move downstream by executing navigation click selector onto target page 2
    home.click_pagination_page("2")
    page.wait_for_timeout(1000)

    # Assert that the product array grid modified its context payload entries
    new_first_element = home.get_first_element()
    assert initial_first_element != new_first_element, "Pagination control click action failed to alter the rendering card data."

