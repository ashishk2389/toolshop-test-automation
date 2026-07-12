import base64
import json
import os
import time
import pytest
from playwright.sync_api import BrowserContext,Playwright, APIRequestContext, expect
import yaml

AUTH_STATE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "auth.json"))


def _decode_jwt_payload(token: str):
    """Decode a JWT payload without requiring external dependencies."""
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
    """Return True when auth.json contains a non-expired auth-token."""
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


# --- Native Plugin Configurations ---

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, session_auth_state):
    """
    Overriding the native plugin fixture.
    Injects the global JSON session state into every test automatically.
    """
    if session_auth_state is None:
        return browser_context_args

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
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", "data", "registration_data.yaml"))
    with open(yaml_path, "r") as file:
        return yaml.safe_load(file)

@pytest.fixture(scope="session")
def session_auth_state(request, browser, registration_data):
    """
    Runs ONCE per test run using the plugin's native 'browser' instance.
    Skips the shared login flow for the dedicated login test so it performs its own UI login.
    """
    from src.pages.login_page import LoginPage

    if os.getenv("SKIP_SESSION_AUTH_FOR_LOGIN") == "1":
        print("\n🔐 [Setup] Skipping shared session login for test_login; login will run in the test itself.")
        yield None
        return

    user_info = registration_data["valid_user"]

    def _is_authenticated(page):
        try:
            return (
                page.get_by_role("link", name="My account").is_visible(timeout=3000)
                or page.get_by_text("Jane Doe", exact=True).is_visible(timeout=3000)
            )
        except Exception:
            return False

    if os.path.exists(AUTH_STATE_PATH):
        print("\n⚡ [Setup] Validating cached session state from auth.json...")
        if _is_cached_auth_state_valid(AUTH_STATE_PATH):
            print("✅ [Setup] Cached session token is still valid.")
            yield AUTH_STATE_PATH
            return

        print("⚠️ [Setup] Cached session state is stale or invalid. Re-authenticating...")
        try:
            os.remove(AUTH_STATE_PATH)
        except OSError:
            pass
    else:
        print("\n🔑 [Setup] Session state not found. Running UI login authentication...")

    context = browser.new_context()
    page = context.new_page()

    login_page = LoginPage(page)
    login_page.navigateToLoginPage()
    login_page.verify_login_page_displayed()

    # Perform login action with a fallback to register and retry if needed
    login_page.login_with_fallback(user_info)

    # Validate that the account area is visible after successful login
    expect(page.get_by_role("heading", name="My account")).to_be_visible(timeout=10000)

    page.wait_for_load_state("networkidle")
    context.storage_state(path=AUTH_STATE_PATH)

    context.close()
    print("💾 [Setup] Session state captured successfully.")

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