import pytest
from playwright.sync_api import expect  # Ensure expect is imported
from pages.registration_page import RegisterPage
from pages.login_page import LoginPage

@pytest.mark.smoke
def test_successful_registration(page, registration_data):

    login_page = LoginPage(page)
    register_page = RegisterPage(page)

    # Extract the specific user dictionary from your YAML data
    user_info = registration_data["valid_user"]

    # Navigate to the registration page
    register_page.navigateToRegisterPage()

    # Verify that the registration page is displayed
    register_page.verify_register_page_displayed()

    # Fill the registration form
    register_page.fill_registration_form(user_info)

    # -------------------------------------------------------------
    # 2 SOFT ASSERTIONS (Will log failure but won't stop execution)
    # -------------------------------------------------------------

    # Soft Assertion 1: Check that the URL updated away from the register route
    expect.soft(page, "URL should change from register page").not_to_have_url(
        "https://practicesoftwaretesting.com/auth/register")

    # Soft Assertion 2: Check that a registration success alert/toast message isn't an error
    # (Assuming there's a dynamic alert element box displaying text status)
    register_page.verify_no_error_alert()

    # Verify that registration has left the registration route
    register_page.verify_registration_url_changed()

    # -------------------------------------------------------------
    # HARD ASSERTION (Your original condition)
    # -------------------------------------------------------------
    if not register_page.verify_user_exist():
        login_page.verify_login_page_displayed()