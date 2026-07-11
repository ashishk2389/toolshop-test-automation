import pytest
from playwright.sync_api import Page
from pages.my_account_page import AccountPage

@pytest.mark.regression
def test_my_account_dashboard_navigation(page: Page):
    """
    Test Case: Verify an already authenticated user can successfully interact with
    the Favorites view, navigate back, and test the remaining tabs.
    """

    # 1. Initialize the Page Object Model
    account_page = AccountPage(page)

    # 2. Navigate directly to the account page (since the session state is pre-loaded)
    # Note: Replace this with your actual application dashboard or account URL string
    account_page.navigateToMyAccountsPage()

    # 3. Step 1: Validate Account main landing page elements are correct
    account_page.verify_account_page_loaded()
    account_page.verify_account_menu_visible()

    # 4. Step 2: Verify Favorites link works as expected
    account_page.verify_favorites_button_working()

    # 5. Step 3: Navigate back to the main Account page and verify it reloaded
    page.go_back()
    account_page.verify_account_page_loaded()

    # 6. Step 4: Verify remaining sidebar navigation links are operational
    account_page.verify_profile_button_working()
    page.go_back()
    account_page.verify_account_page_loaded()

    account_page.verify_invoices_button_working()
    page.go_back()
    account_page.verify_account_page_loaded()

    account_page.verify_messages_button_working()
    page.go_back()
    account_page.verify_account_page_loaded()

    # Shadow DOM piercing validation
    account_page.verify_chat_widget_integration_shadow_dom_piercing()
