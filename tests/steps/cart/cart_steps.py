"""
Generated step definitions for to add a product to my cart and check out with a credit card (cart)
Generated at: 2025-08-12T19:44:24.897091
"""
from pathlib import Path
from typing import Dict, Any
import json
import re
import os

from pytest_bdd import given, when, then, scenarios, parsers
from playwright.sync_api import Page, expect
RUN_HEURISTICS = os.getenv("RUN_HEURISTICS", "0").lower() in {"1", "true", "yes"}

# Bind this step module to its Feature
FEATURE_FILE = Path(__file__).resolve().parents[2] / "features" / ""
scenarios(str(FEATURE_FILE))


# Common environment/setup steps
@given('the test environment is configured')
def setup_environment(page: Page, execution_config):
    # Navigate to base URL so browser visibly opens and context is ready
    try:
        page.set_default_timeout(5000)
        page.set_default_navigation_timeout(10000)
    except Exception:
        pass
    base_url = execution_config.get('target_url', '/')
    page.goto(base_url, wait_until="domcontentloaded")


@given('execution mode is set to "<ui_mode>" for UI and "<api_mode>" for API')
def set_execution_mode(ui_mode: str, api_mode: str):
    # Reserved for future use: mode-specific setup
    pass


# Auto-generated explicit bindings from raw Gherkin lines




# Optional action router for structured actions
@when(parsers.parse('I perform "{action}" with params:\n{params}'))
def perform_action(page: Page, action: str, params: str):
    params_dict: Dict[str, Any] = json.loads(params)
    action_handlers = {
    }
    if handler := action_handlers.get(action):
        handler(page, params_dict)
    else:
        # Fallback: no-op until implemented
        pass

