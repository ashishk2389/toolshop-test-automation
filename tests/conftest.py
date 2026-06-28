import os

import pytest
from playwright.sync_api import sync_playwright
import yaml


@pytest.fixture(scope="function") # Explicitly define it runs per test case
def page():
    # 1. Start the playwright driver manually
    playwright = sync_playwright().start()


    # Change the default 'data-testid' tao 'data-test'
    playwright.selectors.set_test_id_attribute("data-test")

    # 2. Launch the browser (headless=False so you can see it execution)
    browser = playwright.chromium.launch(headless=False)

    # 3. Create the page
    page = browser.new_page()

    # 4. Yield the page to your test
    yield page

    # 5. Teardown: ALWAYS clean up your processes!
    # browser.close()
    # playwright.stop()


@pytest.fixture(scope="session") # Scope session means it reads the YAML file only ONCE for the entire test run
def registration_data():
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "registration_data.yaml"))
    with open(yaml_path, "r") as file:
        return yaml.safe_load(file)
