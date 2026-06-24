from pages.base_page import BasePage
from playwright.sync_api import expect


class RegisterPage(BasePage):

    # Locators (Placeholders from the UI)
    FIRST_NAME_INPUT = "First name *"
    LAST_NAME_INPUT = "Your last name *"
    DOB_INPUT = "YYYY-MM-DD"
    COUNTRY_SELECT = "country"  # Label/ID for the dropdown
    POSTAL_CODE_INPUT = "Your Postcode *"
    HOUSE_NUMBER_INPUT = "e.g. 42 *"
    STREET_INPUT = "Your Street *"
    CITY_INPUT = "Your City *"
    STATE_INPUT = "Your State *"
    PHONE_INPUT = "Your phone *"
    EMAIL_INPUT = "Your email *"
    PASSWORD_INPUT = "Your password"
    REGISTER_BUTTON = "Register"

    def __init__(self, page):
        super().__init__(page)

    # Actions

    def navigateToRegisterPage(self):
        self.navigate("https://practicesoftwaretesting.com/auth/register")

    def enter_first_name(self, first_name):
        self.page.get_by_placeholder(self.FIRST_NAME_INPUT).fill(first_name)

    def enter_last_name(self, last_name):
        self.page.get_by_placeholder(self.LAST_NAME_INPUT).fill(last_name)

    def enter_date_of_birth(self, dob):
        self.page.get_by_placeholder(self.DOB_INPUT).fill(dob)

    def select_country(self, country_value):
        # Uses select_option for the dropdown menu
        self.page.locator("[data-test='country']").select_option(country_value)

    def enter_postal_code(self, postal_code):
        self.page.get_by_placeholder(self.POSTAL_CODE_INPUT).fill(postal_code)

    def enter_house_number(self, house_number):
        self.page.get_by_placeholder(self.HOUSE_NUMBER_INPUT).fill(house_number)

    def enter_street(self, street):
        self.page.get_by_placeholder(self.STREET_INPUT).fill(street)

    def enter_city(self, city):
        self.page.get_by_placeholder(self.CITY_INPUT).fill(city)

    def enter_state(self, state):
        self.page.get_by_placeholder(self.STATE_INPUT).fill(state)

    def enter_phone(self, phone):
        self.page.get_by_placeholder(self.PHONE_INPUT).fill(phone)

    def enter_email(self, email):
        self.page.get_by_placeholder(self.EMAIL_INPUT).fill(email)

    def enter_password(self, password):
        self.page.get_by_placeholder(self.PASSWORD_INPUT).fill(password)

    def click_register(self):
        # Note: The register button is situated at the bottom of the form
        self.page.get_by_role("button", name=self.REGISTER_BUTTON).click()

    def fill_registration_form(self, user_details: dict):
        """
        Helper method to fill out the entire registration form at once.
        Expects a dictionary with keys matching the fields.
        """
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

    # Validations

    def verify_register_page_displayed(self):
        expect(
            self.page.locator("h3")
        ).to_have_text("Customer registration")