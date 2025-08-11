"""
Test Case Generator - Generates test cases from RequirementGraph
"""
import json
from typing import List, Dict, Any, Optional
from itertools import product
import logging

from .schemas import RequirementGraph, TestCase, TestStep, TestSuite
from .llm_orchestrator import LLMOrchestrator

logger = logging.getLogger(__name__)


class TestCaseGenerator:
    """Generate test cases from RequirementGraph using heuristics"""
    
    def __init__(self, orchestrator: Optional[LLMOrchestrator] = None):
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.test_counter = 0
    
    def generate(self, 
                 requirement: RequirementGraph,
                 coverage: str = "comprehensive") -> TestSuite:
        """
        Generate test cases from requirement
        
        Args:
            requirement: Parsed requirement graph
            coverage: "basic" or "comprehensive"
        """
        test_cases = []
        
        # Generate positive test cases from acceptance criteria
        for ac in requirement.acceptanceCriteria:
            test_cases.extend(self._generate_from_ac(ac, requirement, "positive"))
        
        # Generate negative test cases
        if coverage == "comprehensive":
            test_cases.extend(self._generate_negative_cases(requirement))
            test_cases.extend(self._generate_edge_cases(requirement))
        
        # Apply ECP/BVA heuristics
        test_cases = self._apply_test_heuristics(test_cases, requirement)
        
        # Deduplicate
        test_cases = self._deduplicate_cases(test_cases)
        
        # Calculate coverage metrics
        coverage_metrics = self._calculate_coverage(test_cases, requirement)
        
        return TestSuite(
            requirement_id=requirement.id,
            test_cases=test_cases,
            coverage_metrics=coverage_metrics,
            generation_metadata={
                "coverage_level": coverage,
                "total_cases": len(test_cases),
                "ac_coverage": coverage_metrics.get("ac_coverage", 0)
            }
        )
    
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
        prompt = f"""
Break down this acceptance criteria into specific test steps:
Given: {ac.given}
When: {ac.when}
Then: {ac.then}

Context: {req.title}
Domain: {req.domain or 'general'}

Generate a list of semantic actions (e.g., login.enter_credentials, product.add_to_cart).
Return as JSON array of steps with action and params.
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
            # Create signature from steps and data
            signature = (
                case.type,
                tuple(step.action for step in case.steps),
                tuple(sorted(case.data.items()) if isinstance(case.data, dict) else [])
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
