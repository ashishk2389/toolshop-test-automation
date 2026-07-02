from pages.base_page import BasePage
from playwright.sync_api import expect


class AccountPage(BasePage):
    """
    Page Object Model representing the Customer 'My Account' landing page
    and its sub-navigation menu on practicesoftwaretesting.com.
    """

    def __init__(self, page):
        super().__init__(page)

        # Main Page Header Element
        self.page_title = page.locator("[data-test='page-title']")

        # Account Sidebar Menu Navigation Elements
        # Using role="link" because these selections function as anchor (<a>) application routes
        self.favorites_button = page.get_by_role("button", name="Favorites")
        self.profile_button = page.get_by_role("button", name="Profile")
        self.invoices_button = page.get_by_role("button", name="Invoices")
        self.messages_button = page.get_by_role("button", name="Messages")
        self.testing_guide = page.get_by_role("button", name=" Testing Guide ")
        self.bug_hunting = page.get_by_role("button", name=" 🐛 Bug Hunting ")
        self.chat_toggle = page.locator("[data-test='chat-toggle']")
        self.chat_window = page.locator("[data-test='chat-window']")


    # ==========================================
    #                 ACTIONS
    # ==========================================

    def click_favorites(self):
        """Clicks the Favorites menu link."""
        self.favorites_button.click()

    def click_profile(self):
        """Clicks the Profile menu link."""
        self.profile_button.click()

    def click_invoices(self):
        """Clicks the Invoices menu link."""
        self.invoices_button.click()

    def click_messages(self):
        """Clicks the Messages menu link."""
        self.messages_button.click()


    # ==========================================
    #               VALIDATIONS
    # ==========================================

    def verify_account_page_loaded(self):
        """Verifies that the main Account landing page has loaded successfully."""
        expect(self.page_title).to_have_text("My account")

    def verify_account_menu_visible(self):
        """Verifies that all sidebar navigation links are fully visible to the user."""
        expect(self.favorites_button).to_be_visible()
        expect(self.profile_button).to_be_visible()
        expect(self.invoices_button).to_be_visible()
        expect(self.messages_button).to_be_visible()

    # ==========================================
    #        INTEGRATED ACTION & VERIFICATION
    # ==========================================

    def verify_favorites_button_working(self):
        """Clicks the Favorites link and verifies the page title changes to 'Favorites'."""
        self.click_favorites()
        expect(self.page_title).to_have_text("Favorites")

    def verify_profile_button_working(self):
        """Clicks the Profile link and verifies the page title changes to 'Profile'."""
        self.click_profile()
        expect(self.page_title).to_have_text("Profile")

    def verify_invoices_button_working(self):
        """Clicks the Invoices link and verifies the page title changes to 'Invoices'."""
        self.click_invoices()
        expect(self.page_title).to_have_text("Invoices")

    def verify_messages_button_working(self):
        """Clicks the Messages link and verifies the page title changes to 'Messages'."""
        self.click_messages()
        expect(self.page_title).to_have_text("Messages")
    def verify_testing_guide_wokring(self):
        #click on the testing  guidde
        self.testing_guide.click()

    def verify_chat_widget_integration_shadow_dom_piercing(self):
        self.chat_toggle.click()
        expect(self.chat_window).to_contain_text(' Hi! How can I help you today? ')

    def open_bug_hunting_tab(self):
        """Open the bug hunting link in a new tab and return the new page object."""
        with self.page.context.expect_page() as new_page_info:
            self.bug_hunting.click()
        new_tab = new_page_info.value
        new_tab.wait_for_load_state()
        return new_tab

    def verify_bug_hunting_url(self, new_tab):
        """Validate that the bug hunting tab opened to the expected external URL."""
        expect(new_tab).to_have_url('https://with-bugs.practicesoftwaretesting.com/#/?bug-hunting=true')

    def verify_iframe_piercing(self):
        new_tab = self.open_bug_hunting_tab()
        self.verify_bug_hunting_url(new_tab)
        new_tab.close()

