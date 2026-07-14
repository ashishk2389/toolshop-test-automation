import logging
import time

from playwright.sync_api import expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from src.pages.base_page import BasePage
from src.pages.registration_page import RegisterPage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """Page Object for the customer login page.

    Also owns the "login, and register-then-retry if the account doesn't
    exist yet" fallback flow, since that flow always starts and ends on
    this page.
    """

    LOGIN_URL = "https://practicesoftwaretesting.com/auth/login"

    # Placeholder-based locators
    EMAIL_PLACEHOLDER = "Your email"
    PASSWORD_PLACEHOLDER = "Your password"

    # Role-based locators
    LOGIN_BUTTON_NAME = "Login"

    # Text content
    LOGIN_ERROR_TEXT = "Invalid email or password"
    ACCOUNT_PAGE_TITLE_TEXT = "My account"

    # Timeouts
    DEFAULT_LOGIN_TIMEOUT_MS = 20000
    LOGIN_ERROR_VISIBLE_TIMEOUT_MS = 5000
    POLL_INTERVAL_MS = 1000

    def __init__(self, page):
        super().__init__(page)

    # --- Actions --------------------------------------------------------

    def navigate_to_login_page(self):
        """Navigate the browser to the login page."""
        logger.info("Navigating to login page: %s", self.LOGIN_URL)
        self.navigate(self.LOGIN_URL)

    def enter_email(self, email):
        """Fill the email field.

        Args:
            email: The email address to enter.
        """
        logger.debug("Entering email: %s", email)
        self.page.get_by_placeholder(self.EMAIL_PLACEHOLDER).fill(email)

    def enter_password(self, password):
        """Fill the password field.

        Note:
            The value is intentionally not logged to avoid leaking
            credentials into log output.
        """
        logger.debug("Entering password (value masked)")
        self.page.get_by_placeholder(self.PASSWORD_PLACEHOLDER).fill(password)

    def click_login(self):
        """Click the Login submit button."""
        logger.info("Submitting login form")
        self.page.get_by_role("button", name=self.LOGIN_BUTTON_NAME).click()

    def login(self, user_details: dict, register_if_failed: bool = True):
        """Log in with the given credentials, optionally registering first if login fails.

        Args:
            user_details: Dictionary of user values. Must include "email"
                and "password"; if a registration fallback is triggered,
                the full set of fields required by
                ``RegisterPage.fill_registration_form`` is required.
            register_if_failed: If True, and login does not succeed within
                the timeout, fall back to registering the account and
                retrying login once. If False, raise on failure instead.

        Raises:
            AssertionError: If login fails and ``register_if_failed`` is False.
        """
        logger.info("Attempting login for email: %s", user_details.get("email"))
        self.enter_email(user_details.get("email"))
        self.enter_password(user_details.get("password"))
        self.click_login()

        if self._wait_for_login_result(timeout_ms=self.DEFAULT_LOGIN_TIMEOUT_MS):
            logger.info("Login succeeded")
            return

        if not register_if_failed:
            logger.error("Login failed and registration fallback is disabled")
            raise AssertionError("Login failed after registration fallback.")

        logger.info("Login failed, falling back to registration")
        self._register_and_retry_login(user_details)

    def login_with_fallback(self, user_details: dict):
        """Log in, registering the account first if it doesn't already exist.

        Args:
            user_details: Dictionary of user values, as required by ``login``.
        """
        self.login(user_details, register_if_failed=True)

    def get_error_message(self) -> str:
        """Return the currently displayed login error text.

        Returns:
            The error message text, or an empty string if no error is visible.
        """
        error_locator = self.page.get_by_text(self.LOGIN_ERROR_TEXT, exact=True)
        if error_locator.is_visible():
            message = error_locator.inner_text()
            logger.debug("Login error message visible: %s", message)
            return message
        return ""

    def _register_and_retry_login(self, user_details: dict):
        """Register a new account for the given user, then retry login once.

        Args:
            user_details: Dictionary of user values required by both
                registration and login.
        """
        register_page = RegisterPage(self.page)
        register_page.navigate_to_register_page()
        register_page.verify_register_page_displayed()
        register_page.fill_registration_form(user_details)

        register_page.verify_registration_url_changed()
        register_page.verify_no_error_alert()

        self.page.wait_for_load_state("networkidle")
        self.navigate_to_login_page()
        self.login(user_details, register_if_failed=False)

    def _is_login_error_visible(self) -> bool:
        """Check whether the invalid-credentials error message is visible.

        Returns:
            True if the login error is visible within the timeout, False otherwise.
        """
        try:
            return self.page.get_by_text(self.LOGIN_ERROR_TEXT, exact=True).is_visible(
                timeout=self.LOGIN_ERROR_VISIBLE_TIMEOUT_MS
            )
        except PlaywrightTimeoutError:
            return False

    def _wait_for_login_result(self, timeout_ms: int = DEFAULT_LOGIN_TIMEOUT_MS) -> bool:
        """Poll until login either succeeds (navigates away from /auth/login) or times out.

        Args:
            timeout_ms: Maximum time to wait, in milliseconds.

        Returns:
            True if login appears to have succeeded, False if it timed out.
        """
        end_time = time.time() + (timeout_ms / 1000)

        while time.time() < end_time:
            if self._is_my_accounts_page_visible():
                return True

            if "/auth/login" not in self.page.url:
                logger.debug("URL no longer on /auth/login, treating login as successful")
                return True

            self.page.wait_for_timeout(self.POLL_INTERVAL_MS)

        logger.debug("Timed out waiting for login result")
        return False

    def _is_my_accounts_page_visible(self) -> bool:
        """Check whether the 'My account' page title is currently displayed.

        Note:
            Previously this called ``.to_have_text()`` directly on a
            Locator, which is not a valid Locator method (that assertion
            belongs on ``expect()``) and always raised, silently caught by
            a bare ``except Exception``, making this check permanently
            return False. Fixed to read the element's text directly.

        Returns:
            True if the account page title is visible with the expected text.
        """
        try:
            title_locator = self.page.locator("[data-test='page-title']")
            return title_locator.is_visible() and title_locator.inner_text() == self.ACCOUNT_PAGE_TITLE_TEXT
        except PlaywrightTimeoutError:
            return False

    # --- Validations ------------------------------------------------------

    def verify_login_page_displayed(self):
        """Assert that the 'Login' heading is visible."""
        logger.info("Verifying login page heading is displayed")
        expect(self.page.locator("h3")).to_have_text("Login")

    def verify_email_field_visible(self):
        """Assert that the email input field is visible.

        Note:
            Previously this called ``.is_visible()`` without wrapping it in
            ``expect()``, so the boolean result was discarded and the
            method never actually asserted anything. Fixed to use
            ``expect().to_be_visible()``.
        """
        logger.info("Verifying email field is visible")
        expect(self.page.get_by_placeholder(self.EMAIL_PLACEHOLDER)).to_be_visible()