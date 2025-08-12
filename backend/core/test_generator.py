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
from .dynamic_test_generator import DynamicTestGenerator

logger = logging.getLogger(__name__)


class TestCaseGenerator:
    """Generate test cases from RequirementGraph using heuristics"""
    
    def __init__(self, orchestrator: Optional[LLMOrchestrator] = None):
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.domain_detector = DomainDetector()
        self.prompt_loader = PromptLoader()
        self.dynamic_generator = DynamicTestGenerator()
        self.test_counter = 0

    def _sanitize_tags(self, tags: List[str]) -> List[str]:
        """Sanitize and de-duplicate tags for Gherkin (@tag)."""
        seen = set()
        clean: List[str] = []
        for t in tags:
            if not t:
                continue
            s = str(t).lower()
            s = s.replace(' ', '_')
            s = s.replace('&', '_and_')
            s = re.sub(r"[^a-z0-9_\-]", "", s)
            if s and s not in seen:
                seen.add(s)
                clean.append(s)
        return clean
    
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
        test_cases = self._deduplicate_cases(test_cases)
        
        # If the LLM returned too few, augment deterministically to reach >= 30 scenarios
        if len(test_cases) < 40:
            # ensure a large, meaningful set for domain
            needed = 40 - len(test_cases)
            supplements = self._augment_tests(requirement, needed)
            test_cases.extend(supplements)
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
                "ac_coverage": coverage_metrics.get("ac_coverage", 0),
                "features_generated": len(features)
            }
        )

    def _augment_tests(self, requirement: RequirementGraph, needed: int) -> List[TestCase]:
        """Create additional negative/edge cases deterministically to reach target volume."""
        supplements: List[TestCase] = []
        # Detect domain to pick augmentation set
        ac_text = ' '.join([f"{ac.given} {ac.when} {ac.then}" for ac in requirement.acceptanceCriteria])
        requirement_text = f"{requirement.title} {requirement.goal} {ac_text}"
        url = getattr(requirement, 'url', '') or ''
        domain = self.domain_detector.detect_domain(requirement_text, url)

        # Diverse corporate-site templates
        corporate_templates = [
            ("Top navigation links work", "positive", "P0", [
                "Given I am on the homepage",
                "When I click \"Products\" in the top navigation",
                "Then I land on the Products page"
            ]),
            ("Site search returns results", "positive", "P0", [
                "Given I am on the homepage",
                "When I search the site for \"firewall\"",
                "Then I see a site results page with relevant items"
            ]),
            ("Resources download gated by form", "positive", "P1", [
                "Given I am on a whitepaper resource page",
                "When I request download",
                "Then I am shown a lead capture form"
            ]),
            ("Resources form validation", "negative", "P1", [
                "Given I am on a lead capture form",
                "When I submit with an invalid email",
                "Then I see an error \"Enter a valid email\""
            ]),
            ("Cookie consent banner can be accepted", "positive", "P2", [
                "Given a cookie banner is displayed",
                "When I click \"Accept All\"",
                "Then the banner disappears"
            ]),
            ("Language selector switches locale", "edge", "P2", [
                "Given I am on the homepage",
                "When I change language to \"Deutsch\"",
                "Then interface text updates to German"
            ]),
            ("Footer links open correct pages", "positive", "P2", [
                "Given I am at the bottom of a page",
                "When I click \"Privacy\" in the footer",
                "Then I land on the Privacy page"
            ]),
            ("Contact form submits successfully", "positive", "P0", [
                "Given I filled Name, Work Email, and Message",
                "When I submit the contact form",
                "Then I see a confirmation message"
            ]),
            ("Careers job search filters", "edge", "P2", [
                "Given I am on the Careers page",
                "When I filter jobs by \"Location: US\" and \"Department: Engineering\"",
                "Then I see matching job listings"
            ]),
            ("Newsletter signup requires consent", "negative", "P1", [
                "Given I am on a signup module",
                "When I submit without consenting to terms",
                "Then I see an error indicating consent is required"
            ]),
            ("Primary CTA navigates to request demo", "positive", "P0", [
                "Given I am on a product landing page",
                "When I click \"Request a Demo\"",
                "Then I am taken to the demo request form"
            ]),
            ("Broken link check for hero CTAs", "edge", "P2", [
                "Given I am on the homepage",
                "When I click the hero CTA",
                "Then the destination returns status 200"
            ]),
            ("Mobile menu opens and closes", "edge", "P2", [
                "Given I am on a mobile viewport",
                "When I tap the hamburger menu",
                "Then the mobile menu expands"
            ]),
        ]

        ecommerce_templates = [
            ("Add to cart from PLP", "positive", "P0", [
                "Given I am on a category listing",
                "When I add the first item to cart",
                "Then mini-cart shows item count increased"
            ]),
            ("Coupon rejected when expired", "negative", "P1", [
                "Given my cart has eligible items",
                "When I apply coupon \"EXPIRED50\"",
                "Then I see a message that the coupon is no longer valid"
            ]),
            ("Checkout as guest basic flow", "positive", "P0", [
                "Given I proceed to checkout as guest",
                "When I provide shipping and payment",
                "Then the order is placed successfully"
            ]),
        ]

        search_templates = [
            ("Results show tabs", "positive", "P0", [
                "Given I searched for \"cloud security\"",
                "Then I see tabs for \"All\", \"Images\", \"Videos\", and \"News\""
            ]),
            ("People also ask toggles", "edge", "P2", [
                "Given I am on the results page",
                "When I expand a \"People also ask\" question",
                "Then I see an expanded answer"
            ]),
        ]

        if domain == 'ecommerce':
            templates = ecommerce_templates
        elif domain == 'search_engine':
            templates = search_templates
        else:
            templates = corporate_templates
        i = 0
        while len(supplements) < needed:
            title, ttype, prio, steps_lines = templates[i % len(templates)]
            self.test_counter += 1
            steps = [TestStep(action="user.step", params={"line": s}) for s in steps_lines]
            supplements.append(TestCase(
                id=f"TC-AUTO-{self.test_counter:03d}",
                title=f"Augmented: {title}",
                priority=prio, type=ttype, traceTo=["AC-1"],
                preconditions=["Given the system is ready"], steps=steps,
                data={"raw_steps": steps_lines, "scenario_name": title},
                expected=["Appropriate system behavior occurs"], tags=["auto", ttype]
            ))
            i += 1
        return supplements
    
    def _generate_bdd_features(self, requirement: RequirementGraph, coverage: str) -> List[Dict[str, Any]]:
        """Generate comprehensive BDD Features with Scenarios using LLM or dynamic scraping"""
        
        # Check if we have a URL for dynamic generation
        url = getattr(requirement, 'url', '') or ''
        logger.info(f"Requirement URL: '{url}' (type: {type(url)})")
        
        if url and url.startswith(('http://', 'https://')):
            logger.info(f"URL detected: {url}. Using dynamic test generation based on actual website structure.")
            try:
                # Use dynamic generation based on actual website scraping
                logger.info("Starting dynamic generation...")
                features = self.dynamic_generator.generate_tests_from_website(url, headless=True)
                logger.info(f"Dynamic generation completed. Features: {len(features) if features else 0}")
                
                if features and len(features) > 0:
                    logger.info(f"Dynamic generation successful. Generated {len(features)} features.")
                    return features
                else:
                    logger.warning("Dynamic generation returned no features, falling back to LLM generation.")
            except Exception as e:
                logger.error(f"Dynamic generation failed with error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.info("Falling back to LLM generation.")
        else:
            logger.info(f"No valid URL found. URL value: '{url}'. Using LLM generation.")
        
        # Fall back to LLM-based generation
        logger.info("Using LLM-based test generation.")
        return self._generate_llm_bdd_features(requirement, coverage)
    
    def _generate_llm_bdd_features(self, requirement: RequirementGraph, coverage: str) -> List[Dict[str, Any]]:
        """Generate BDD features using LLM (original method)"""
        
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

        # Robustly extract first JSON array/object (ignore trailing text)
        raw = (response.content or "").strip()
        if not raw:
            logger.error("Empty LLM response; using fallback features")
            return self._generate_fallback_features(requirement)

        def strip_code_fences(text: str) -> str:
            t = text.strip()
            if t.startswith("```"):
                try:
                    first_nl = t.find("\n")
                    t = t[first_nl+1:]
                    if t.endswith("```"):
                        t = t[:-3]
                except Exception:
                    pass
            return t

        try:
            text = strip_code_fences(raw)
            # Find first JSON start
            s_idx = text.find("[")
            start_is_array = True
            if s_idx == -1:
                s_idx = text.find("{")
                start_is_array = False
            if s_idx == -1:
                raise ValueError("No JSON start token found")
            from json import JSONDecoder
            dec = JSONDecoder()
            obj, end = dec.raw_decode(text[s_idx:])
            # obj may be an object or array
            features = obj if isinstance(obj, list) else [obj]
            # Domain-based safety filter: drop e-commerce-only features if domain isn't ecommerce
            if domain != 'ecommerce':
                features = self._filter_features_by_domain(features, domain)
            return features
        except Exception as e:
            logger.error(f"Failed to parse BDD features: {e}")
            return self._generate_fallback_features(requirement)

    def _feature_looks_ecommerce(self, feature: Dict[str, Any]) -> bool:
        name = str(feature.get("feature_name", "")).lower()
        text = " ".join([
            name,
            str(feature.get("background", "")),
            " ".join([str(s.get("name", "")) for s in feature.get("scenarios", [])])
        ]).lower()
        ecommerce_markers = [
            "product", "cart", "checkout", "coupon", "sku", "price", "variant",
            "pdp", "plp", "wishlist", "facets", "sort", "mini-cart", "orders"
        ]
        return any(m in text for m in ecommerce_markers)

    def _filter_features_by_domain(self, features: List[Dict[str, Any]], domain: str) -> List[Dict[str, Any]]:
        if domain == 'ecommerce':
            return features
        filtered: List[Dict[str, Any]] = []
        for f in features:
            if self._feature_looks_ecommerce(f):
                continue
            filtered.append(f)
        return filtered
    
    def _generate_fallback_features(self, requirement: RequirementGraph) -> List[Dict[str, Any]]:
        """Generate domain-specific fallback BDD features when LLM fails."""
        
        # Detect domain from requirement
        ac_text = ' '.join([f"{ac.given} {ac.when} {ac.then}" for ac in requirement.acceptanceCriteria])
        requirement_text = f"{requirement.title} {requirement.goal} {ac_text}"
        url = getattr(requirement, 'url', '') or ''
        domain = self.domain_detector.detect_domain(requirement_text, url)
        
        logger.info(f"Generating fallback features for domain: {domain}")
        
        # Get domain-specific context
        domain_context = self.domain_detector.get_domain_context(domain)
        
        features: List[Dict[str, Any]] = []
        def scen(name: str, steps: List[str]) -> Dict[str, Any]:
            return {"type": "scenario", "name": name, "steps": steps}

        if domain in ('generic', 'search_engine'):
            # Generic application testing with Scenario Outlines
            features.append({
                "feature_name": "Google Home Page" if domain == 'search_engine' else "Page Navigation",
                "actor": "user",
                "goal": "load and use the home page" if domain == 'search_engine' else "navigate through the website",
                "benefit": "access different sections",
                "scenarios": [
                    {
                        "type": "scenario_outline", 
                        "name": "Home page loads with key UI elements" if domain == 'search_engine' else "Navigate to different sections", 
                        "steps": [
                            "Given I am on the Google home page" if domain == 'search_engine' else "Given I am on the homepage",
                            "Then I should see the Google logo" if domain == 'search_engine' else "Then the page content should load completely",
                            "And I should see a single search input box" if domain == 'search_engine' else "",
                            "And I should see a \"Google Search\" button" if domain == 'search_engine' else "",
                            "And I should see an \"I'm Feeling Lucky\" button" if domain == 'search_engine' else ""
                        ], 
                        "examples": []
                    },
                    {
                        "type": "scenario",
                        "name": "Submitting a query with Enter" if domain == 'search_engine' else "Load homepage successfully", 
                        "steps": [
                            "When I type \"kittens\" into the search input" if domain == 'search_engine' else "When the page loads",
                            "And I press Enter" if domain == 'search_engine' else "Then all main elements are visible",
                            "Then I should land on the search results page for \"kittens\"" if domain == 'search_engine' else "And the page is fully interactive"
                        ]
                    }
                ]
            })
            
            if domain == 'search_engine':
                features.extend([
                    {"feature_name": "Basic Web Search", "actor": "user", "goal": "search for information", "benefit": "find relevant content", "scenarios": [
                        {"type": "scenario", "name": "Basic query returns a results page", "steps": [
                            "Given I am on the Google home page",
                            "When I search for \"selenium webdriver\"",
                            "Then I should see a results page with organic results",
                            "And the \"All\" tab should be selected"
                        ]},
                        {"type": "scenario", "name": "Query is case-insensitive", "steps": [
                            "Given I am on the Google home page",
                            "When I search for \"Python\"",
                            "Then I should see similar results as searching for \"python\""
                        ]},
                        {"type": "scenario", "name": "Special characters are handled", "steps": [
                            "Given I am on the Google home page",
                            "When I search for \"C++ tutorial\"",
                            "Then I should see results relevant to \"C++ tutorial\""
                        ]}
                    ]},
                    {"feature_name": "Autocomplete & Suggestions", "actor": "user", "goal": "receive query suggestions", "benefit": "type faster", "scenarios": [
                        {"type": "scenario", "name": "Suggestions appear while typing", "steps": [
                            "Given I am on the Google home page",
                            "When I type \"indi\" into the search input",
                            "Then I should see a suggestions list beneath the input"
                        ]},
                        {"type": "scenario", "name": "Dismissing suggestions with Escape", "steps": [
                            "Given suggestions are visible",
                            "When I press Escape",
                            "Then the suggestions list should close"
                        ]}
                    ]},
                    {"feature_name": "Results Page Layout", "actor": "user", "goal": "view SERP", "benefit": "navigate results", "scenarios": [
                        {"type": "scenario", "name": "Search box retains the query", "steps": [
                            "Given I have searched for \"best programming languages\"",
                            "Then the search input should contain \"best programming languages\""
                        ]},
                        {"type": "scenario", "name": "Tabs for verticals are present", "steps": [
                            "Given I have searched for \"best programming languages\"",
                            "Then I should see tabs for \"All\", \"Images\", \"Videos\", and \"News\""
                        ]}
                    ]}
                ])
            
        elif domain == 'ecommerce':
            # E-commerce fallback: provide rich baseline (PLP, PDP, Cart, Coupon, Checkout, Payment)
            features.append({
                "feature_name": "Homepage & Global Navigation",
                "actor": "shopper",
                "goal": "discover products and actions",
                "benefit": "shop efficiently",
                "scenarios": [
                    {"type": "scenario", "name": "Render homepage for a first-time visitor", "steps": [
                        "When I open the homepage",
                        "Then I see the cookie consent banner",
                        "And I see the primary navigation and search"
                    ]},
                    {"type": "scenario_outline", "name": "Navigate to category", "steps": [
                        "Given I am on the homepage",
                        "When I select the \"<category>\" menu item",
                        "Then I land on the \"<expected_page>\" listing page"
                    ], "examples": [
                        {"category": "Women > Tops", "expected_page": "Women Tops"},
                        {"category": "Men > Hoodies", "expected_page": "Men Hoodies"}
                    ]}
                ]
            })

            features.append({
                "feature_name": "Product Listing Page (PLP)",
                "actor": "shopper",
                "goal": "filter and sort products",
                "benefit": "find items quickly",
                "scenarios": [
                    {"type": "scenario_outline", "name": "Apply facet and sort", "steps": [
                        "Given I navigate to the \"<category>\" category",
                        "When I apply facet \"<facet>\" with value \"<value>\"",
                        "And I sort by \"<sortOption>\"",
                        "Then the product grid shows items matching \"<facet>\"=\"<value>\"",
                        "And results are ordered by \"<sortOption>\""
                    ], "examples": [
                        {"category": "Women > Tops", "facet": "Color", "value": "Black", "sortOption": "Price: Low to High"},
                        {"category": "Men > Hoodies", "facet": "Size", "value": "M", "sortOption": "Customer Rating"}
                    ]}
                ]
            })

            features.append({
                "feature_name": "Product Detail Page (PDP)",
                "actor": "shopper",
                "goal": "select variant and add to cart",
                "benefit": "purchase desired item",
                "scenarios": [
                    {"type": "scenario_outline", "name": "Select variant and verify availability", "steps": [
                        "Given I open the PDP for \"<baseName>\"",
                        "When I select variant \"<variantAttr>\" = \"<variantValue>\"",
                        "Then the availability message is \"<expectedAvailability>\""
                    ], "examples": [
                        {"baseName": "Push It Messenger Bag", "variantAttr": "Color", "variantValue": "Blue", "expectedAvailability": "In stock"},
                        {"baseName": "Fusion Backpack", "variantAttr": "Color", "variantValue": "Orange", "expectedAvailability": "Out of stock"}
                    ]},
                    {"type": "scenario", "name": "Add to cart from PDP", "steps": [
                        "Given I am on the PDP for \"Fusion Backpack\"",
                        "When I add quantity 1 to the cart",
                        "Then the mini-cart shows item count increased"
                    ]}
                ]
            })

            features.append({
                "feature_name": "Cart",
                "actor": "shopper",
                "goal": "review and update cart",
                "benefit": "proceed to checkout",
                "scenarios": [
                    {"type": "scenario", "name": "Open mini-cart and view contents", "steps": [
                        "Given I have added an item to the cart",
                        "When I open the mini-cart",
                        "Then I see line items and subtotal"
                    ]},
                    {"type": "scenario_outline", "name": "Update quantity in cart", "steps": [
                        "Given my cart contains SKU \"<sku>\"",
                        "When I update quantity to <qty>",
                        "Then the line subtotal reflects the change"
                    ], "examples": [
                        {"sku": "24-MB02", "qty": 2},
                        {"sku": "24-MB02", "qty": 3}
                    ]},
                    {"type": "scenario", "name": "Apply coupon code", "steps": [
                        "Given my cart contains eligible items",
                        "When I apply coupon \"WELCOME10\"",
                        "Then totals reflect the coupon"
                    ]}
                ]
            })

            features.append({
                "feature_name": "Checkout",
                "actor": "guest",
                "goal": "place order as guest",
                "benefit": "complete purchase",
                "scenarios": [
                    {"type": "scenario_outline", "name": "Guest checkout with shipping and payment", "steps": [
                        "Given I proceed to checkout as \"guest\"",
                        "And I provide shipping address: <shipName>, <shipPostal>",
                        "When I select shipping method \"<shippingMethod>\"",
                        "And I select payment method \"<paymentMethod>\"",
                        "And I place the order",
                        "Then the order is created with status \"Placed\""
                    ], "examples": [
                        {"shipName": "Guest User", "shipPostal": "78701", "shippingMethod": "Standard", "paymentMethod": "Card"},
                        {"shipName": "Guest User", "shipPostal": "600006", "shippingMethod": "Express", "paymentMethod": "Wallet"}
                    ]}
                ]
            })
            
        else:
            # For other domains (banking, healthcare), use generic fallback
            features.append({
                "feature_name": "Core Functionality",
                "actor": "user",
                "goal": "use the application effectively", 
                "benefit": "accomplish tasks successfully",
                "background": "Given the application is available",
                "scenarios": [
                    scen("Load main page", [
                        "When I navigate to the main page",
                        "Then I see the application interface",
                        "And all essential elements are visible"
                    ]),
                    scen("Basic navigation works", [
                        "When I navigate through the application",
                        "Then I can access different sections",
                        "And the navigation is responsive"
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
                scenario_name = scenario.get("name", f"Scenario {i+1}")
                scenario_type = scenario.get("type", "scenario")
                steps = scenario.get("steps", [])

                def classify(name: str) -> tuple[str, str]:
                    lower = name.lower()
                    if any(w in lower for w in ["invalid", "error", "fail", "expired", "decline", "unauthorized", "empty", "missing", "format"]):
                        return ("negative", "P1")
                    if any(w in lower for w in ["edge", "boundary", "maximum", "minimum", "limit", "timeout", "retry"]):
                        return ("edge", "P2")
                    return ("positive", "P0")

                if scenario_type == "scenario_outline" and isinstance(scenario.get("examples"), list) and scenario["examples"]:
                    for ex_idx, example in enumerate(scenario["examples"], 1):
                        # Replace <param> with values in raw steps
                        replaced_steps: List[str] = []
                        for line in steps:
                            new_line = line
                            if isinstance(example, dict):
                                for k, v in example.items():
                                    new_line = new_line.replace(f"<{k}>", str(v))
                            replaced_steps.append(new_line)
                        ttype, prio = classify(scenario_name)
                        # Build parsed step actions
                        test_steps = []
                        for s in replaced_steps:
                            action = self._parse_step_to_action(s)
                            test_steps.append(TestStep(action=action["action"], params=action["params"]))
                        self.test_counter += 1
                        tags = self._sanitize_tags([prio, ttype, "scenario", feature_name.lower().replace(" ", "_")])
                        test_cases.append(TestCase(
                            id=f"TC-{feature_name.replace(' ', '').replace('&', '').upper()[:8]}-{self.test_counter:03d}",
                            title=f"{feature_name}: {scenario_name} [{ex_idx}]",
                            priority=prio,
                            type=ttype,
                            traceTo=["AC-1"],
                            preconditions=[feature.get("background", "Given the system is ready")],
                            steps=test_steps,
                            data={"raw_steps": replaced_steps, "scenario_name": f"{scenario_name} [{ex_idx}]"},
                            expected=[f"Scenario '{scenario_name} [{ex_idx}]' completes successfully"],
                            tags=tags
                        ))
                else:
                    ttype, prio = classify(scenario_name)
                    # Build parsed step actions
                    test_steps = []
                    for s in steps:
                        action = self._parse_step_to_action(s)
                        test_steps.append(TestStep(action=action["action"], params=action["params"]))
                    self.test_counter += 1
                    tags = self._sanitize_tags([prio, ttype, scenario_type, feature_name.lower().replace(" ", "_")])
                    test_cases.append(TestCase(
                        id=f"TC-{feature_name.replace(' ', '').replace('&', '').upper()[:8]}-{self.test_counter:03d}",
                        title=f"{feature_name}: {scenario_name}",
                        priority=prio,
                        type=ttype,
                        traceTo=["AC-1"],
                        preconditions=[feature.get("background", "Given the system is ready")],
                        steps=test_steps,
                        data={"raw_steps": steps, "scenario_name": scenario_name},
                        expected=[f"Scenario '{scenario_name}' completes successfully"],
                        tags=tags
                    ))
        
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
        domain_hint = (req.domain or "").lower()
        if domain_hint == "ecommerce" or any(k in (req.title or "").lower() for k in ["ecommerce", "cart", "checkout", "order"]):
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
        
        title_seen = set()
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
                        elif isinstance(v, list):
                            # Convert lists to tuples of strings for hashing
                            flat_data[k] = tuple(str(item) for item in v)
                        else:
                            flat_data[k] = v
                    data_signature = tuple(sorted(flat_data.items()))
                except Exception:
                    # Fallback: use string representation
                    data_signature = str(case.data)
            
            signature = (
                case.type,
                (tuple(step.action for step in case.steps), case.data.get("scenario_name") if isinstance(case.data, dict) else None),
                data_signature
            )
            simple_title = case.title.strip().lower()
            
            if signature not in seen and simple_title not in title_seen:
                seen.add(signature)
                title_seen.add(simple_title)
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
