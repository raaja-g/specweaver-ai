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
                 template_dir: str = "backend/core/templates",
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
        Synthesize test code from test cases with proper functional organization
        
        Returns:
            Dict mapping file type to generated file path
        """
        output_dir = output_dir or Path("tests/generated")
        
        # Organize by functional areas
        features_dir = output_dir / "features"
        steps_dir = output_dir / "steps"
        
        # Create functional subdirectories
        functional_areas = self._identify_functional_areas(test_suite.test_cases)
        for area in functional_areas:
            (steps_dir / area).mkdir(parents=True, exist_ok=True)
        
        features_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # Generate feature files organized by functional area
        for area in functional_areas:
            area_tests = [tc for tc in test_suite.test_cases if self._get_functional_area(tc) == area]
            if area_tests:
                feature_file = self._generate_feature_by_area(requirement, area_tests, area, features_dir, config)
                generated_files[f"feature_{area}"] = feature_file
                
                # Generate step definitions for this area
                steps_file = self._generate_steps_by_area(requirement, area_tests, area, steps_dir / area, config)
                generated_files[f"steps_{area}"] = steps_file
        
        # Generate shared locator repository (not per-test)
        locator_file = self._generate_locators(test_suite.test_cases, output_dir)
        generated_files["locators"] = locator_file
        
        # Generate shared conftest (not per-test)
        conftest_file = self._generate_conftest(config, output_dir)
        generated_files["conftest"] = conftest_file
        
        return generated_files
    
    def _identify_functional_areas(self, test_cases: List[TestCase]) -> List[str]:
        """Identify functional areas from test cases"""
        areas = set()
        for test_case in test_cases:
            area = self._get_functional_area(test_case)
            areas.add(area)
        return sorted(list(areas))
    
    def _get_functional_area(self, test_case: TestCase) -> str:
        """Determine functional area from test case"""
        title_lower = test_case.title.lower()
        
        if any(keyword in title_lower for keyword in ['search', 'find', 'browse', 'filter', 'catalog']):
            return 'search'
        elif any(keyword in title_lower for keyword in ['cart', 'add', 'remove', 'quantity', 'item']):
            return 'cart'
        elif any(keyword in title_lower for keyword in ['checkout', 'payment', 'order', 'billing', 'shipping']):
            return 'checkout'
        elif any(keyword in title_lower for keyword in ['login', 'register', 'auth', 'account', 'profile']):
            return 'auth'
        else:
            # Default area for general tests
            return 'general'
    
    def _generate_feature_by_area(self,
                                 requirement: RequirementGraph,
                                 test_cases: List[TestCase],
                                 area: str,
                                 features_dir: Path,
                                 config: ExecutionConfig) -> Path:
        """Generate feature file for specific functional area"""
        template = self.env.get_template("feature.j2")
        
        content = template.render(
            requirement=requirement,
            test_cases=test_cases,
            functional_area=area,
            config=config,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save feature file
        feature_file = features_dir / f"{area}.feature"
        feature_file.write_text(content)
        logger.info(f"Generated {area} feature file: {feature_file}")
        
        return feature_file
    
    def _generate_steps_by_area(self,
                               requirement: RequirementGraph,
                               test_cases: List[TestCase],
                               area: str,
                               steps_dir: Path,
                               config: ExecutionConfig) -> Path:
        """Generate step definitions for specific functional area"""
        template = self.env.get_template("pytest_steps.j2")
        
        content = template.render(
            requirement=requirement,
            test_cases=test_cases,
            functional_area=area,
            config=config,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Save steps file
        steps_file = steps_dir / f"{area}_steps.py"
        steps_file.write_text(content)
        logger.info(f"Generated {area} steps file: {steps_file}")
        
        return steps_file
    
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
