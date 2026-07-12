import pytest

from src.pages.my_account_page import AccountPage


@pytest.mark.regression
def test_new_tab(page, registration_data):

    # 1. Initialize Page Object Models
    # login_page = LoginPage(page)
    account_page = AccountPage(page)

    # 2. Extract valid user credentials from fixture data
    user_info = registration_data["valid_user"]

    # 3. Prerequisites: Navigate to the authenticated account page
    account_page.navigateToMyAccountsPage()
    page.wait_for_load_state("networkidle")

    # 4. Verify Account main landing page elements are correct
    account_page.verify_account_page_loaded()
    account_page.verify_account_menu_visible()

    new_tab = account_page.open_bug_hunting_tab()
    account_page.verify_bug_hunting_url(new_tab)
    new_tab.close()
