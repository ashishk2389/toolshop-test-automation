import pytest
from pages.login_page import LoginPage

@pytest.mark.smoke
def test_user_login(page,registration_data):


    login_page = LoginPage(page)
    user_info = registration_data["valid_user"]
    # Navigate to the login page
    login_page.navigateToLoginPage()

    # Verify that the login page is displayed
    login_page.verify_login_page_displayed()

    login_page.verify_email_field_visible()

    # Perform login action
    login_page.login(user_info)

    #add validatin that my homepege is visible