"""
Test Case Generator - Generates test cases from RequirementGraph
"""
import json
import re
from typing import List, Dict, Any, Optional
from itertools import product
import logging

from .schemas import RequirementGraph, TestCase, TestStep, TestSuite
from .llm_orchestrator import LLMOrchestrator
from .domain_detector import DomainDetector
from .prompt_loader import PromptLoader

logger = logging.getLogger(__name__)


class TestCaseGenerator:
    """Generate test cases from RequirementGraph using heuristics"""
    
    def __init__(self, orchestrator: Optional[LLMOrchestrator] = None):
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.domain_detector = DomainDetector()
        self.prompt_loader = PromptLoader()
        self.test_counter = 0
    
    def generate(self, 
                 requirement: RequirementGraph,
                 coverage: str = "comprehensive") -> TestSuite:
        """
        Generate comprehensive BDD Features with Scenarios from requirement
        
        Args:
            requirement: Parsed requirement graph
            coverage: "basic" or "comprehensive"
        """
        # Generate comprehensive BDD Features using LLM
        features = self._generate_bdd_features(requirement, coverage)
        
        # Convert Features to TestCase format for compatibility
        test_cases = self._convert_features_to_test_cases(features)
        
        # Calculate coverage metrics
        coverage_metrics = self._calculate_coverage(test_cases, requirement)
        
        return TestSuite(
            requirement_id=requirement.id,
            test_cases=test_cases,
            coverage_metrics=coverage_metrics,
            generation_metadata={
                "coverage_level": coverage,
                "total_cases": len(test_cases),
                "ac_coverage": coverage_metrics.get("ac_coverage", 0),
                "features_generated": len(features)
            }
        )
    
    def _generate_bdd_features(self, requirement: RequirementGraph, coverage: str) -> List[Dict[str, Any]]:
        """Generate comprehensive BDD Features with Scenarios using LLM"""
        
        # Detect domain from requirement
        ac_text = ' '.join([f"{ac.given} {ac.when} {ac.then}" for ac in requirement.acceptanceCriteria])
        requirement_text = f"{requirement.title} {requirement.goal} {ac_text}"
        url = getattr(requirement, 'url', '') or ''
        domain = self.domain_detector.detect_domain(requirement_text, url)
        
        logger.info(f"Detected domain: {domain} for requirement: {requirement.title}")
        
        # Get domain-specific context
        domain_context = self.domain_detector.get_domain_context(domain)
        
        # Load prompt template
        prompt = self.prompt_loader.get_prompt(
            'bdd_generation.main_prompt',
            requirement_json=requirement.model_dump_json(indent=2),
            domain_context=domain_context.get('context', ''),
            domain_examples=domain_context.get('example_features', '')
        )
        
        system_prompt = self.prompt_loader.get_prompt('bdd_generation.system_prompt') or \
                       "You are an expert BDD test designer. Generate comprehensive Features with realistic scenarios."
        
        if not prompt:
            logger.error("Failed to load BDD generation prompt template")
            return self._generate_fallback_features(requirement)
        
        response = self.orchestrator.call(
            prompt=prompt,
            system=system_prompt,
            task_type="bdd_generation"
        )

        # Try to coerce to JSON array safely (strip markdown or prefaces)
        raw = (response.content or "").strip()
        if not raw:
            logger.error("Empty LLM response; using fallback features")
            return self._generate_fallback_features(requirement)

        # Extract first JSON array or object using simple delimiters
        try:
            start = raw.find("[")
            if start == -1:
                start = raw.find("{")
            end = len(raw)
            # Attempt to trim trailing non-JSON
            snippet = raw[start:end] if start != -1 else raw
            features = json.loads(snippet)
            return features if isinstance(features, list) else [features]
        except Exception as e:
            logger.error(f"Failed to parse BDD features: {e}")
            return self._generate_fallback_features(requirement)
    
    def _generate_fallback_features(self, requirement: RequirementGraph) -> List[Dict[str, Any]]:
        """Generate extensive fallback BDD features when LLM fails.
        Deterministic, domain-agnostic but e-commerce-weighted coverage.
        """
        features: List[Dict[str, Any]] = []
        def scen(name: str, steps: List[str]) -> Dict[str, Any]:
            return {"type": "scenario", "name": name, "steps": steps}

        # Homepage & Navigation
        features.append({
            "feature_name": "Homepage & Global Navigation",
            "actor": "shopper",
            "goal": "discover products and actions",
            "benefit": "shop efficiently",
            "background": "Given the site is available",
            "scenarios": [
                scen("Render homepage for a first-time visitor", [
                    "When I open the homepage",
                    "Then I see the cookie consent banner",
                    "And I see the primary navigation and search"
                ]),
                scen("Accept cookie consent", [
                    "Given I have not previously set consent",
                    "When I accept cookies",
                    "Then my consent is recorded"
                ]),
                {"type": "scenario_outline", "name": "Navigate to category", "steps": [
                    "When I select the \"<category>\" menu item",
                    "Then I land on the \"<expected_page>\" listing page"
                ], "examples": [
                    {"category": "Men > Shoes", "expected_page": "Men Shoes"},
                    {"category": "Women > Dresses", "expected_page": "Women Dresses"}
                ]}
            ]
        })

        # Search
        features.append({
            "feature_name": "Search",
            "actor": "shopper",
            "goal": "find relevant products",
            "benefit": "quick discovery",
            "background": "Given I am on any page with a search input",
            "scenarios": [
                {"type": "scenario_outline", "name": "Execute keyword search", "steps": [
                    "When I search for \"<query>\"",
                    "Then I see results relevant to \"<query>\"",
                    "And the total result count is displayed"
                ], "examples": [
                    {"query": "running shoes"},
                    {"query": "128GB phone"},
                    {"query": "blue jeans"}
                ]},
                scen("No-results state", [
                    "When I search for \"zzzxxyy\"",
                    "Then I see a friendly no results message"
                ])
            ]
        })

        # Cart & Checkout (sample)
        features.append({
            "feature_name": "Cart & Mini-cart",
            "actor": "shopper",
            "goal": "manage items",
            "benefit": "complete purchase",
            "background": "Given I have at least one item in my cart",
            "scenarios": [
                scen("View mini-cart", [
                    "When I open the mini-cart",
                    "Then I see line items and subtotal"
                ]),
                scen("Apply coupon code", [
                    "When I apply coupon \"WELCOME10\"",
                    "Then totals reflect the coupon"
                ])
            ]
        })

        return features
    
    def _convert_features_to_test_cases(self, features: List[Dict[str, Any]]) -> List[TestCase]:
        """Convert BDD Features to TestCase format for compatibility"""
        test_cases = []
        
        for feature in features:
            feature_name = feature.get("feature_name", "Unknown Feature")
            scenarios = feature.get("scenarios", [])
            
            for i, scenario in enumerate(scenarios):
                self.test_counter += 1
                scenario_name = scenario.get("name", f"Scenario {i+1}")
                scenario_type = scenario.get("type", "scenario")
                steps = scenario.get("steps", [])
                
                # Determine test type based on scenario content
                test_type = "positive"
                if any(word in scenario_name.lower() for word in ["invalid", "error", "fail", "negative"]):
                    test_type = "negative"
                elif any(word in scenario_name.lower() for word in ["edge", "boundary", "maximum", "minimum"]):
                    test_type = "edge"
                
                # Create test steps
                test_steps = []
                for step in steps:
                    # Parse step into action and params
                    action = self._parse_step_to_action(step)
                    test_steps.append(TestStep(action=action["action"], params=action["params"]))
                
                # Generate examples data if it's a scenario outline
                examples_data = {}
                if scenario_type == "scenario_outline" and "examples" in scenario:
                    examples_data = {"examples": scenario["examples"]}
                
                test_case = TestCase(
                    id=f"TC-{feature_name.replace(' ', '').replace('&', '').upper()[:8]}-{self.test_counter:03d}",
                    title=f"{feature_name}: {scenario_name}",
                    priority="P0" if test_type == "positive" else "P1" if test_type == "negative" else "P2",
                    type=test_type,
                    traceTo=["AC-1"],  # Link to first AC by default
                    preconditions=[feature.get("background", "Given the system is ready")],
                    steps=test_steps,
                    data=examples_data,
                    expected=[f"Scenario '{scenario_name}' completes successfully"],
                    tags=[feature_name.lower().replace(" ", "_"), test_type, scenario_type]
                )
                test_cases.append(test_case)
        
        return test_cases
    
    def _parse_step_to_action(self, step: str) -> Dict[str, Any]:
        """Parse BDD step into action and parameters"""
        step_lower = step.lower()
        
        # Map common BDD steps to actions
        if "click" in step_lower and "add to cart" in step_lower:
            return {"action": "cart.add_item", "params": {"button": "Add to Cart"}}
        elif "search for" in step_lower:
            # Extract search query
            match = re.search(r'"([^"]*)"', step)
            query = match.group(1) if match else "test query"
            return {"action": "search.execute", "params": {"query": query}}
        elif "navigate" in step_lower or "select" in step_lower:
            return {"action": "navigation.goto", "params": {"target": step}}
        elif "enter" in step_lower and ("zip" in step_lower or "postal" in step_lower):
            match = re.search(r'"([^"]*)"', step)
            zip_code = match.group(1) if match else "10001"
            return {"action": "form.enter_zip", "params": {"zip": zip_code}}
        elif "apply" in step_lower and "coupon" in step_lower:
            match = re.search(r'"([^"]*)"', step)
            coupon = match.group(1) if match else "WELCOME10"
            return {"action": "cart.apply_coupon", "params": {"code": coupon}}
        elif "set quantity" in step_lower:
            match = re.search(r'(\d+)', step)
            qty = int(match.group(1)) if match else 1
            return {"action": "product.set_quantity", "params": {"quantity": qty}}
        else:
            return {"action": "user.action", "params": {"description": step}}
    
    def _generate_from_ac(self, 
                          ac: Any, 
                          req: RequirementGraph,
                          test_type: str) -> List[TestCase]:
        """Generate test cases from acceptance criteria"""
        cases = []
        self.test_counter += 1
        
        # Parse AC to identify test steps
        steps = self._parse_ac_to_steps(ac, req)
        
        # Create base test case
        base_case = TestCase(
            id=f"TC-{req.domain or 'GEN'}-{self.test_counter:03d}",
            title=f"{test_type.capitalize()}: {ac.when} -> {ac.then[:50]}",
            priority="P0" if test_type == "positive" else "P1",
            type=test_type,
            traceTo=[ac.id],
            preconditions=[ac.given],
            steps=steps,
            data=self._generate_test_data(steps, test_type),
            expected=[ac.then],
            tags=[req.domain or "general", test_type, "ac-derived"]
        )
        cases.append(base_case)
        
        # Generate variations for comprehensive coverage
        if test_type == "positive":
            cases.extend(self._generate_data_variations(base_case))
        
        return cases
    
    def _parse_ac_to_steps(self, ac: Any, req: RequirementGraph) -> List[TestStep]:
        """Parse acceptance criteria into test steps"""
        steps = []
        
        # Use LLM to break down the AC into steps
        domain_examples = ""
        if "ecommerce" in req.title.lower() or "commerce" in req.title.lower():
            domain_examples = """
E-COMMERCE SPECIFIC ACTIONS:
- navigation.goto_page: {"url": "https://example.com/category/shoes"}
- search.enter_query: {"query": "running shoes", "suggestions": true}
- product.select_variant: {"attribute": "size", "value": "10.5"}
- product.set_quantity: {"quantity": 2}
- cart.add_item: {"sku": "NIKE-001", "quantity": 1}
- cart.apply_coupon: {"code": "WELCOME10"}
- checkout.enter_shipping: {"zip": "10001", "address": "123 Main St"}
- payment.enter_card: {"type": "visa", "number": "4242****", "cvv": "123"}
- order.place: {"confirmation": true}
"""
        
        prompt = f"""
Break down this acceptance criteria into SPECIFIC, ACTIONABLE test steps:

Given: {ac.given}
When: {ac.when}
Then: {ac.then}

Context: {req.title}
Domain: {req.domain or 'general'}

{domain_examples}

REQUIREMENTS:
1. Generate SPECIFIC actions with REAL parameters (not placeholders)
2. Use realistic data (ZIP codes: 10001, 90210; SKUs: NIKE-AIR-001; emails: user@example.com)
3. Each action should be executable and testable
4. Include validation steps where appropriate

EXAMPLE OUTPUT:
[
  {{"action": "navigation.goto_category", "params": {{"category": "men-shoes", "url": "/category/men/shoes"}}}},
  {{"action": "product.select_variant", "params": {{"attribute": "size", "value": "10.5"}}}},
  {{"action": "cart.add_item", "params": {{"sku": "NIKE-AIR-MAX-001", "quantity": 1}}}},
  {{"action": "cart.verify_contents", "params": {{"expected_items": 1, "expected_total": "$129.99"}}}}
]

Return ONLY the JSON array of specific, actionable steps.
"""
        
        response = self.orchestrator.call(
            prompt=prompt,
            system="You are a test automation expert. Generate precise test steps.",
            task_type="test_generation"
        )
        
        try:
            steps_data = json.loads(response.content)
            for step in steps_data:
                steps.append(TestStep(
                    action=step.get("action", "unknown.action"),
                    params=step.get("params", {})
                ))
        except:
            # Fallback: create basic steps from AC
            steps = self._create_fallback_steps(ac)
        
        return steps
    
    def _create_fallback_steps(self, ac: Any) -> List[TestStep]:
        """Create fallback steps from AC"""
        steps = []
        
        # Analyze the when clause for actions
        when_lower = ac.when.lower()
        
        if "login" in when_lower or "log in" in when_lower:
            steps.append(TestStep(action="auth.login", params={"username": "testuser"}))
        
        if "add" in when_lower and "cart" in when_lower:
            steps.append(TestStep(action="product.add_to_cart", params={"sku": "TEST-SKU"}))
        
        if "checkout" in when_lower:
            steps.append(TestStep(action="cart.checkout", params={}))
        
        if "payment" in when_lower or "pay" in when_lower:
            steps.append(TestStep(action="payment.enter_details", params={"method": "card"}))
        
        if "order" in when_lower or "purchase" in when_lower:
            steps.append(TestStep(action="order.place", params={}))
        
        # If no specific actions found, create generic step
        if not steps:
            steps.append(TestStep(action="user.action", params={"description": ac.when}))
        
        return steps
    
    def _generate_negative_cases(self, req: RequirementGraph) -> List[TestCase]:
        """Generate negative test cases"""
        cases = []
        
        # Common negative scenarios
        negative_scenarios = [
            ("Invalid credentials", "auth.login", {"username": "invalid", "password": "wrong"}),
            ("Empty required fields", "form.submit", {"data": {}}),
            ("Out of stock product", "product.add_to_cart", {"sku": "OUT-OF-STOCK"}),
            ("Invalid payment", "payment.process", {"card": "0000000000000000"}),
            ("Expired session", "user.action", {"session": "expired"}),
        ]
        
        for title, action, params in negative_scenarios:
            self.test_counter += 1
            cases.append(TestCase(
                id=f"TC-NEG-{self.test_counter:03d}",
                title=f"Negative: {title}",
                priority="P1",
                type="negative",
                traceTo=["AC-1"],  # Link to first AC by default
                preconditions=["System is accessible"],
                steps=[TestStep(action=action, params=params)],
                data=params,
                expected=["Error message displayed", "Action prevented"],
                tags=["negative", "validation"]
            ))
        
        return cases[:3]  # Limit negative cases
    
    def _generate_edge_cases(self, req: RequirementGraph) -> List[TestCase]:
        """Generate edge/boundary test cases"""
        cases = []
        
        # Boundary value scenarios
        edge_scenarios = [
            ("Maximum quantity", "product.add_to_cart", {"qty": 9999}),
            ("Minimum quantity", "product.add_to_cart", {"qty": 0}),
            ("Special characters in input", "form.input", {"text": "!@#$%^&*()"}),
            ("Very long input", "form.input", {"text": "A" * 1000}),
            ("Concurrent actions", "action.concurrent", {"parallel": True}),
        ]
        
        for title, action, params in edge_scenarios:
            self.test_counter += 1
            cases.append(TestCase(
                id=f"TC-EDGE-{self.test_counter:03d}",
                title=f"Edge: {title}",
                priority="P2",
                type="edge",
                traceTo=["AC-1"],
                preconditions=["System is accessible"],
                steps=[TestStep(action=action, params=params)],
                data=params,
                expected=["System handles edge case gracefully"],
                tags=["edge", "boundary"]
            ))
        
        return cases[:2]  # Limit edge cases
    
    def _generate_test_data(self, steps: List[TestStep], test_type: str) -> Dict[str, Any]:
        """Generate test data for steps"""
        data = {
            "user": {
                "username": "testuser@example.com",
                "password": "Test123!" if test_type == "positive" else "wrong"
            },
            "product": {
                "sku": "SKU-123",
                "name": "Test Product",
                "price": 99.99,
                "quantity": 1
            },
            "payment": {
                "cardNumber": "4242424242424242" if test_type == "positive" else "0000000000000000",
                "expiry": "12/25",
                "cvv": "123"
            },
            "address": {
                "line1": "123 Test St",
                "city": "Test City",
                "zip": "12345"
            }
        }
        return data
    
    def _generate_data_variations(self, base_case: TestCase) -> List[TestCase]:
        """Generate data-driven variations"""
        variations = []
        
        # Different data sets
        data_sets = [
            {"description": "with promo code", "promo": "SAVE10"},
            {"description": "with multiple items", "quantity": 5},
            {"description": "with different payment", "payment_method": "paypal"},
        ]
        
        for i, data_set in enumerate(data_sets, 1):
            self.test_counter += 1
            variation = TestCase(
                id=f"TC-VAR-{self.test_counter:03d}",
                title=f"{base_case.title} {data_set['description']}",
                priority=base_case.priority,
                type=base_case.type,
                traceTo=base_case.traceTo,
                preconditions=base_case.preconditions,
                steps=base_case.steps,
                data={**base_case.data, **data_set},
                expected=base_case.expected,
                tags=base_case.tags + ["variation"]
            )
            variations.append(variation)
        
        return variations[:2]  # Limit variations
    
    def _apply_test_heuristics(self, 
                               cases: List[TestCase],
                               req: RequirementGraph) -> List[TestCase]:
        """Apply ECP/BVA and other heuristics"""
        # This is where we'd apply:
        # - Equivalence Class Partitioning
        # - Boundary Value Analysis
        # - Decision Tables
        # - State Transitions
        
        # For now, just ensure we have good coverage
        return cases
    
    def _deduplicate_cases(self, cases: List[TestCase]) -> List[TestCase]:
        """Remove duplicate test cases"""
        seen = set()
        unique = []
        
        for case in cases:
            # Create signature from steps and data (handle nested dicts)
            data_signature = []
            if isinstance(case.data, dict):
                try:
                    # Flatten nested dicts to avoid unhashable issues
                    flat_data = {}
                    for k, v in case.data.items():
                        if isinstance(v, dict):
                            flat_data[k] = str(v)  # Convert nested dicts to strings
                        else:
                            flat_data[k] = v
                    data_signature = tuple(sorted(flat_data.items()))
                except Exception:
                    # Fallback: use string representation
                    data_signature = str(case.data)
            
            signature = (
                case.type,
                tuple(step.action for step in case.steps),
                data_signature
            )
            
            if signature not in seen:
                seen.add(signature)
                unique.append(case)
        
        return unique
    
    def _calculate_coverage(self, 
                           cases: List[TestCase],
                           req: RequirementGraph) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        ac_ids = {ac.id for ac in req.acceptanceCriteria}
        covered_acs = set()
        
        for case in cases:
            covered_acs.update(case.traceTo)
        
        coverage = {
            "ac_coverage": len(covered_acs) / len(ac_ids) * 100 if ac_ids else 0,
            "total_acs": len(ac_ids),
            "covered_acs": len(covered_acs),
            "uncovered_acs": list(ac_ids - covered_acs),
            "test_types": {
                "positive": sum(1 for c in cases if c.type == "positive"),
                "negative": sum(1 for c in cases if c.type == "negative"),
                "edge": sum(1 for c in cases if c.type == "edge")
            }
        }
        
        return coverage
