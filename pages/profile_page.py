from pages.base_page import BasePage
from playwright.sync_api import Page, expect


class ProfilePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # --- Form Fields Locators (using get_by_test_data) ---
        self.page_title = self.page.get_by_test_id("page-title")
        # self.page_title = page.locator("[data-test='page-title']")
        # self.first_name_input = page.locator('[data-test="first-name"]')
        self.first_name_input = self.page.get_by_test_id("first-name")
        self.last_name_input = self.page.get_by_test_id("last-name")
        self.email_input = self.page.get_by_test_id("email")
        self.phone_input = self.page.get_by_test_id("phone")
        self.street_input = self.page.get_by_test_id("street")
        self.postal_code_input = self.page.get_by_test_id("postal_code")
        self.city_input = self.page.get_by_test_id("city")
        self.state_input = self.page.get_by_test_id("state")
        self.country_input = self.page.get_by_test_id("country")

        # --- Action Buttons ---
        self.update_profile_button = self.page.get_by_test_id("update-profile-submit")

        # --- Alerts / Messages (kept general if no data-test is present on alert) ---
        self.success_message = page.locator(".alert-success")

    def update_profile(self, profile_data: dict):
        """
        Fills out the profile form fields and submits the updates.

        Supports alternate keys for address and postal code values.
        """
        if "first_name" in profile_data:
            self.first_name_input.fill(profile_data["first_name"])
        if "last_name" in profile_data:
            self.last_name_input.fill(profile_data["last_name"])
        if "phone" in profile_data:
            self.phone_input.fill(profile_data["phone"])
        if "street" in profile_data:
            self.street_input.fill(profile_data["street"])
        elif "address" in profile_data:
            self.street_input.fill(profile_data["address"])
        if "city" in profile_data:
            self.city_input.fill(profile_data["city"])
        if "state" in profile_data:
            self.state_input.fill(profile_data["state"])
        if "country" in profile_data:
            self.country_input.select_option(profile_data["country"])
        if "postal_code" in profile_data:
            self.postal_code_input.fill(profile_data["postal_code"])
        elif "postcode" in profile_data:
            self.postal_code_input.fill(profile_data["postcode"])

        self.update_profile_button.click()

    def verify_profile_details(self, expected_data: dict):
        """
        Validates that the input fields contain the expected information.

        Accepts alternate key names for address and postal code verification.
        """
        if "first_name" in expected_data:
            expect(self.first_name_input).to_have_value(expected_data["first_name"])
        if "last_name" in expected_data:
            expect(self.last_name_input).to_have_value(expected_data["last_name"])
        if "email" in expected_data:
            expect(self.email_input).to_have_value(expected_data["email"])
        if "phone" in expected_data:
            expect(self.phone_input).to_have_value(expected_data["phone"])
        if "street" in expected_data:
            expect(self.street_input).to_have_value(expected_data["street"])
        elif "address" in expected_data:
            expect(self.street_input).to_have_value(expected_data["address"])
        if "city" in expected_data:
            expect(self.city_input).to_have_value(expected_data["city"])
        if "state" in expected_data:
            expect(self.state_input).to_have_value(expected_data["state"])
        if "country" in expected_data:
            expect(self.country_input).to_have_value(expected_data["country"])
        if "postal_code" in expected_data:
            expect(self.postal_code_input).to_have_value(expected_data["postal_code"])
        elif "postcode" in expected_data:
            expect(self.postal_code_input).to_have_value(expected_data["postcode"])

    def verify_update_success(self, expected_text: str = "Your profile is successfully updated!"):
        """
        Validates the success alert visibility and text.
        """
        expect(self.success_message).to_be_visible()
        expect(self.success_message).to_contain_text(expected_text)

    def verify_email_disabled(self):
        """
        Ensures the email input field is locked/disabled for editing.
        """
        expect(self.email_input).to_have_attribute("readonly", "")

    def navigateToProfilePage(self):
        self.navigate("https://practicesoftwaretesting.com/account/profile")

    def verify_profile_page_loaded(self):
        """Verifies that the main Account landing page has loaded successfully."""
        expect(self.page_title).to_have_text("Profile")