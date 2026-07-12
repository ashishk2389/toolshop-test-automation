import time

from src.pages.base_page import BasePage
from playwright.sync_api import expect

from src.pages.registration_page import RegisterPage


class LoginPage(BasePage):

    # Locators
    EMAIL_INPUT = "Your email"
    PASSWORD_INPUT = "Your password"
    LOGIN_BUTTON = "Login"
    LOGIN_ERROR = "Invalid email or password"


    def __init__(self, page):
        super().__init__(page)

    # Actions

    def enter_email(self, email):
        self.page.get_by_placeholder(self.EMAIL_INPUT).fill(email)
        
    def enter_password(self, password):
        self.page.get_by_placeholder(self.PASSWORD_INPUT).fill(password)


    def click_login(self):
        self.page.get_by_role("button", name=self.LOGIN_BUTTON).click()


    def login(self, user_details: dict, register_if_failed: bool = True):
        self.enter_email(user_details.get("email"))
        self.enter_password(user_details.get("password"))
        self.click_login()

        if self._wait_for_login_result(timeout_ms=20000):
            return

        if not register_if_failed:
            raise AssertionError("Login failed after registration fallback.")

        self._register_and_retry_login(user_details)

    def _register_and_retry_login(self, user_details: dict):
        register_page = RegisterPage(self.page)
        register_page.navigateToRegisterPage()
        register_page.verify_register_page_displayed()
        register_page.fill_registration_form(user_details)

        register_page.verify_registration_url_changed()
        register_page.verify_no_error_alert()
        register_page.verify_registration_url_changed()

        self.page.wait_for_load_state("networkidle")
        self.navigateToLoginPage()
        self.login(user_details, register_if_failed=False)

    def login_with_fallback(self, user_details: dict):
        self.login(user_details, register_if_failed=True)

    def _is_login_error_visible(self) -> bool:
        try:
            return self.page.get_by_text(self.LOGIN_ERROR, exact=True).is_visible(timeout=5000)
        except Exception:
            return False

    def _wait_for_login_result(self, timeout_ms: int = 20000) -> bool:
        end_time = time.time() + (timeout_ms / 1000)

        while time.time() < end_time:
            if self._is_my_accounts_page_visible():
                return True

            if "/auth/login" not in self.page.url:
                print("in method ---------- not in")
                return True

            self.page.wait_for_timeout(1000)

        return False

    def _is_my_accounts_page_visible(self) -> bool:
        try:
            return (
                self.page.locator("[data-test='page-title']").to_have_text("My account")
            )
        except Exception:
            return False

    def navigateToLoginPage(self):
        self.navigate("https://practicesoftwaretesting.com/auth/login")

    def getErrorMessage(self):
        #todo
        pass

    # Validations

    def verify_login_page_displayed(self):

        expect(
            self.page.locator("h3")
        ).to_have_text("Login")


    def verify_email_field_visible(self):
        self.page.get_by_placeholder(self.EMAIL_INPUT).is_visible()

