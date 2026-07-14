import base64
import json
import logging
import os
import time

from playwright.sync_api import APIRequestContext, BrowserContext, Playwright, expect
import pytest
import yaml

logger = logging.getLogger(__name__)

AUTH_STATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "auth.json"))
TRACE_DIR = "traces"


def _decode_jwt_payload(token: str):
    """Decode a JWT payload without requiring external dependencies.

    Args:
        token: The JWT string to decode.

    Returns:
        dict | None: The decoded payload, or None if the token is malformed.
    """
    if not token or token.count(".") != 2:
        return None

    payload_segment = token.split(".")[1]
    padding = "=" * (-len(payload_segment) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload_segment + padding).decode("utf-8")
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _is_cached_auth_state_valid(auth_state_path: str) -> bool:
    """Check whether a cached auth.json file contains a non-expired auth token.

    Args:
        auth_state_path: Path to the cached Playwright storage-state JSON file.

    Returns:
        bool: True if a valid, non-expired auth token was found.
    """
    if not os.path.exists(auth_state_path):
        return False

    try:
        with open(auth_state_path, "r") as handle:
            state = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return False

    for origin in state.get("origins", []):
        for item in origin.get("localStorage", []):
            if item.get("name") != "auth-token":
                continue

            payload = _decode_jwt_payload(item.get("value", ""))
            if not payload:
                continue

            exp = payload.get("exp")
            if exp is None:
                return True

            try:
                return int(time.time()) < int(exp)
            except (TypeError, ValueError):
                return False

    return False


# --- Native Plugin Configurations --------------------------------------

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, session_auth_state):
    """Override the native plugin fixture to inject the cached session state.

    Args:
        browser_context_args: The plugin's default context args.
        session_auth_state: Path to the cached auth state file, or None.

    Returns:
        dict: The context args, with storage_state injected when available.
    """
    if session_auth_state is None:
        return browser_context_args

    return {
        **browser_context_args,
        "storage_state": session_auth_state,
    }


def pytest_addoption(parser):
    """Register the --enable-trace command-line option."""
    parser.addoption(
        "--enable-trace",
        action="store",
        default="on-failure",
        choices=["always", "on-failure", "never"],
        help="Trace recording mode: always, on-failure, never",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Expose test execution status (passed/failed) to fixtures via item.rep_*."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# --- Test Data and Authentication --------------------------------------

@pytest.fixture(scope="session")
def registration_data():
    """Load shared registration/user test data from the YAML data file.

    Returns:
        dict: Parsed contents of registration_data.yaml.
    """
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "data", "registration_data.yaml"))
    with open(yaml_path, "r") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session")
def session_auth_state(request, browser, registration_data):
    """Provide a cached, valid login session, re-authenticating via the UI if needed.

    Runs once per test session. Skips the shared login flow when
    SKIP_SESSION_AUTH_FOR_LOGIN=1 is set, so the dedicated login test can
    perform its own UI login.

    Yields:
        str | None: Path to the cached auth state file, or None when
        session auth is skipped for the current test.
    """
    # Deferred import to avoid importing the pages package at conftest
    # collection time for tests that don't need it.
    from src.pages.login_page import LoginPage

    if os.getenv("SKIP_SESSION_AUTH_FOR_LOGIN") == "1":
        logger.info("Skipping shared session login; login will run in the test itself")
        yield None
        return

    user_info = registration_data["valid_user"]

    if os.path.exists(AUTH_STATE_PATH):
        logger.info("Validating cached session state from auth.json")
        if _is_cached_auth_state_valid(AUTH_STATE_PATH):
            logger.info("Cached session token is still valid")
            yield AUTH_STATE_PATH
            return

        logger.warning("Cached session state is stale or invalid, re-authenticating")
        try:
            os.remove(AUTH_STATE_PATH)
        except OSError:
            pass
    else:
        logger.info("Session state not found, running UI login authentication")

    context = browser.new_context()
    page = context.new_page()

    login_page = LoginPage(page)
    login_page.navigate_to_login_page()
    login_page.verify_login_page_displayed()

    # Perform login action with a fallback to register and retry if needed
    login_page.login_with_fallback(user_info)

    # Validate that the account area is visible after successful login
    expect(page.get_by_role("heading", name="My account")).to_be_visible(timeout=10000)

    page.wait_for_load_state("networkidle")
    context.storage_state(path=AUTH_STATE_PATH)
    context.close()

    logger.info("Session state captured successfully")

    yield AUTH_STATE_PATH


# --- Tracing Controls (Wrapping Native Fixture) -------------------------

@pytest.fixture(scope="function", autouse=True)
def configure_tracing(request, context: BrowserContext):
    """Start and conditionally save a Playwright trace for each test.

    An autouse fixture that hooks into the plugin's native 'context'
    fixture. Trace behavior is controlled by the --enable-trace option:
    "always" saves every trace, "on-failure" saves only failed tests'
    traces, "never" disables tracing entirely.
    """
    trace_mode = request.config.getoption("--enable-trace")

    if trace_mode != "never":
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield

    if trace_mode == "never":
        return

    os.makedirs(TRACE_DIR, exist_ok=True)
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    should_save = trace_mode == "always" or (trace_mode == "on-failure" and test_failed)

    if should_save:
        trace_path = os.path.join(TRACE_DIR, f"{request.node.name}.zip")
        context.tracing.stop(path=trace_path)
        if test_failed:
            logger.info("Failure trace archived to: %s", trace_path)
    else:
        context.tracing.stop()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Override the native plugin's browser launch arguments.

    Headless mode defaults to off (headed) for local debugging visibility,
    but can be enabled via the HEADLESS=true environment variable for CI.

    Returns:
        dict: The launch args, with headless mode applied.
    """
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    return {
        **browser_type_launch_args,
        "headless": headless,
    }


# --- API Authentication --------------------------------------------------

API_LOGIN_URL = "https://api.practicesoftwaretesting.com/users/login"


@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    """Create an authenticated API request context via a programmatic login.

    Credentials are read from the API_TEST_USER_EMAIL and
    API_TEST_USER_PASSWORD environment variables (never hardcode test
    credentials in source control).

    Yields:
        APIRequestContext: A request context with the Bearer token applied,
        if login succeeded.
    """
    email = os.getenv("API_TEST_USER_EMAIL")
    password = os.getenv("API_TEST_USER_PASSWORD")
    if not email or not password:
        pytest.fail(
            "API_TEST_USER_EMAIL and API_TEST_USER_PASSWORD environment variables "
            "must be set to use the api_request_context fixture."
        )

    credentials = {"email": email, "password": password}

    # Spin up a temporary standalone request context to complete the token handshake
    temp_context = playwright.request.new_context()
    login_response = temp_context.post(API_LOGIN_URL, data=credentials)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if login_response.ok:
        token = login_response.json().get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            logger.info("Programmatic API login successful, Bearer token applied")
    else:
        logger.error("Programmatic API login failed, status: %s", login_response.status)

    temp_context.dispose()

    request_context = playwright.request.new_context(extra_http_headers=headers)

    yield request_context

    request_context.dispose()