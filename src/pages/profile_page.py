import logging

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class ProfilePage(BasePage):
    """Page Object for the customer account profile page.

    Encapsulates all locators and interactions required to view, edit,
    and verify the logged-in customer's profile at ``/account/profile``.
    """

    PROFILE_URL = "https://practicesoftwaretesting.com/account/profile"
    PAGE_HEADING_NAME = "Profile"
    UPDATE_PROFILE_BUTTON_NAME = "Update Profile"
    DEFAULT_SUCCESS_TEXT = "Your profile is successfully updated!"

    def __init__(self, page: Page):
        super().__init__(page)

        # --- Form field locators (using the current profile page markup) ---
        self.page_title = self.page.get_by_role("heading", name=self.PAGE_HEADING_NAME)
        self.first_name_input = self.page.locator("#first_name")
        self.last_name_input = self.page.locator("#last_name")
        self.email_input = self.page.locator("#email")
        self.phone_input = self.page.locator("#phone")
        self.street_input = self.page.locator("#street")
        self.postal_code_input = self.page.locator("#postal_code")
        self.city_input = self.page.locator("#city")
        self.state_input = self.page.locator("#state")
        self.country_input = self.page.locator("#country")

        # --- Action buttons ---
        self.update_profile_button = self.page.get_by_role("button", name=self.UPDATE_PROFILE_BUTTON_NAME)

        # --- Alerts / messages (kept general since no data-test is present on the alert) ---
        self.success_message = self.page.locator(".alert-success")

    # --- Actions ------------------------------------------------------

    def navigate_to_profile_page(self):
        """Navigate the browser to the customer profile page."""
        logger.info("Navigating to profile page: %s", self.PROFILE_URL)
        self.navigate(self.PROFILE_URL)

    def update_profile(self, profile_data: dict):
        """Fill out the profile form fields and submit the updates.

        Supports alternate keys for the street and postal code values
        (``address`` as an alias for ``street``, ``postcode`` as an
        alias for ``postal_code``).

        Args:
            profile_data: Dictionary of profile values. Recognized keys:
                first_name, last_name, phone, street (or address), city,
                state, country, postal_code (or postcode).
        """
        logger.info("Updating profile with fields: %s", list(profile_data.keys()))

        if "first_name" in profile_data:
            logger.debug("Setting first name: %s", profile_data["first_name"])
            self.first_name_input.fill(profile_data["first_name"])
        if "last_name" in profile_data:
            logger.debug("Setting last name: %s", profile_data["last_name"])
            self.last_name_input.fill(profile_data["last_name"])
        if "phone" in profile_data:
            logger.debug("Setting phone: %s", profile_data["phone"])
            self.phone_input.fill(profile_data["phone"])
        if "street" in profile_data:
            logger.debug("Setting street: %s", profile_data["street"])
            self.street_input.fill(profile_data["street"])
        elif "address" in profile_data:
            logger.debug("Setting street (via 'address' alias): %s", profile_data["address"])
            self.street_input.fill(profile_data["address"])
        if "city" in profile_data:
            logger.debug("Setting city: %s", profile_data["city"])
            self.city_input.fill(profile_data["city"])
        if "state" in profile_data:
            logger.debug("Setting state: %s", profile_data["state"])
            self.state_input.fill(profile_data["state"])
        if "country" in profile_data:
            logger.debug("Setting country: %s", profile_data["country"])
            self.country_input.fill(profile_data["country"])
        if "postal_code" in profile_data:
            logger.debug("Setting postal code: %s", profile_data["postal_code"])
            self.postal_code_input.fill(profile_data["postal_code"])
        elif "postcode" in profile_data:
            logger.debug("Setting postal code (via 'postcode' alias): %s", profile_data["postcode"])
            self.postal_code_input.fill(profile_data["postcode"])

        logger.info("Submitting profile update")
        self.update_profile_button.click()

    # --- Validations ----------------------------------------------------

    def verify_profile_details(self, expected_data: dict):
        """Validate that the input fields contain the expected information.

        Accepts alternate key names for street and postal code verification
        (``address`` as an alias for ``street``, ``postcode`` as an alias
        for ``postal_code``).

        Args:
            expected_data: Dictionary of expected profile values. Recognized
                keys: first_name, last_name, email, phone, street (or
                address), city, state, country, postal_code (or postcode).
        """
        logger.info("Verifying profile fields: %s", list(expected_data.keys()))

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

    def verify_update_success(self, expected_text: str = DEFAULT_SUCCESS_TEXT):
        """Validate that the success alert is visible with the expected text.

        Args:
            expected_text: The text expected within the success alert.
                Defaults to the standard profile-update success message.
        """
        logger.info("Verifying profile update success message")
        expect(self.success_message).to_be_visible()
        expect(self.success_message).to_contain_text(expected_text)

    def verify_email_disabled(self):
        """Ensure the email input field is locked/disabled for editing."""
        logger.debug("Verifying email field is readonly")
        expect(self.email_input).to_have_attribute("readonly", "")

    def verify_profile_page_loaded(self):
        """Verify that the profile page has loaded by checking its heading."""
        logger.info("Verifying profile page heading is displayed")
        expect(self.page_title).to_have_text(self.PAGE_HEADING_NAME)