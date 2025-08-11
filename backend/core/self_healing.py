"""
Self-Healing Engine for UI Test Selectors
Automatically suggests and applies selector updates when elements are not found
"""
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging
from dataclasses import dataclass
from enum import Enum

from .llm_orchestrator import LLMOrchestrator

logger = logging.getLogger(__name__)


class SelectorType(Enum):
    ID = "id"
    CLASS = "class"
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    DATA_TESTID = "data-testid"


@dataclass
class SelectorSuggestion:
    original_selector: str
    suggested_selector: str
    selector_type: SelectorType
    confidence: float
    reason: str
    context: Optional[str] = None


@dataclass
class SelfHealingResult:
    element_name: str
    original_selector: str
    suggestions: List[SelectorSuggestion]
    auto_applied: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class SelfHealingEngine:
    """
    Self-healing engine that analyzes failed selectors and suggests alternatives
    """
    
    def __init__(self, orchestrator: Optional[LLMOrchestrator] = None):
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.suggestions_cache = {}
        self.auto_apply_threshold = 0.8  # Auto-apply suggestions with >80% confidence
        
    def analyze_failed_selector(self, 
                               element_name: str,
                               failed_selector: str,
                               page_source: Optional[str] = None,
                               screenshot_path: Optional[str] = None) -> SelfHealingResult:
        """
        Analyze a failed selector and suggest alternatives
        """
        suggestions = []
        
        # Rule-based suggestions
        rule_based = self._generate_rule_based_suggestions(failed_selector)
        suggestions.extend(rule_based)
        
        # LLM-based suggestions if page source is available
        if page_source:
            llm_suggestions = self._generate_llm_suggestions(
                element_name, failed_selector, page_source
            )
            suggestions.extend(llm_suggestions)
        
        # Pattern-based suggestions
        pattern_suggestions = self._generate_pattern_suggestions(
            element_name, failed_selector
        )
        suggestions.extend(pattern_suggestions)
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        
        # Auto-apply if high confidence
        auto_applied = None
        if suggestions and suggestions[0].confidence >= self.auto_apply_threshold:
            auto_applied = suggestions[0].suggested_selector
            logger.info(f"Auto-applying high confidence suggestion: {auto_applied}")
        
        return SelfHealingResult(
            element_name=element_name,
            original_selector=failed_selector,
            suggestions=suggestions[:5],  # Top 5 suggestions
            auto_applied=auto_applied
        )
    
    def _generate_rule_based_suggestions(self, selector: str) -> List[SelectorSuggestion]:
        """Generate suggestions based on common selector patterns"""
        suggestions = []
        
        # ID selector variations
        if selector.startswith('#'):
            base_id = selector[1:]
            variations = [
                f"[id='{base_id}']",
                f"[id*='{base_id}']",
                f"[id^='{base_id}']",
                f"[id$='{base_id}']"
            ]
            for var in variations:
                suggestions.append(SelectorSuggestion(
                    original_selector=selector,
                    suggested_selector=var,
                    selector_type=SelectorType.CSS,
                    confidence=0.7,
                    reason=f"Alternative ID selector syntax"
                ))
        
        # Class selector variations
        elif selector.startswith('.'):
            base_class = selector[1:]
            variations = [
                f"[class*='{base_class}']",
                f"[class^='{base_class}']",
                f"[class$='{base_class}']"
            ]
            for var in variations:
                suggestions.append(SelectorSuggestion(
                    original_selector=selector,
                    suggested_selector=var,
                    selector_type=SelectorType.CSS,
                    confidence=0.6,
                    reason=f"Partial class match"
                ))
        
        # CSS selector to XPath
        if not selector.startswith('//'):
            xpath = self._css_to_xpath_approximation(selector)
            if xpath:
                suggestions.append(SelectorSuggestion(
                    original_selector=selector,
                    suggested_selector=xpath,
                    selector_type=SelectorType.XPATH,
                    confidence=0.5,
                    reason="CSS to XPath conversion"
                ))
        
        return suggestions
    
    def _generate_llm_suggestions(self, 
                                element_name: str, 
                                failed_selector: str, 
                                page_source: str) -> List[SelectorSuggestion]:
        """Use LLM to analyze page source and suggest selectors"""
        try:
            # Truncate page source if too long
            if len(page_source) > 10000:
                page_source = page_source[:10000] + "..."
            
            prompt = f"""
Analyze this HTML page source and suggest alternative selectors for the element "{element_name}".

Original failing selector: {failed_selector}

Page source excerpt:
{page_source}

Suggest 3 alternative selectors that might work for finding the "{element_name}" element.
Consider:
1. The element might have dynamic IDs or classes
2. Look for stable attributes like data-testid, aria-label, or text content
3. Consider parent-child relationships
4. Prefer specific but resilient selectors

Return JSON format:
{{
  "suggestions": [
    {{
      "selector": "suggested selector",
      "type": "css|xpath|text",
      "confidence": 0.0-1.0,
      "reason": "why this selector should work"
    }}
  ]
}}
"""
            
            response = self.orchestrator.call(
                prompt=prompt,
                system="You are a web automation expert specializing in robust selector strategies.",
                task_type="analysis"
            )
            
            # Parse LLM response
            try:
                data = json.loads(response.content)
                suggestions = []
                for sugg in data.get("suggestions", []):
                    selector_type = SelectorType.CSS
                    if sugg["type"] == "xpath":
                        selector_type = SelectorType.XPATH
                    elif sugg["type"] == "text":
                        selector_type = SelectorType.TEXT
                    
                    suggestions.append(SelectorSuggestion(
                        original_selector=failed_selector,
                        suggested_selector=sugg["selector"],
                        selector_type=selector_type,
                        confidence=float(sugg["confidence"]),
                        reason=sugg["reason"]
                    ))
                return suggestions
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response for selector suggestions")
                return []
                
        except Exception as e:
            logger.exception("Failed to generate LLM suggestions")
            return []
    
    def _generate_pattern_suggestions(self, 
                                    element_name: str, 
                                    failed_selector: str) -> List[SelectorSuggestion]:
        """Generate suggestions based on common element naming patterns"""
        suggestions = []
        
        # Common patterns based on element name
        element_lower = element_name.lower().replace(' ', '_')
        patterns = [
            f"[data-testid='{element_lower}']",
            f"[data-testid*='{element_lower}']",
            f"[aria-label*='{element_name}']",
            f"[title*='{element_name}']",
            f"[placeholder*='{element_name}']",
            f"button:contains('{element_name}')",
            f"input[name*='{element_lower}']",
            f"#{element_lower}",
            f".{element_lower}",
        ]
        
        for pattern in patterns:
            suggestions.append(SelectorSuggestion(
                original_selector=failed_selector,
                suggested_selector=pattern,
                selector_type=SelectorType.CSS,
                confidence=0.4,
                reason=f"Common pattern for '{element_name}' elements"
            ))
        
        return suggestions
    
    def _css_to_xpath_approximation(self, css_selector: str) -> Optional[str]:
        """Convert simple CSS selectors to XPath (basic implementation)"""
        try:
            # Very basic CSS to XPath conversion
            if css_selector.startswith('#'):
                return f"//*[@id='{css_selector[1:]}']"
            elif css_selector.startswith('.'):
                return f"//*[contains(@class, '{css_selector[1:]}')]"
            elif '[' in css_selector and ']' in css_selector:
                # Basic attribute selector
                match = re.match(r'(\w+)?\[(\w+)([*^$]?)=?["\']?([^"\']*)["\']?\]', css_selector)
                if match:
                    tag, attr, op, value = match.groups()
                    tag = tag or '*'
                    if op == '*':
                        return f"//{tag}[contains(@{attr}, '{value}')]"
                    elif op == '^':
                        return f"//{tag}[starts-with(@{attr}, '{value}')]"
                    else:
                        return f"//{tag}[@{attr}='{value}']"
            return None
        except Exception:
            return None
    
    def save_suggestions(self, result: SelfHealingResult, output_dir: Path) -> Path:
        """Save self-healing suggestions to file"""
        output_dir.mkdir(parents=True, exist_ok=True)
        suggestions_file = output_dir / f"self_heal_suggestions_{result.timestamp.replace(':', '-')}.json"
        
        # Convert to serializable format
        data = {
            "element_name": result.element_name,
            "original_selector": result.original_selector,
            "timestamp": result.timestamp,
            "auto_applied": result.auto_applied,
            "suggestions": [
                {
                    "selector": s.suggested_selector,
                    "type": s.selector_type.value,
                    "confidence": s.confidence,
                    "reason": s.reason,
                    "context": s.context
                }
                for s in result.suggestions
            ]
        }
        
        suggestions_file.write_text(json.dumps(data, indent=2))
        logger.info(f"Saved self-healing suggestions to {suggestions_file}")
        return suggestions_file
    
    def apply_suggestion(self, 
                        suggestion: SelectorSuggestion, 
                        locator_file: Path) -> bool:
        """Apply a suggestion by updating the locator repository"""
        try:
            if not locator_file.exists():
                logger.warning(f"Locator file not found: {locator_file}")
                return False
            
            # Read current locators
            content = locator_file.read_text()
            if locator_file.suffix == '.json':
                locators = json.loads(content)
            else:
                # YAML support would go here
                logger.warning("YAML locator files not yet supported for auto-update")
                return False
            
            # Find and update the selector
            updated = False
            for page_name, page_locators in locators.items():
                if isinstance(page_locators, dict):
                    for element_name, selector in page_locators.items():
                        if selector == suggestion.original_selector:
                            page_locators[element_name] = suggestion.suggested_selector
                            updated = True
                            logger.info(f"Updated selector for {element_name}: {selector} -> {suggestion.suggested_selector}")
            
            if updated:
                # Write back to file
                locator_file.write_text(json.dumps(locators, indent=2))
                return True
            else:
                logger.warning(f"Original selector not found in {locator_file}")
                return False
                
        except Exception as e:
            logger.exception(f"Failed to apply suggestion: {e}")
            return False
