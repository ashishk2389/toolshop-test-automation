import pytest
from pages.registration_page import RegisterPage
from pages.login_page import LoginPage

@pytest.mark.smoke
def test_successful_registration(page,registration_data):


    login_page = LoginPage(page)
    # 1. Initialize your RegisterPage object
    register_page = RegisterPage(page)

    # 2. Extract the specific user dictionary from your YAML data
    user_info = registration_data["valid_user"]

    # Navigate to the registration page
    register_page.navigateToRegisterPage()

    # Verify that the registration page is displayed
    register_page.verify_register_page_displayed()

    # fill the registration form
    register_page.fill_registration_form(user_info)

    # 3. Validation: Check that the login page is automatically displayed after successful registration
    login_page.verify_login_page_displayed()

