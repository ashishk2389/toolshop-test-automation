import logging

from playwright.sync_api import expect

from src.pages.base_page import BasePage

logger = logging.getLogger(__name__)


class AccountPage(BasePage):
    """Page Object for the customer 'My Account' landing page and its
    sub-navigation menu on practicesoftwaretesting.com.
    """

    ACCOUNT_URL = "https://practicesoftwaretesting.com/account"
    BUG_HUNTING_URL = "https://with-bugs.practicesoftwaretesting.com/#/?bug-hunting=true"

    PAGE_TITLE_ACCOUNT = "My account"
    PAGE_TITLE_FAVORITES = "Favorites"
    PAGE_TITLE_PROFILE = "Profile"
    PAGE_TITLE_INVOICES = "Invoices"
    PAGE_TITLE_MESSAGES = "Messages"

    # NOTE: leading/trailing whitespace and the emoji below are intentional —
    # they reflect the exact accessible name rendered by the site's markup.
    # Verify against the live DOM before changing these.
    TESTING_GUIDE_BUTTON_NAME = " Testing Guide "
    BUG_HUNTING_BUTTON_NAME = " 🐛 Bug Hunting "
    CHAT_GREETING_TEXT = " Hi! How can I help you today? "

    def __init__(self, page):
        super().__init__(page)

        # Main page header element
        self.page_title = page.locator("[data-test='page-title']")

        # Account sidebar menu navigation elements.
        # These are rendered as <button> elements (not anchors), hence role="button".
        self.favorites_button = page.get_by_role("button", name=self.PAGE_TITLE_FAVORITES)
        self.profile_button = page.get_by_role("button", name=self.PAGE_TITLE_PROFILE)
        self.invoices_button = page.get_by_role("button", name=self.PAGE_TITLE_INVOICES)
        self.messages_button = page.get_by_role("button", name=self.PAGE_TITLE_MESSAGES)
        self.testing_guide_button = page.get_by_role("button", name=self.TESTING_GUIDE_BUTTON_NAME)
        self.bug_hunting_button = page.get_by_role("button", name=self.BUG_HUNTING_BUTTON_NAME)
        self.chat_toggle = page.locator("[data-test='chat-toggle']")
        self.chat_window = page.locator("[data-test='chat-window']")

    # ==========================================
    #                 ACTIONS
    # ==========================================

    def navigate_to_account_page(self):
        """Navigate the browser to the customer 'My Account' landing page."""
        logger.info("Navigating to account page: %s", self.ACCOUNT_URL)
        self.navigate(self.ACCOUNT_URL)

    def click_favorites(self):
        """Click the Favorites menu button."""
        logger.debug("Clicking Favorites menu button")
        self.favorites_button.click()

    def click_profile(self):
        """Click the Profile menu button."""
        logger.debug("Clicking Profile menu button")
        self.profile_button.click()

    def click_invoices(self):
        """Click the Invoices menu button."""
        logger.debug("Clicking Invoices menu button")
        self.invoices_button.click()

    def click_messages(self):
        """Click the Messages menu button."""
        logger.debug("Clicking Messages menu button")
        self.messages_button.click()

    def click_testing_guide(self):
        """Click the Testing Guide menu button.

        Note:
            Renamed from ``verify_testing_guide_wokring`` — this method
            only performs the click and does not assert anything, so it
            follows the ``click_*`` action naming used by its sibling
            methods rather than the ``verify_*`` prefix.
        """
        logger.debug("Clicking Testing Guide menu button")
        self.testing_guide_button.click()

    # ==========================================
    #               VALIDATIONS
    # ==========================================

    def verify_account_page_loaded(self):
        """Verify that the main Account landing page has loaded successfully."""
        logger.info("Verifying account page title is displayed")
        expect(self.page_title).to_have_text(self.PAGE_TITLE_ACCOUNT)

    def verify_account_menu_visible(self):
        """Verify that all sidebar navigation buttons are visible to the user."""
        logger.info("Verifying account sidebar menu is visible")
        expect(self.favorites_button).to_be_visible()
        expect(self.profile_button).to_be_visible()
        expect(self.invoices_button).to_be_visible()
        expect(self.messages_button).to_be_visible()

    # ==========================================
    #        INTEGRATED ACTION & VERIFICATION
    # ==========================================

    def verify_favorites_button_working(self):
        """Click the Favorites button and verify the page title changes to 'Favorites'."""
        self.click_favorites()
        expect(self.page_title).to_have_text(self.PAGE_TITLE_FAVORITES)

    def verify_profile_button_working(self):
        """Click the Profile button and verify the page title changes to 'Profile'."""
        self.click_profile()
        expect(self.page_title).to_have_text(self.PAGE_TITLE_PROFILE)

    def verify_invoices_button_working(self):
        """Click the Invoices button and verify the page title changes to 'Invoices'."""
        self.click_invoices()
        expect(self.page_title).to_have_text(self.PAGE_TITLE_INVOICES)

    def verify_messages_button_working(self):
        """Click the Messages button and verify the page title changes to 'Messages'."""
        self.click_messages()
        expect(self.page_title).to_have_text(self.PAGE_TITLE_MESSAGES)

    def verify_chat_widget_greeting(self):
        """Open the chat widget and verify the default greeting message appears.

        Note:
            Renamed from ``verify_chat_widget_integration_shadow_dom_piercing`` —
            Playwright locators pierce shadow DOM by default, so no special
            piercing logic is implemented here; the previous name overstated
            what the method does.
        """
        logger.info("Opening chat widget and verifying greeting message")
        self.chat_toggle.click()
        expect(self.chat_window).to_contain_text(self.CHAT_GREETING_TEXT)

    def open_bug_hunting_tab(self):
        """Open the Bug Hunting link in a new browser tab.

        Returns:
            playwright.sync_api.Page: The newly opened tab/page object.
        """
        logger.info("Opening Bug Hunting link in a new tab")
        with self.page.context.expect_page() as new_page_info:
            self.bug_hunting_button.click()
        new_tab = new_page_info.value
        new_tab.wait_for_load_state()
        return new_tab

    def verify_bug_hunting_url(self, new_tab):
        """Validate that the Bug Hunting tab opened to the expected external URL.

        Args:
            new_tab: The Page object for the newly opened Bug Hunting tab.
        """
        logger.info("Verifying Bug Hunting tab URL: %s", self.BUG_HUNTING_URL)
        expect(new_tab).to_have_url(self.BUG_HUNTING_URL)

    def verify_bug_hunting_new_tab(self):
        """Open the Bug Hunting link and verify it loads in a new tab with the correct URL.

        Note:
            Renamed from ``verify_iframe_piercing`` — this scenario opens a
            new browser tab/page, not an iframe, so the previous name was
            testing terminology that didn't match the actual behavior.
        """
        new_tab = self.open_bug_hunting_tab()
        self.verify_bug_hunting_url(new_tab)
        new_tab.close()