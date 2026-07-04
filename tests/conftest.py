import os
import pytest
from playwright.sync_api import sync_playwright
import yaml


def pytest_addoption(parser):
    """Add custom command-line options for trace control."""
    parser.addoption(
        "--enable-trace",
        action="store",
        default="on-failure",
        choices=["always", "on-failure", "never"],
        help="Trace recording mode: always (record all), on-failure (only failures), never (disable)"
    )


@pytest.fixture(scope="function")
def page(request):
    """
    Playwright page fixture with conditional trace recording.
    Traces capture screenshots, DOM snapshots, and source code for debugging.
    """
    trace_mode = request.config.getoption("--enable-trace")

    # 1. Start the playwright driver manually
    playwright = sync_playwright().start()

    # Change the default 'data-testid' to 'data-test'
    playwright.selectors.set_test_id_attribute("data-test")

    # 2. Launch the browser
    browser = playwright.chromium.launch(headless=False)

    # 3. Create browser context and page
    context = browser.new_context()
    page = context.new_page()

    # Start tracing based on mode
    if trace_mode == "always":
        context.tracing.start(
            screenshots=True,      # Capture screenshots at each step
            snapshots=True,        # Capture DOM snapshots for inspection
            sources=True           # Include source files in trace
        )
        should_save_trace = True
    else:
        # Start tracing for on-failure mode, but we'll decide later if we save it
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True
        )
        should_save_trace = False  # Will update based on test result

    # 4. Yield the page to your test
    yield page

    # 5. Teardown: Save trace if needed and clean up
    os.makedirs("traces", exist_ok=True)

    # Determine if test failed
    test_failed = hasattr(request, "node") and hasattr(request.node, "rep_call") and request.node.rep_call.failed

    # Decide whether to save trace
    should_save = (
            trace_mode == "always" or
            (trace_mode == "on-failure" and test_failed)
    )

    if should_save:
        trace_path = os.path.join("traces", f"{request.node.name}.zip")
        context.tracing.stop(path=trace_path)
        if test_failed:
            print(f"\n📍 Trace saved to: {trace_path}")
            print(f"   View trace: playwright show-trace {trace_path}")
    else:
        context.tracing.stop()  # Discard trace

    # Close context and browser
    context.close()
    browser.close()
    playwright.stop()


@pytest.fixture(scope="function")
def failed_test(request):
    """Helper fixture to determine if test failed."""
    yield
    if hasattr(request, "node") and hasattr(request.node, "rep_call"):
        return request.node.rep_call.failed
    return False


@pytest.fixture(scope="session")
def registration_data():
    """Scope session means it reads the YAML file only ONCE for the entire test run."""
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "registration_data.yaml"))
    with open(yaml_path, "r") as file:
        return yaml.safe_load(file)
