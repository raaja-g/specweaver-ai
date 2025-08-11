"""
Locator Repository Manager - Runtime generation and management of UI element locators
"""
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging
import re
from urllib.parse import urlparse

from .llm_orchestrator import LLMOrchestrator
from .self_healing import SelfHealingEngine

logger = logging.getLogger(__name__)


class LocatorManager:
    """
    Manages UI element locators with runtime generation and self-healing capabilities
    """
    
    def __init__(self, 
                 orchestrator: Optional[LLMOrchestrator] = None,
                 self_healing: Optional[SelfHealingEngine] = None):
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.self_healing = self_healing or SelfHealingEngine(orchestrator)
        self.locator_cache = {}
        
    def generate_locator_repository(self, 
                                  target_url: str,
                                  page_name: str,
                                  elements: List[str],
                                  output_dir: Path,
                                  page_source: Optional[str] = None) -> Path:
        """
        Generate a locator repository for a specific page
        
        Args:
            target_url: URL of the target application page
            page_name: Name identifier for the page (e.g., 'checkout', 'product_catalog')
            elements: List of element names to locate (e.g., ['Add to Cart', 'Quantity Input'])
            output_dir: Directory to save the locator repository
            page_source: Optional HTML source for analysis
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate locators using LLM if page source available
        if page_source:
            locators = self._generate_locators_from_source(page_name, elements, page_source)
        else:
            # Generate heuristic-based locators
            locators = self._generate_heuristic_locators(page_name, elements, target_url)
        
        # Create repository structure
        repository = {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "target_url": target_url,
                "page_name": page_name,
                "version": "1.0.0"
            },
            "pages": {
                page_name: locators
            }
        }
        
        # Save as JSON
        locator_file = output_dir / f"{page_name}_locators.json"
        locator_file.write_text(json.dumps(repository, indent=2))
        
        # Also save as YAML for human readability
        yaml_file = output_dir / f"{page_name}_locators.yml"
        with open(yaml_file, 'w') as f:
            yaml.dump(repository, f, default_flow_style=False, indent=2)
        
        logger.info(f"Generated locator repository: {locator_file}")
        return locator_file
    
    def _generate_locators_from_source(self, 
                                     page_name: str, 
                                     elements: List[str], 
                                     page_source: str) -> Dict[str, Any]:
        """Generate locators by analyzing HTML source with LLM"""
        try:
            # Truncate if too long
            if len(page_source) > 15000:
                page_source = page_source[:15000] + "..."
            
            prompt = f"""
Analyze this HTML page source and generate robust CSS selectors for the following UI elements on the "{page_name}" page:

Elements to locate: {', '.join(elements)}

HTML Source:
{page_source}

For each element, provide:
1. A primary CSS selector (most reliable)
2. A fallback CSS selector (alternative approach)
3. An XPath selector (as backup)
4. Any relevant attributes for identification

Focus on:
- Stable attributes (data-testid, id, name, aria-label)
- Avoid dynamically generated classes/IDs when possible
- Consider text content for buttons/links
- Use structural relationships when needed

Return JSON format:
{{
  "element_name": {{
    "primary": "css selector",
    "fallback": "alternative css selector", 
    "xpath": "xpath selector",
    "attributes": ["attr1", "attr2"],
    "description": "brief description of element location strategy"
  }}
}}
"""
            
            response = self.orchestrator.call(
                prompt=prompt,
                system="You are a web automation expert. Generate robust, maintainable selectors that resist UI changes.",
                task_type="analysis"
            )
            
            try:
                locators = json.loads(response.content)
                
                # Validate and clean up the response
                cleaned_locators = {}
                for element in elements:
                    element_key = element.lower().replace(' ', '_').replace('-', '_')
                    
                    # Look for the element in various forms
                    found_data = None
                    for key, data in locators.items():
                        if (key.lower() == element.lower() or 
                            key.lower() == element_key or
                            element.lower() in key.lower()):
                            found_data = data
                            break
                    
                    if found_data and isinstance(found_data, dict):
                        cleaned_locators[element_key] = {
                            "primary": found_data.get("primary", f"[aria-label*='{element}']"),
                            "fallback": found_data.get("fallback", f"*:contains('{element}')"),
                            "xpath": found_data.get("xpath", f"//*[contains(text(), '{element}')]"),
                            "attributes": found_data.get("attributes", []),
                            "description": found_data.get("description", f"Locators for {element}")
                        }
                    else:
                        # Fallback for missing elements
                        cleaned_locators[element_key] = self._generate_fallback_locator(element)
                
                return cleaned_locators
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM response, using heuristic locators")
                return self._generate_heuristic_locators(page_name, elements)
                
        except Exception as e:
            logger.exception("Failed to generate locators from source")
            return self._generate_heuristic_locators(page_name, elements)
    
    def _generate_heuristic_locators(self, 
                                   page_name: str, 
                                   elements: List[str], 
                                   target_url: Optional[str] = None) -> Dict[str, Any]:
        """Generate locators using heuristic patterns"""
        locators = {}
        
        for element in elements:
            element_key = element.lower().replace(' ', '_').replace('-', '_')
            locators[element_key] = self._generate_fallback_locator(element)
        
        return locators
    
    def _generate_fallback_locator(self, element_name: str) -> Dict[str, Any]:
        """Generate fallback locator strategies for an element"""
        element_lower = element_name.lower().replace(' ', '_').replace('-', '_')
        
        # Common patterns based on element type/name
        patterns = {
            "primary": self._get_primary_pattern(element_name),
            "fallback": self._get_fallback_pattern(element_name),
            "xpath": self._get_xpath_pattern(element_name),
            "attributes": self._get_common_attributes(element_name),
            "description": f"Heuristic locators for {element_name}"
        }
        
        return patterns
    
    def _get_primary_pattern(self, element_name: str) -> str:
        """Get primary selector pattern based on element name"""
        element_lower = element_name.lower().replace(' ', '_')
        
        # Button patterns
        if any(word in element_name.lower() for word in ['button', 'btn', 'click', 'submit', 'add', 'remove']):
            return f"button[data-testid='{element_lower}'], input[type='button'][data-testid='{element_lower}']"
        
        # Input patterns
        elif any(word in element_name.lower() for word in ['input', 'field', 'text', 'email', 'password']):
            return f"input[data-testid='{element_lower}'], input[name*='{element_lower}']"
        
        # Link patterns
        elif any(word in element_name.lower() for word in ['link', 'nav', 'menu']):
            return f"a[data-testid='{element_lower}'], a[href*='{element_lower}']"
        
        # Generic pattern
        else:
            return f"[data-testid='{element_lower}'], #{element_lower}"
    
    def _get_fallback_pattern(self, element_name: str) -> str:
        """Get fallback selector pattern"""
        return f"[aria-label*='{element_name}'], [title*='{element_name}'], *:contains('{element_name}')"
    
    def _get_xpath_pattern(self, element_name: str) -> str:
        """Get XPath selector pattern"""
        return f"//*[@data-testid='{element_name.lower().replace(' ', '_')}'] | //*[contains(text(), '{element_name}')]"
    
    def _get_common_attributes(self, element_name: str) -> List[str]:
        """Get common attributes to look for"""
        base_attrs = ["data-testid", "id", "name", "class"]
        
        if any(word in element_name.lower() for word in ['button', 'click', 'submit']):
            base_attrs.extend(["type", "onclick", "aria-label"])
        elif any(word in element_name.lower() for word in ['input', 'field']):
            base_attrs.extend(["type", "placeholder", "aria-label"])
        elif any(word in element_name.lower() for word in ['link', 'nav']):
            base_attrs.extend(["href", "role"])
        
        return base_attrs
    
    def update_locator_repository(self, 
                                locator_file: Path, 
                                page_name: str, 
                                element_updates: Dict[str, str]) -> bool:
        """Update existing locator repository with new/changed selectors"""
        try:
            if not locator_file.exists():
                logger.error(f"Locator file not found: {locator_file}")
                return False
            
            # Read existing repository
            if locator_file.suffix == '.json':
                repository = json.loads(locator_file.read_text())
            elif locator_file.suffix in ['.yml', '.yaml']:
                with open(locator_file, 'r') as f:
                    repository = yaml.safe_load(f)
            else:
                logger.error(f"Unsupported file format: {locator_file}")
                return False
            
            # Update locators
            if "pages" not in repository:
                repository["pages"] = {}
            
            if page_name not in repository["pages"]:
                repository["pages"][page_name] = {}
            
            for element_name, selector in element_updates.items():
                if isinstance(repository["pages"][page_name].get(element_name), dict):
                    # Update primary selector in complex structure
                    repository["pages"][page_name][element_name]["primary"] = selector
                else:
                    # Simple string selector
                    repository["pages"][page_name][element_name] = selector
            
            # Update metadata
            repository["metadata"]["updated_at"] = datetime.utcnow().isoformat()
            
            # Write back
            if locator_file.suffix == '.json':
                locator_file.write_text(json.dumps(repository, indent=2))
            else:
                with open(locator_file, 'w') as f:
                    yaml.dump(repository, f, default_flow_style=False, indent=2)
            
            logger.info(f"Updated locator repository: {locator_file}")
            return True
            
        except Exception as e:
            logger.exception(f"Failed to update locator repository: {e}")
            return False
    
    def get_locator(self, 
                   locator_file: Path, 
                   page_name: str, 
                   element_name: str) -> Optional[Dict[str, str]]:
        """Get locator information for a specific element"""
        try:
            if locator_file.suffix == '.json':
                repository = json.loads(locator_file.read_text())
            elif locator_file.suffix in ['.yml', '.yaml']:
                with open(locator_file, 'r') as f:
                    repository = yaml.safe_load(f)
            else:
                return None
            
            page_locators = repository.get("pages", {}).get(page_name, {})
            element_key = element_name.lower().replace(' ', '_').replace('-', '_')
            
            locator_data = page_locators.get(element_key)
            if isinstance(locator_data, dict):
                return locator_data
            elif isinstance(locator_data, str):
                return {"primary": locator_data}
            else:
                return None
                
        except Exception as e:
            logger.exception(f"Failed to get locator: {e}")
            return None
    
    def validate_locators(self, 
                         locator_file: Path, 
                         page_source: Optional[str] = None) -> Dict[str, Any]:
        """Validate locators against page source (if available)"""
        validation_results = {
            "valid_locators": [],
            "invalid_locators": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            if locator_file.suffix == '.json':
                repository = json.loads(locator_file.read_text())
            elif locator_file.suffix in ['.yml', '.yaml']:
                with open(locator_file, 'r') as f:
                    repository = yaml.safe_load(f)
            else:
                validation_results["warnings"].append("Unsupported file format")
                return validation_results
            
            # Basic structural validation
            if "pages" not in repository:
                validation_results["warnings"].append("No pages section found")
                return validation_results
            
            for page_name, page_locators in repository["pages"].items():
                for element_name, locator_data in page_locators.items():
                    if isinstance(locator_data, dict):
                        primary = locator_data.get("primary")
                        if primary:
                            validation_results["valid_locators"].append({
                                "page": page_name,
                                "element": element_name,
                                "selector": primary
                            })
                    elif isinstance(locator_data, str):
                        validation_results["valid_locators"].append({
                            "page": page_name,
                            "element": element_name,
                            "selector": locator_data
                        })
            
            # TODO: If page_source provided, validate selectors actually exist
            # This would require a HTML parser like BeautifulSoup
            
        except Exception as e:
            validation_results["warnings"].append(f"Validation error: {str(e)}")
        
        return validation_results
