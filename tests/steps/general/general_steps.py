"""
Generated step definitions for Auto Synthesized (general)
Generated at: 2025-08-12T19:01:59.024773
"""
from pathlib import Path
from typing import Dict, Any
import json
import re

from pytest_bdd import given, when, then, scenarios, parsers
from playwright.sync_api import Page, expect

# Bind this step module to its Feature
FEATURE_FILE = Path(__file__).resolve().parents[2] / "features" / "general.feature"
scenarios(str(FEATURE_FILE))


# Common environment/setup steps
@given('the test environment is configured')
def setup_environment(page: Page, execution_config):
    # Navigate to base URL so browser visibly opens and context is ready
    base_url = execution_config.get('target_url', '/')
    page.goto(base_url)


@given('execution mode is set to "<ui_mode>" for UI and "<api_mode>" for API')
def set_execution_mode(ui_mode: str, api_mode: str):
    # Reserved for future use: mode-specific setup
    pass


# Auto-generated explicit bindings from raw Gherkin lines
# Given steps
@given("I am a logged-in user with two saved credit cards, 'Visa ending in 4242' and 'Mastercard ending in 5555'")
def given_1(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am a logged-in user with two saved credit cards, 'Visa ending in 4242' and 'Mastercard ending in 5555'", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("I am on the cart page")
def given_2(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am on the cart page", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("I am on the cart page with a subtotal of $200.00")
def given_3(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am on the cart page with a subtotal of $200.00", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("I am on the cart page with a subtotal of $45.00")
def given_4(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am on the cart page with a subtotal of $45.00", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("I am on the cart page with a subtotal of $80.00")
def given_5(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am on the cart page with a subtotal of $80.00", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("I am on the product page for 'Limited Edition Compass' (SKU: CMP-LTD-01)")
def given_6(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am on the product page for 'Limited Edition Compass' (SKU: CMP-LTD-01)", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("I am on the product page for 'TrailMax Hiking Backpack'")
def given_7(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am on the product page for 'TrailMax Hiking Backpack'", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("I am on the product page for 'TrailMax Hiking Backpack' (SKU: HBP-GRN-40L)")
def given_8(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "I am on the product page for 'TrailMax Hiking Backpack' (SKU: HBP-GRN-40L)", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass
@given("my payment attempt with the Visa card was declined")
def given_9(page: Page, execution_config):
    # Heuristic: if the step declares a page state, open the base URL
    base_url = execution_config.get('target_url', '/')
    if re.search(r"\bI am on\b|\bpage\b|\bhomepage\b", "my payment attempt with the Visa card was declined", flags=re.IGNORECASE):
        page.goto(base_url)
    # Additional preconditions can be implemented here
    pass

# When steps
@when("I click 'Apply'")
def when_1(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I click 'Apply'", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I click 'Apply'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I click 'Apply'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I click 'Apply'", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I enter the discount code 'ALREADYUSED'")
def when_2(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I enter the discount code 'ALREADYUSED'", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I enter the discount code 'ALREADYUSED'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I enter the discount code 'ALREADYUSED'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I enter the discount code 'ALREADYUSED'", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I enter the discount code 'EXPIRED2020'")
def when_3(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I enter the discount code 'EXPIRED2020'", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I enter the discount code 'EXPIRED2020'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I enter the discount code 'EXPIRED2020'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I enter the discount code 'EXPIRED2020'", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I enter the discount code 'INVALIDCODE'")
def when_4(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I enter the discount code 'INVALIDCODE'", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I enter the discount code 'INVALIDCODE'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I enter the discount code 'INVALIDCODE'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I enter the discount code 'INVALIDCODE'", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I enter the discount code 'SAVE50' which requires a $50 minimum spend")
def when_5(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I enter the discount code 'SAVE50' which requires a $50 minimum spend", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I enter the discount code 'SAVE50' which requires a $50 minimum spend", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I enter the discount code 'SAVE50' which requires a $50 minimum spend", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I enter the discount code 'SAVE50' which requires a $50 minimum spend", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I enter the valid discount code 'SAVE15' in the discount code field")
def when_6(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I enter the valid discount code 'SAVE15' in the discount code field", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I enter the valid discount code 'SAVE15' in the discount code field", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I enter the valid discount code 'SAVE15' in the discount code field", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I enter the valid discount code 'SAVE15' in the discount code field", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I enter the valid discount code 'TENOFF' in the discount code field")
def when_7(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I enter the valid discount code 'TENOFF' in the discount code field", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I enter the valid discount code 'TENOFF' in the discount code field", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I enter the valid discount code 'TENOFF' in the discount code field", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I enter the valid discount code 'TENOFF' in the discount code field", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I scroll down to the 'Reviews' section")
def when_8(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I scroll down to the 'Reviews' section", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I scroll down to the 'Reviews' section", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I scroll down to the 'Reviews' section", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I scroll down to the 'Reviews' section", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I select the 'Mastercard ending in 5555'")
def when_9(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I select the 'Mastercard ending in 5555'", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I select the 'Mastercard ending in 5555'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I select the 'Mastercard ending in 5555'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I select the 'Mastercard ending in 5555'", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I select the color 'Ocean Blue'")
def when_10(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I select the color 'Ocean Blue'", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I select the color 'Ocean Blue'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I select the color 'Ocean Blue'", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I select the color 'Ocean Blue'", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass
@when("I submit the payment again")
def when_11(page: Page):
    # Heuristics for common actions
    m = re.search(r"click (?:the )?'([^']+)' (?:button|link)", "I submit the payment again", re.IGNORECASE)
    if m:
        name = m.group(1)
        try:
            page.get_by_role('button', name=name).click()
        except Exception:
            page.get_by_text(name, exact=False).first.click()
        return
    m = re.search(r"enter '([^']*)' .*email", "I submit the payment again", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Email', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='email']", m.group(1))
    m = re.search(r"password '([^']+)'", "I submit the payment again", re.IGNORECASE)
    if m:
        try:
            page.get_by_label('Password', exact=False).fill(m.group(1))
        except Exception:
            page.fill("input[type='password']", m.group(1))
    m = re.search(r"enter \"([^\"]+)\" .*search bar.*press Enter", "I submit the payment again", re.IGNORECASE)
    if m:
        term = m.group(1)
        try:
            page.get_by_placeholder('Search', exact=False).fill(term)
        except Exception:
            page.fill('input[type="search"]', term)
        page.keyboard.press('Enter')
    # Extend with more heuristics as needed
    pass

# Then steps
@then("I see a message 'Discount code SAVE15 applied successfully.'")
def then_1(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I see a message 'Discount code SAVE15 applied successfully.'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should proceed to the order review page")
def then_2(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should proceed to the order review page")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see a color selector with options 'Forest Green', 'Ocean Blue', and 'Slate Grey'")
def then_3(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see a color selector with options 'Forest Green', 'Ocean Blue', and 'Slate Grey'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see a gallery with at least 3 product images")
def then_4(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see a gallery with at least 3 product images")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see a list of customer reviews with reviewer names, ratings, and comments")
def then_5(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see a list of customer reviews with reviewer names, ratings, and comments")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see a stock status message 'In Stock'")
def then_6(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see a stock status message 'In Stock'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see a stock status message 'Out of Stock'")
def then_7(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see a stock status message 'Out of Stock'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see an average star rating, such as '4.7 out of 5 stars'")
def then_8(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see an average star rating, such as '4.7 out of 5 stars'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see an error message 'Discount code 'INVALIDCODE' is not valid.'")
def then_9(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see an error message 'Discount code 'INVALIDCODE' is not valid.'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see an error message 'This discount code has already been used.'")
def then_10(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see an error message 'This discount code has already been used.'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see an error message 'This discount code is expired.'")
def then_11(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see an error message 'This discount code is expired.'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see an error message 'This discount code requires a minimum purchase of $50.00.'")
def then_12(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see an error message 'This discount code requires a minimum purchase of $50.00.'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see an option to 'Notify me when back in stock'")
def then_13(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see an option to 'Notify me when back in stock'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see the price '$99.95'")
def then_14(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see the price '$99.95'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see the product name 'Limited Edition Compass'")
def then_15(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see the product name 'Limited Edition Compass'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("I should see the product name 'TrailMax Hiking Backpack'")
def then_16(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "I should see the product name 'TrailMax Hiking Backpack'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("a line item for 'Discount (15%)' appears with a value of '-$30.00'")
def then_17(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "a line item for 'Discount (15%)' appears with a value of '-$30.00'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("a line item for 'Discount' appears with a value of '-$10.00'")
def then_18(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "a line item for 'Discount' appears with a value of '-$10.00'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("the 'Add to Cart' button should be disabled")
def then_19(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "the 'Add to Cart' button should be disabled")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("the SKU displayed on the page should update to 'HBP-BLU-40L'")
def then_20(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "the SKU displayed on the page should update to 'HBP-BLU-40L'")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("the main product image should update to show the blue backpack")
def then_21(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "the main product image should update to show the blue backpack")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("the order total is updated to $170.00")
def then_22(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "the order total is updated to $170.00")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("the order total is updated to $70.00")
def then_23(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "the order total is updated to $70.00")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("the order total should not change")
def then_24(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "the order total should not change")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass
@then("the payment should be authorized successfully")
def then_25(page: Page):
    # Generic visibility checks for expected text phrases
    m = re.search(r"'([^']+)'", "the payment should be authorized successfully")
    if m:
        expect(page.get_by_text(m.group(1), exact=False)).to_be_visible()
        return
    # Otherwise leave as TODO
    pass


# Optional action router for structured actions
@when(parsers.parse('I perform "{action}" with params:\n{params}'))
def perform_action(page: Page, action: str, params: str):
    params_dict: Dict[str, Any] = json.loads(params)
    action_handlers = {
        "navigation.goto": handle_navigation_goto,
        "user.action": handle_user_action,
    }
    if handler := action_handlers.get(action):
        handler(page, params_dict)
    else:
        # Fallback: no-op until implemented
        pass

def handle_navigation_goto(page: Page, params: Dict[str, Any]):
    # TODO: implement handler for navigation.goto
    pass
def handle_user_action(page: Page, params: Dict[str, Any]):
    # TODO: implement handler for user.action
    pass
