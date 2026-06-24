from playwright.sync_api import Page, expect


class BasePage:

    def __init__(self, page: Page):
        self.page = page


    # Navigation
    def navigate(self, url):
        self.page.goto(url)


    # Click actions
    def click(self, locator):
        locator.click()


    # Fill input
    def fill(self, locator, value):
        locator.fill(value)


    # Get text
    def get_text(self, locator):
        return locator.inner_text()


    # Visibility checks
    def is_visible(self, locator):
        return locator.is_visible()


    # Wait
    def wait_for_page_load(self):
        self.page.wait_for_load_state("networkidle")


    # Assertions
    def verify_text(self, locator, expected_text):
        expect(locator).to_have_text(expected_text)


    def verify_visible(self, locator):
        expect(locator).to_be_visible()