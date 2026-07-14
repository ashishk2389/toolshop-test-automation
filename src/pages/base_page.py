import logging
import re

from playwright.sync_api import Page, expect

logger = logging.getLogger(__name__)


class BasePage:
    """Base Page Object providing shared browser interactions used by every
    page in the suite: navigation, generic element actions/assertions,
    network-asset blocking, and post-login redirect handling.
    """

    # Compiled once at class definition time rather than rebuilt on every
    # intercepted network request (block_assets_and_media previously
    # recreated this set inside the per-request callback).
    BLOCKED_URL_PATTERNS = [
        re.compile(r'\.(?:png|jpg|jpeg|gif|webp|svg)(?:\?|$)'),   # Images
        re.compile(r'\.(?:woff2?|ttf|otf|eot)(?:\?|$)'),          # Fonts
        re.compile(r'\.(?:mp4|webm|ogg|m4a)(?:\?|$)'),            # Media files
        re.compile(r'(?:google-analytics|gtag|analytics|googletagmanager)'),  # Analytics
        re.compile(r'(?:facebook\.com/tr|doubleclick\.net|pixel\.facebook)'),  # Tracking pixels
    ]

    LOGIN_URL_PATTERN = re.compile(r".*/auth/login.*")
    AUTH_REDIRECT_TIMEOUT_MS = 15000

    def __init__(self, page: Page):
        self.page = page
        self._asset_blocking_registered = False
        self.block_assets_and_media()

    # --- Network setup ------------------------------------------------

    def block_assets_and_media(self):
        """Block images, fonts, media files, and analytics/tracking requests.

        Registered once per page instance to speed up test runs; safe to
        call multiple times, subsequent calls are no-ops.
        """
        if self._asset_blocking_registered:
            return

        logger.info("Registering asset/media/analytics request blocking")

        def should_block(route):
            url = route.request.url.lower()
            return any(pattern.search(url) for pattern in self.BLOCKED_URL_PATTERNS)

        self.page.route("**/*", lambda route: (
            route.abort()
            if should_block(route)
            else route.continue_()
        ))
        self._asset_blocking_registered = True

    # --- Navigation ---------------------------------------------------

    def navigate(self, url):
        """Navigate the browser to the given URL.

        Args:
            url: The URL to navigate to.
        """
        logger.info("Navigating to: %s", url)
        self.page.goto(url)

    def navigate_back(self):
        """Navigate back to the previous browser history entry."""
        logger.info("Navigating back to previous page")
        self.page.go_back()

    def wait_for_page_load(self):
        """Wait until the page reaches the network-idle load state."""
        self.page.wait_for_load_state("networkidle")

    def wait_for_authentication(self):
        """Wait for a post-login redirect away from the login page to complete."""
        logger.debug("Waiting for authentication redirect away from login page")
        expect(self.page).not_to_have_url(self.LOGIN_URL_PATTERN, timeout=self.AUTH_REDIRECT_TIMEOUT_MS)
        self.page.wait_for_load_state("networkidle")

    # --- Generic element actions ----------------------------------------

    def click(self, locator):
        """Click the given locator.

        Args:
            locator: The Playwright Locator to click.
        """
        locator.click()

    def fill(self, locator, value):
        """Fill the given locator with a value.

        Args:
            locator: The Playwright Locator to fill.
            value: The text value to enter.
        """
        locator.fill(value)

    def get_text(self, locator) -> str:
        """Return the inner text of the given locator.

        Args:
            locator: The Playwright Locator to read.

        Returns:
            str: The element's inner text.
        """
        return locator.inner_text()

    def is_visible(self, locator) -> bool:
        """Return whether the given locator is currently visible.

        Args:
            locator: The Playwright Locator to check.

        Returns:
            bool: True if visible, False otherwise.
        """
        return locator.is_visible()

    # --- Generic assertions ---------------------------------------------

    def verify_text(self, locator, expected_text):
        """Assert that the given locator has the expected text.

        Args:
            locator: The Playwright Locator to check.
            expected_text: The exact text expected on the element.
        """
        expect(locator).to_have_text(expected_text)

    def verify_visible(self, locator):
        """Assert that the given locator is visible.

        Args:
            locator: The Playwright Locator to check.
        """
        expect(locator).to_be_visible()