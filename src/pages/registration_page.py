import logging

from playwright.sync_api import expect

from src.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class RegisterPage(BasePage):
    """Page Object for the customer registration page.

    Encapsulates all locators and interactions required to fill out and
    submit the registration form at ``/auth/register``.
    """

    # --- Locators grouped by strategy ---------------------------------
    # Placeholder-based locators
    FIRST_NAME_PLACEHOLDER = "First name *"
    LAST_NAME_PLACEHOLDER = "Your last name *"
    DOB_PLACEHOLDER = "YYYY-MM-DD"
    POSTAL_CODE_PLACEHOLDER = "Your Postcode *"
    HOUSE_NUMBER_PLACEHOLDER = "e.g. 42 *"
    STREET_PLACEHOLDER = "Your Street *"
    CITY_PLACEHOLDER = "Your City *"
    STATE_PLACEHOLDER = "Your State *"
    PHONE_PLACEHOLDER = "Your phone *"
    EMAIL_PLACEHOLDER = "Your email *"
    PASSWORD_PLACEHOLDER = "Your password"

    # data-test attribute based locators
    COUNTRY_SELECT_TEST_ID = "country"
    REGISTER_ERROR_TEST_ID = "register-error"

    # Role-based locators
    REGISTER_BUTTON_NAME = "Register"

    REGISTER_URL = "https://practicesoftwaretesting.com/auth/register"
    DUPLICATE_EMAIL_ERROR_TEXT = "A customer with this email address already exists."

    def __init__(self, page):
        super().__init__(page)

    # --- Actions --------------------------------------------------------

    def navigate_to_register_page(self):
        """Navigate the browser to the customer registration page."""
        logger.info("Navigating to registration page: %s", self.REGISTER_URL)
        self.navigate(self.REGISTER_URL)

    def enter_first_name(self, first_name: str):
        """Fill the first name field.

        Args:
            first_name: The first name to enter.
        """
        logger.debug("Entering first name: %s", first_name)
        self.page.get_by_placeholder(self.FIRST_NAME_PLACEHOLDER).fill(first_name)

    def enter_last_name(self, last_name: str):
        """Fill the last name field.

        Args:
            last_name: The last name to enter.
        """
        logger.debug("Entering last name: %s", last_name)
        self.page.get_by_placeholder(self.LAST_NAME_PLACEHOLDER).fill(last_name)

    def enter_date_of_birth(self, dob: str):
        """Fill the date of birth field.

        Args:
            dob: Date of birth in YYYY-MM-DD format.
        """
        logger.debug("Entering date of birth: %s", dob)
        self.page.get_by_placeholder(self.DOB_PLACEHOLDER).fill(dob)

    def select_country(self, country_value: str):
        """Select a country from the country dropdown.

        Args:
            country_value: The option value (e.g. country code) to select.
        """
        logger.debug("Selecting country: %s", country_value)
        self.page.locator(f"[data-test='{self.COUNTRY_SELECT_TEST_ID}']").select_option(country_value)

    def enter_postal_code(self, postal_code: str):
        """Fill the postal code field.

        Args:
            postal_code: The postal/zip code to enter.
        """
        logger.debug("Entering postal code: %s", postal_code)
        self.page.get_by_placeholder(self.POSTAL_CODE_PLACEHOLDER).fill(postal_code)

    def enter_house_number(self, house_number: str):
        """Fill the house number field.

        Args:
            house_number: The house/building number to enter.
        """
        logger.debug("Entering house number: %s", house_number)
        self.page.get_by_placeholder(self.HOUSE_NUMBER_PLACEHOLDER).fill(house_number)

    def enter_street(self, street: str):
        """Fill the street field.

        Args:
            street: The street name to enter.
        """
        logger.debug("Entering street: %s", street)
        self.page.get_by_placeholder(self.STREET_PLACEHOLDER).fill(street)

    def enter_city(self, city: str):
        """Fill the city field.

        Args:
            city: The city name to enter.
        """
        logger.debug("Entering city: %s", city)
        self.page.get_by_placeholder(self.CITY_PLACEHOLDER).fill(city)

    def enter_state(self, state: str):
        """Fill the state field.

        Args:
            state: The state/province to enter.
        """
        logger.debug("Entering state: %s", state)
        self.page.get_by_placeholder(self.STATE_PLACEHOLDER).fill(state)

    def enter_phone(self, phone: str):
        """Fill the phone number field.

        Args:
            phone: The phone number to enter.
        """
        logger.debug("Entering phone number: %s", phone)
        self.page.get_by_placeholder(self.PHONE_PLACEHOLDER).fill(phone)

    def enter_email(self, email: str):
        """Fill the email field.

        Args:
            email: The email address to enter.
        """
        logger.debug("Entering email: %s", email)
        self.page.get_by_placeholder(self.EMAIL_PLACEHOLDER).fill(email)

    def enter_password(self, password: str):
        """Fill the password field.

        Note:
            The value is intentionally not logged to avoid leaking
            credentials into log output.
        """
        logger.debug("Entering password (value masked)")
        self.page.get_by_placeholder(self.PASSWORD_PLACEHOLDER).fill(password)

    def click_register(self):
        """Click the Register submit button at the bottom of the form."""
        logger.info("Submitting registration form")
        self.page.get_by_role("button", name=self.REGISTER_BUTTON_NAME).click()

    def fill_registration_form(self, user_details: dict):
        """Fill out and submit the entire registration form in one call.

        Args:
            user_details: Dictionary of form values. Expected keys:
                first_name, last_name, dob, country, postal_code,
                house_number, street, city, state, phone, email, password.
                ``country`` defaults to ``"AL"`` if not provided.
        """
        logger.info("Filling registration form for email: %s", user_details.get("email"))
        self.enter_first_name(user_details.get("first_name"))
        self.enter_last_name(user_details.get("last_name"))
        self.enter_date_of_birth(user_details.get("dob"))
        self.select_country(user_details.get("country", "AL"))
        self.enter_postal_code(user_details.get("postal_code"))
        self.enter_house_number(user_details.get("house_number"))
        self.enter_street(user_details.get("street"))
        self.enter_city(user_details.get("city"))
        self.enter_state(user_details.get("state"))
        self.enter_phone(user_details.get("phone"))
        self.enter_email(user_details.get("email"))
        self.enter_password(user_details.get("password"))
        self.click_register()

    # --- Validations ------------------------------------------------------

    def verify_register_page_displayed(self):
        """Assert that the 'Customer registration' heading is visible."""
        logger.info("Verifying registration page heading is displayed")
        expect(self.page.locator("h3")).to_have_text("Customer registration")

    def verify_registration_url_changed(self):
        """Assert that the browser has navigated away from the register form route."""
        logger.info("Verifying URL has changed away from the register page")
        expect(self.page).not_to_have_url(self.REGISTER_URL)

    def verify_no_error_alert(self):
        """Assert that no registration-level alert contains an invalid or failure message."""
        alerts = self.page.locator(".alert")
        if alerts.count() > 0:
            logger.debug("Alert(s) found on page, checking for invalid message")
            expect(alerts.first).not_to_contain_text("invalid")
        else:
            logger.debug("No alerts present on page")

    def verify_user_exist(self) -> bool:
        """Check whether a duplicate-email registration error is displayed.

        Returns:
            True if the "customer already exists" error is shown within
            the timeout window, False otherwise.
        """
        try:
            expect(self.page.get_by_test_id(self.REGISTER_ERROR_TEST_ID)).to_have_text(
                self.DUPLICATE_EMAIL_ERROR_TEXT,
                timeout=5000,
            )
            logger.info("Duplicate user error confirmed on page")
            return True
        except AssertionError:
            logger.error("Expected duplicate user error not found on page")
            return False