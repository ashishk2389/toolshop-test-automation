import pytest
from pages.login_page import LoginPage
from pages.my_account_page import AccountPage

@pytest.mark.smoke
def test_my_account_dashboard_navigation(page, registration_data):
    """
    Test Case: Verify a logged-in user can successfully interact with
    the Favorites view, navigate back, and test the remaining tabs.
    """

    # 1. Initialize Page Object Models
    login_page = LoginPage(page)
    account_page = AccountPage(page)

    # 2. Extract valid user credentials from fixture data
    user_info = registration_data["valid_user"]

    # 3. Prerequisites: Navigate and log in to reach the Account Page
    login_page.navigateToLoginPage()
    login_page.verify_login_page_displayed()
    login_page.login(user_info)

    # 4. Step 1: Validate Account main landing page elements are correct
    account_page.verify_account_page_loaded()
    account_page.verify_account_menu_visible()

    # 5. Step 2: Verify Favorites link works as expected
    account_page.verify_favorites_button_working()

    # 6. Step 3: Navigate back to the main Account page and verify it reloaded
    page.go_back()
    account_page.verify_account_page_loaded()

    # 7. Step 4: Verify remaining sidebar navigation links are operational
    account_page.verify_profile_button_working()
    page.go_back()
    account_page.verify_account_page_loaded()

    account_page.verify_invoices_button_working()
    page.go_back()
    account_page.verify_account_page_loaded()

    account_page.verify_messages_button_working()
    page.go_back()
    account_page.verify_account_page_loaded()