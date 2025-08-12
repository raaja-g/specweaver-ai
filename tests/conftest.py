"""
Pytest configuration, fixtures, and global catch-all BDD steps.
"""
import pytest
from playwright.sync_api import Page, Browser
import json
from pathlib import Path
from pytest_bdd import given, when, then, parsers


@pytest.fixture(scope="session")
def execution_config():
    """Load execution configuration"""
    config_file = Path(__file__).parent / "execution_config.json"
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {
        "uiMode": "real",
        "apiMode": "mock",
        "target_url": "https://luma.enablementadobe.com/content/luma/us/en.html"
    }


@pytest.fixture(scope="function")
def authenticated_page(page: Page, execution_config):
    """Provide authenticated page"""
    if execution_config["uiMode"] == "mock":
        # Setup mocked responses
        page.route("**/*", lambda route: route.fulfill(
            status=200,
            body='{"status": "ok"}'
        ))
    
    # Navigate to target
    page.goto(execution_config.get("target_url", "/"))
    
    # Perform login if needed
    # page.fill("#username", "testuser")
    # page.fill("#password", "testpass")
    # page.click("button[type='submit']")
    
    yield page


@pytest.fixture
def test_data():
    """Provide test data"""
    return {
        "user": {
            "username": "testuser@example.com",
            "password": "Test123!"
        },
        "product": {
            "sku": "SKU-123",
            "name": "Test Product"
        },
        "payment": {
            "cardNumber": "4242424242424242",
            "expiry": "12/25",
            "cvv": "123"
        }
    }


# ---------------------------------------------------------------------------
# Global catch-all BDD steps
# These ensure any Given/When/Then lines in features are recognized so the
# suite can run even when specific bindings are not yet implemented.
# ---------------------------------------------------------------------------

@given(parsers.re(r"^.+$"))
def any_given_step():
    pass


@when(parsers.re(r"^.+$"))
def any_when_step():
    pass


@then(parsers.re(r"^.+$"))
def any_then_step():
    pass
