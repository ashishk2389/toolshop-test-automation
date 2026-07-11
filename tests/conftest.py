import json
import os
import pytest
from playwright.sync_api import Browser, BrowserContext,Playwright, APIRequestContext
import yaml
import json

AUTH_STATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "auth.json"))

# --- Native Plugin Configurations ---

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, session_auth_state):
    """
    Overriding the native plugin fixture.
    Injects the global JSON session state into every test automatically.
    """
    return {
        **browser_context_args,
        "storage_state": session_auth_state
    }

def pytest_addoption(parser):
    """Custom command-line options for trace control."""
    parser.addoption(
        "--enable-trace",
        action="store",
        default="on-failure",
        choices=["always", "on-failure", "never"],
        help="Trace recording mode: always, on-failure, never"
    )

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Exposes test execution status (passed/failed) to fixtures."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

# --- Test Data and Authentication ---

@pytest.fixture(scope="session")
def registration_data():
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "registration_data.yaml"))
    with open(yaml_path, "r") as file:
        return yaml.safe_load(file)

@pytest.fixture(scope="session")
def session_auth_state(browser, registration_data) -> str:
    """
    Runs ONCE per test run using the plugin's native 'browser' instance.
    Skips if auth.json already exists.
    """
    from pages.login_page import LoginPage

    if not os.path.exists(AUTH_STATE_PATH):
        print("\n🔑 [Setup] Session state not found. Running UI login authentication...")

        # Uses the 'browser' fixture provided cleanly by the plugin
        context = browser.new_context()
        page = context.new_page()

        user_info = registration_data["valid_user"]

        login_page = LoginPage(page)
        login_page.navigateToLoginPage()
        login_page.verify_login_page_displayed()
        login_page.login(user_info)

        page.wait_for_load_state("networkidle")
        context.storage_state(path=AUTH_STATE_PATH)

        context.close()
        print("💾 [Setup] Session state captured successfully.")
    else:
        print("\n⚡ [Setup] Using cached session state from auth.json. Skipping login UI flow.")

    yield AUTH_STATE_PATH
    #
    # if os.path.exists(AUTH_STATE_PATH):
    #     try:
    #         os.remove(AUTH_STATE_PATH)
    #         print("\n🧹 [Teardown] Session state cache cleared.")
    #     except OSError:
    #         pass

# --- Tracing Controls (Wrapping Native Fixture) ---

@pytest.fixture(scope="function", autouse=True)
def configure_tracing(request, context: BrowserContext):
    """
    An autouse fixture that hooks into the plugin's native 'context'.
    Handles your complex tracing logic dynamically without breaking async loops.
    """
    trace_mode = request.config.getoption("--enable-trace")

    if trace_mode != "never":
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield

    # Teardown: Save trace on condition
    os.makedirs("traces", exist_ok=True)
    test_failed = hasattr(request.node, "rep_call") and request.node.rep_call.failed
    should_save = (trace_mode == "always" or (trace_mode == "on-failure" and test_failed))

    if should_save and trace_mode != "never":
        trace_path = os.path.join("traces", f"{request.node.name}.zip")
        context.tracing.stop(path=trace_path)
        if test_failed:
            print(f"\n📍 Failure Trace archived to: {trace_path}")
    else:
        context.tracing.stop()

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Overrides the native plugin's launch arguments.
    Forces Playwright to open the physical browser window (headed mode).
    """
    return {
        **browser_type_launch_args,
        "headless": False
    }
@pytest.fixture(scope="session")
def api_request_context(playwright: Playwright) -> APIRequestContext:
    """
     Creates an authenticated API context by programmatically logging in
     with a verified test account token payload on session boot.
     """
    # 1. Base endpoints & credentials
    login_url = "https://api.practicesoftwaretesting.com/users/login"
    credentials = {
        "email": "ashishk2389@example.com",
        "password": "Ashi!!!2389"
    }

    # 2. Spin up a temporary standalone request context to complete the token handshake
    temp_context = playwright.request.new_context()
    login_response = temp_context.post(login_url, data=credentials)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # 3. If login succeeds, extract access_token and append Bearer headers
    if login_response.ok:
        token = login_response.json().get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"\n🔑 [API Context] Programmatic login successful. Bearer Token applied globally.")
    else:
        print(f"\n⚠️ [API Context] Programmatic login failed. Status: {login_response.status}")

    temp_context.dispose()

    # 4. Return the official, authenticated request context to your test suite
    request_context = playwright.request.new_context(
        extra_http_headers=headers
    )

    yield request_context

    # Teardown
    request_context.dispose()