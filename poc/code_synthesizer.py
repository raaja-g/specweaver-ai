"""
Code Synthesizer - Generates executable test code from test cases
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import logging

from .schemas import RequirementGraph, TestCase, TestSuite, ExecutionConfig, LocatorRepository
from .llm_orchestrator import LLMOrchestrator

logger = logging.getLogger(__name__)


class CodeSynthesizer:
    """Synthesize executable test code from test cases"""
    
    def __init__(self, 
                 template_dir: str = "poc/templates",
                 orchestrator: Optional[LLMOrchestrator] = None):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.orchestrator = orchestrator or LLMOrchestrator()
    
    def synthesize(self,
                   requirement: RequirementGraph,
                   test_suite: TestSuite,
                   config: ExecutionConfig,
                   output_dir: Optional[Path] = None) -> Dict[str, Path]:
        """
        Synthesize test code from test cases
        
        Returns:
            Dict mapping file type to generated file path
        """
        output_dir = output_dir or Path("tests/generated")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # Generate feature file
        feature_file = self._generate_feature(requirement, test_suite.test_cases, config, output_dir)
        generated_files["feature"] = feature_file
        
        # Generate step definitions
        steps_file = self._generate_steps(requirement, test_suite.test_cases, feature_file.name, output_dir)
        generated_files["steps"] = steps_file
        
        # Generate or update locator repository
        locator_file = self._generate_locators(test_suite.test_cases, output_dir)
        generated_files["locators"] = locator_file
        
        # Generate conftest with fixtures
        conftest_file = self._generate_conftest(config, output_dir)
        generated_files["conftest"] = conftest_file
        
        # Generate execution config
        config_file = self._save_execution_config(config, output_dir)
        generated_files["config"] = config_file
        
        return generated_files
    
    def _generate_feature(self,
                         requirement: RequirementGraph,
                         test_cases: List[TestCase],
                         config: ExecutionConfig,
                         output_dir: Path) -> Path:
        """Generate BDD feature file"""
        template = self.env.get_template("feature.j2")
        
        content = template.render(
            requirement=requirement,
            test_cases=test_cases,
            config=config,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save feature file
        feature_file = output_dir / f"{requirement.id.lower()}.feature"
        feature_file.write_text(content)
        logger.info(f"Generated feature file: {feature_file}")
        
        return feature_file
    
    def _generate_steps(self,
                       requirement: RequirementGraph,
                       test_cases: List[TestCase],
                       feature_file: str,
                       output_dir: Path) -> Path:
        """Generate pytest-bdd step definitions"""
        template = self.env.get_template("pytest_steps.j2")
        
        # Extract unique elements for template
        all_preconditions = set()
        unique_actions = set()
        all_expectations = set()
        
        for tc in test_cases:
            all_preconditions.update(tc.preconditions)
            unique_actions.update(step.action for step in tc.steps)
            all_expectations.update(tc.expected)
        
        content = template.render(
            requirement=requirement,
            feature_file=feature_file,
            all_preconditions=sorted(all_preconditions),
            unique_actions=sorted(unique_actions),
            all_expectations=sorted(all_expectations),
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save step definitions
        steps_file = output_dir / f"test_{requirement.id.lower()}_steps.py"
        steps_file.write_text(content)
        logger.info(f"Generated step definitions: {steps_file}")
        
        return steps_file
    
    def _generate_locators(self,
                          test_cases: List[TestCase],
                          output_dir: Path) -> Path:
        """Generate or update locator repository"""
        # Extract actions that need locators
        ui_actions = set()
        for tc in test_cases:
            for step in tc.steps:
                if not step.action.startswith("api."):
                    ui_actions.add(step.action)
        
        # Generate locators using LLM
        locators = self._derive_locators(ui_actions)
        
        # Save as JSON
        locator_file = output_dir / "locator_repo.json"
        locator_file.write_text(json.dumps(locators, indent=2))
        logger.info(f"Generated locator repository: {locator_file}")
        
        return locator_file
    
    def _derive_locators(self, actions: set) -> Dict[str, Any]:
        """Derive locators for actions"""
        locators = {
            "version": 1,
            "pages": {},
            "created_at": datetime.utcnow().isoformat(),
            "auto_generated": True
        }
        
        for action in actions:
            parts = action.split(".")
            if len(parts) >= 2:
                page = parts[0]
                action_name = ".".join(parts[1:])
                
                if page not in locators["pages"]:
                    locators["pages"][page] = {}
                
                # Generate selector based on action
                selector = self._generate_selector(page, action_name)
                locators["pages"][page][action_name] = selector
        
        return locators
    
    def _generate_selector(self, page: str, action: str) -> List[Dict[str, Any]]:
        """Generate selector for page action"""
        # Common patterns
        selectors = []
        
        if "login" in action or "auth" in page:
            selectors = [
                {"fill": {"selector": "#username", "value": "{{username}}"}},
                {"fill": {"selector": "#password", "value": "{{password}}"}},
                {"click": "button[type='submit']"}
            ]
        elif "add" in action and "cart" in action:
            selectors = [{"click": "button:has-text('Add to cart')"}]
        elif "checkout" in action:
            selectors = [{"click": "button:has-text('Checkout')"}]
        elif "payment" in action:
            selectors = [
                {"fill": {"selector": "#card-number", "value": "{{cardNumber}}"}},
                {"fill": {"selector": "#expiry", "value": "{{expiry}}"}},
                {"fill": {"selector": "#cvv", "value": "{{cvv}}"}}
            ]
        else:
            # Generic selector
            selectors = [{"click": f"[data-action='{action}']"}]
        
        return selectors
    
    def _generate_conftest(self, config: ExecutionConfig, output_dir: Path) -> Path:
        """Generate pytest conftest with fixtures"""
        content = '''"""
Pytest configuration and fixtures
"""
import pytest
from playwright.sync_api import Page, Browser
import json
from pathlib import Path


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
'''
        
        conftest_file = output_dir / "conftest.py"
        conftest_file.write_text(content)
        logger.info(f"Generated conftest: {conftest_file}")
        
        return conftest_file
    
    def _save_execution_config(self, config: ExecutionConfig, output_dir: Path) -> Path:
        """Save execution configuration"""
        config_file = output_dir / "execution_config.json"
        config_file.write_text(config.model_dump_json(indent=2))
        logger.info(f"Saved execution config: {config_file}")
        
        return config_file
