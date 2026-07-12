import os

import pytest
from playwright.sync_api import expect
from src.pages.home_page import HomePage
from src.pages.login_page import LoginPage

os.environ["SKIP_SESSION_AUTH_FOR_LOGIN"] = "1"


@pytest.mark.regression
def test_user_login(page, registration_data):
    login_page = LoginPage(page)
    home_page = HomePage(page)
    user_info = registration_data["valid_user"]

    # Navigate to the login page
    login_page.navigateToLoginPage()

    # Verify that the login page is displayed
    login_page.verify_login_page_displayed()

    login_page.verify_email_field_visible()

    # Perform login action with a fallback to register and retry if needed
    login_page.login_with_fallback(user_info)

    # Validate that the account area is visible after successful login
    expect(page.get_by_role("heading", name="My account")).to_be_visible(timeout=10000)
    home_page.verify_home_page_loaded()