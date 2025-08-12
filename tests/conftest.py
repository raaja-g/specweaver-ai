"""
Pytest configuration, fixtures, logging, and default BDD step definitions
"""
import os
import re
import logging
from pathlib import Path
import json
import pytest
from playwright.sync_api import Page, Browser
from pytest_bdd import given, when, then, parsers

logger = logging.getLogger("bdd")
logger.setLevel(logging.INFO)
# Ensure console handler exists for live visibility
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    _sh = logging.StreamHandler()
    _sh.setLevel(logging.INFO)
    _sh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    logger.addHandler(_sh)


@pytest.fixture(scope="session")
def execution_config():
    """Load execution configuration with env var overrides.

    Precedence:
    1) tests/execution_config.json if present
    2) Environment variables: UI_MODE, API_MODE, TARGET_URL
    3) Hard-coded defaults
    """
    config_file = Path(__file__).parent / "execution_config.json"
    if config_file.exists():
        return json.loads(config_file.read_text())
    return {
        "uiMode": os.getenv("UI_MODE", "real"),
        "apiMode": os.getenv("API_MODE", "mock"),
        "target_url": os.getenv("TARGET_URL", "https://luma.enablementadobe.com/content/luma/us/en.html"),
    }


@pytest.fixture(scope="function")
def authenticated_page(page: Page, execution_config, request: pytest.FixtureRequest):
    """Provide authenticated page with useful logging."""
    # Attach browser event logs if available
    try:
        page.on("console", lambda msg: logger.info(f"[BROWSER CONSOLE] {msg.type} {msg.text}"))
        page.on("request", lambda req: logger.info(f"[REQUEST] {req.method} {req.url}"))
        page.on("response", lambda res: logger.info(f"[RESPONSE] {res.status} {res.url}"))
    except Exception:  # noqa: BLE001
        pass
    if execution_config["uiMode"] == "mock":
        # Setup mocked responses
        page.route("**/*", lambda route: route.fulfill(
            status=200,
            body='{"status": "ok"}'
        ))
    
    # Navigate to target
    target_url = execution_config.get("target_url", "/")
    logger.info(f"[NAVIGATE] {target_url}")
    page.goto(target_url)
    
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


# ---------- Default catch-all BDD steps with logging ----------

STRICT_BDD = os.getenv("STRICT_BDD", "0") == "1"


@given(parsers.parse("{text}"))
def _generic_given(text: str, authenticated_page: Page):
    logger.info(f"[GIVEN] {text}")
    logger.info(f"[PAGE] url={authenticated_page.url}")
    if STRICT_BDD:
        raise AssertionError(f"Missing Given step implementation: {text}")


@when(parsers.parse("{text}"))
def _generic_when(text: str, authenticated_page: Page):
    logger.info(f"[WHEN] {text}")
    logger.info(f"[PAGE] url={authenticated_page.url}")
    if STRICT_BDD:
        raise AssertionError(f"Missing When step implementation: {text}")


@then(parsers.parse("{text}"))
def _generic_then(text: str, authenticated_page: Page):
    logger.info(f"[THEN] {text}")
    logger.info(f"[PAGE] url={authenticated_page.url}")
    if STRICT_BDD:
        raise AssertionError(f"Missing Then step implementation: {text}")


# ---------- Playwright launch args (headed by default) ----------

@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict:
    """Control headless/headed launch.

    Default is headed (visible). Override with env HEADLESS=1 or HEADED=0.
    """
    headless_env = os.getenv("HEADLESS")
    headed_env = os.getenv("HEADED")
    if headless_env is not None:
        headless = headless_env == "1"
    elif headed_env is not None:
        headless = headed_env != "1"
    else:
        headless = False  # headed by default
    return {"headless": headless}


# ---------- Per-test log file handler ----------

@pytest.fixture(autouse=True)
def _bdd_file_logger(request: pytest.FixtureRequest):
    """Write BDD logs to reports/logs/<testname>.log for each test."""
    logs_dir = Path("reports/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    nodeid = request.node.nodeid
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", nodeid)
    file_path = logs_dir / f"{safe_name}.log"

    handler = logging.FileHandler(file_path, encoding="utf-8")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    try:
        yield
    finally:
        logger.removeHandler(handler)
        handler.close()


# ---------- Pytest-BDD hooks for console logging ----------

def pytest_bdd_before_scenario(request, feature, scenario):
    logger.info(f"[SCENARIO START] {scenario.name} | Feature: {feature.name}")


def pytest_bdd_after_scenario(request, feature, scenario):
    logger.info(f"[SCENARIO END] {scenario.name} | Feature: {feature.name}")


def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    logger.info(f"[STEP START] {step.keyword} {step.name}")


def pytest_bdd_after_step(request, feature, scenario, step, step_func):
    logger.info(f"[STEP END] {step.keyword} {step.name}")


def pytest_bdd_step_error(request, feature, scenario, step, step_func, exception):
    logger.exception(f"[STEP ERROR] {step.keyword} {step.name}: {exception}")
