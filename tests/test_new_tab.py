import re
from lib2to3.fixes.fix_input import context

import pytest

from pages.login_page import LoginPage
from pages.my_account_page import AccountPage
import re
from playwright.sync_api import expect

@pytest.mark.regression
def test_new_tab(page, registration_data):

    # 1. Initialize Page Object Models
    login_page = LoginPage(page)
    account_page = AccountPage(page)

    # 2. Extract valid user credentials from fixture data
    user_info = registration_data["valid_user"]

    # 3. Prerequisites: Navigate and log in to reach the Account Page
    login_page.navigateToLoginPage()
    login_page.verify_login_page_displayed()
    login_page.login(user_info)

    # 4. Verify Account main landing page elements are correct
    account_page.verify_account_page_loaded()
    account_page.verify_account_menu_visible()

    with page.context.expect_page() as new_page_info:
        account_page.bug_hunting.click()

    new_tab = new_page_info.value
    new_tab.wait_for_load_state()
    expect(new_tab).to_have_url('https://with-bugs.practicesoftwaretesting.com/#/?bug-hunting=true')
