import pytest
from pages.profile_page import ProfilePage
from pages.registration_page import RegisterPage
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect

@pytest.mark.regression
def test_profile(page, registration_data):

    login_page = LoginPage(page)
    profile_page = ProfilePage(page)
    user_info = registration_data["valid_user"]

    # 1. Login and Navigate to Profile
    login_page.navigateToLoginPage()
    login_page.login(user_info)

    profile_page.navigateToProfilePage()
    #validate profile page is visible
    profile_page.verify_profile_page_loaded()
    # 2. Validation: Verify initial profile state matches user account details
    profile_page.verify_profile_details({
        "first_name": user_info["first_name"],
        "last_name": user_info["last_name"],
        "email": user_info["email"]
    })

    # 3. Validation: Verify email input is disabled (unchangeable security constraint)
    # profile_page.verify_email_disabled()

    # 4. Action: Update fields with new information
    updated_info = {
        "phone": "9876543210",
        "address": "123 New Testing Lane",
        "city": "Automation City",
        "state": "State of QA",
        "country": "US",  # Value matching select option
        "postcode": "12345"
    }
    profile_page.update_profile(updated_info)

    # 5. Validation: Ensure update confirmation appears successfully
    profile_page.verify_update_success("Your profile is successfully updated!")

    # 6. Validation: Check that values persist on the inputs correctly after submission
    profile_page.verify_profile_details(updated_info)
