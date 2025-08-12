"""
URL Scraper - Analyzes actual website structure using Playwright
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, Page
from playwright.sync_api import sync_playwright
import json
import re

logger = logging.getLogger(__name__)

class URLScraper:
    """Scrapes website structure using Playwright to discover actual functionality"""
    
    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape website and analyze structure
        
        Args:
            url: Website URL to analyze
            
        Returns:
            Dictionary containing discovered elements and functionality
        """
        try:
            logger.info(f"Starting website analysis for: {url}")
            
            # Navigate to the page
            await self.page.goto(url, wait_until="networkidle", timeout=self.timeout)
            
            # Wait for page to fully load
            await asyncio.sleep(2)
            
            # Analyze page structure
            analysis = {
                "url": url,
                "title": await self.page.title(),
                "domain": self._extract_domain(url),
                "elements": await self._discover_elements(),
                "forms": await self._discover_forms(),
                "navigation": await self._discover_navigation(),
                "interactions": await self._discover_interactions(),
                "content": await self._discover_content(),
                "accessibility": await self._discover_accessibility(),
                "performance": await self._analyze_performance()
            }
            
            logger.info(f"Website analysis completed. Found {len(analysis['elements'])} interactive elements")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to scrape website {url}: {e}")
            return self._create_fallback_analysis(url)
    
    async def _discover_elements(self) -> List[Dict[str, Any]]:
        """Discover all interactive elements on the page"""
        elements = []
        
        # Find all clickable elements
        clickable_selectors = [
            "button", "a[href]", "input[type='submit']", "input[type='button']",
            "[role='button']", "[onclick]", "[tabindex]"
        ]
        
        for selector in clickable_selectors:
            try:
                found_elements = await self.page.query_selector_all(selector)
                for elem in found_elements:
                    element_info = await self._extract_element_info(elem, selector)
                    if element_info:
                        elements.append(element_info)
            except Exception as e:
                logger.warning(f"Failed to analyze selector {selector}: {e}")
        
        # Find form inputs
        input_selectors = [
            "input", "textarea", "select", "[contenteditable='true']"
        ]
        
        for selector in input_selectors:
            try:
                found_elements = await self.page.query_selector_all(selector)
                for elem in found_elements:
                    element_info = await self._extract_element_info(elem, selector)
                    if element_info:
                        elements.append(element_info)
            except Exception as e:
                logger.warning(f"Failed to analyze input selector {selector}: {e}")
        
        return elements
    
    async def _extract_element_info(self, element, selector_type: str) -> Optional[Dict[str, Any]]:
        """Extract detailed information about an element"""
        try:
            # Get element properties
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            element_type = await element.evaluate("el => el.type || ''")
            text_content = await element.evaluate("el => el.textContent?.trim() || ''")
            placeholder = await element.evaluate("el => el.placeholder || ''")
            aria_label = await element.evaluate("el => el.getAttribute('aria-label') || ''")
            role = await element.evaluate("el => el.getAttribute('role') || ''")
            
            # Get element position and size
            bounding_box = await element.bounding_box()
            
            # Determine element category
            category = self._categorize_element(tag_name, element_type, role)
            
            # Generate test-friendly name
            test_name = self._generate_test_name(text_content, placeholder, aria_label, tag_name)
            
            # Create unique selector
            selector = await self._generate_unique_selector(element)
            
            element_info = {
                "tag": tag_name,
                "type": element_type,
                "category": category,
                "text": text_content,
                "placeholder": placeholder,
                "aria_label": aria_label,
                "role": role,
                "test_name": test_name,
                "selector": selector,
                "position": {
                    "x": bounding_box["x"] if bounding_box else 0,
                    "y": bounding_box["y"] if bounding_box else 0,
                    "width": bounding_box["width"] if bounding_box else 0,
                    "height": bounding_box["height"] if bounding_box else 0
                },
                "interactive": self._is_interactive(tag_name, element_type, role),
                "selector_type": selector_type
            }
            
            return element_info
            
        except Exception as e:
            logger.warning(f"Failed to extract element info: {e}")
            return None
    
    def _categorize_element(self, tag: str, element_type: str, role: str) -> str:
        """Categorize element based on its properties"""
        if tag == "button" or role == "button":
            return "button"
        elif tag == "a" or role == "link":
            return "link"
        elif tag == "input":
            if element_type in ["text", "email", "password", "search"]:
                return "text_input"
            elif element_type in ["submit", "button"]:
                return "button"
            elif element_type in ["checkbox", "radio"]:
                return "selection"
            else:
                return "input"
        elif tag == "textarea":
            return "text_area"
        elif tag == "select":
            return "dropdown"
        elif tag == "form":
            return "form"
        else:
            return "other"
    
    def _generate_test_name(self, text: str, placeholder: str, aria_label: str, tag: str) -> str:
        """Generate a test-friendly name for the element"""
        if text:
            return text[:50]  # Limit length
        elif placeholder:
            return f"{placeholder} input"
        elif aria_label:
            return aria_label[:50]
        else:
            return f"{tag} element"
    
    async def _generate_unique_selector(self, element) -> str:
        """Generate a unique CSS selector for the element"""
        try:
            # Try to get a unique ID first
            element_id = await element.evaluate("el => el.id")
            if element_id:
                return f"#{element_id}"
            
            # Try to get a unique class combination
            classes = await element.evaluate("el => Array.from(el.classList).join('.')")
            if classes:
                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                return f"{tag_name}.{classes}"
            
            # Fallback to position-based selector
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            return f"{tag_name}:nth-child(n)"
            
        except Exception as e:
            logger.warning(f"Failed to generate selector: {e}")
            return "element"
    
    def _is_interactive(self, tag: str, element_type: str, role: str) -> bool:
        """Determine if element is interactive"""
        interactive_tags = ["button", "a", "input", "textarea", "select"]
        interactive_types = ["button", "submit", "checkbox", "radio"]
        interactive_roles = ["button", "link", "tab", "menuitem"]
        
        return (tag in interactive_tags or 
                element_type in interactive_types or 
                role in interactive_roles)
    
    async def _discover_forms(self) -> List[Dict[str, Any]]:
        """Discover all forms and their fields"""
        forms = []
        
        try:
            form_elements = await self.page.query_selector_all("form")
            
            for form in form_elements:
                form_info = {
                    "action": await form.evaluate("el => el.action || ''"),
                    "method": await form.evaluate("el => el.method || 'get'"),
                    "fields": await self._discover_form_fields(form),
                    "submit_button": await self._find_submit_button(form)
                }
                forms.append(form_info)
                
        except Exception as e:
            logger.warning(f"Failed to discover forms: {e}")
        
        return forms
    
    async def _discover_form_fields(self, form) -> List[Dict[str, Any]]:
        """Discover all fields within a form"""
        fields = []
        
        try:
            field_elements = await form.query_selector_all("input, textarea, select")
            
            for field in field_elements:
                field_info = await self._extract_element_info(field, "form_field")
                if field_info:
                    fields.append(field_info)
                    
        except Exception as e:
            logger.warning(f"Failed to discover form fields: {e}")
        
        return fields
    
    async def _find_submit_button(self, form) -> Optional[Dict[str, Any]]:
        """Find the submit button for a form"""
        try:
            submit_button = await form.query_selector("input[type='submit'], button[type='submit'], button:not([type])")
            if submit_button:
                return await self._extract_element_info(submit_button, "submit_button")
        except Exception as e:
            logger.warning(f"Failed to find submit button: {e}")
        
        return None
    
    async def _discover_navigation(self) -> Dict[str, Any]:
        """Discover navigation structure"""
        navigation = {
            "main_menu": [],
            "breadcrumbs": [],
            "pagination": [],
            "tabs": []
        }
        
        try:
            # Main navigation menu
            nav_elements = await self.page.query_selector_all("nav, [role='navigation'], .nav, .navigation, .menu")
            for nav in nav_elements:
                links = await nav.query_selector_all("a")
                for link in links:
                    link_info = await self._extract_element_info(link, "navigation")
                    if link_info:
                        navigation["main_menu"].append(link_info)
            
            # Breadcrumbs
            breadcrumb_elements = await self.page.query_selector_all("[role='breadcrumb'], .breadcrumb, .breadcrumbs")
            for breadcrumb in breadcrumb_elements:
                links = await breadcrumb.query_selector_all("a")
                for link in links:
                    link_info = await self._extract_element_info(link, "breadcrumb")
                    if link_info:
                        navigation["breadcrumbs"].append(link_info)
            
            # Pagination
            pagination_elements = await self.page.query_selector_all(".pagination, .pager, [role='navigation']")
            for pagination in pagination_elements:
                links = await pagination.query_selector_all("a")
                for link in links:
                    link_info = await self._extract_element_info(link, "pagination")
                    if link_info:
                        navigation["pagination"].append(link_info)
            
            # Tabs
            tab_elements = await self.page.query_selector_all("[role='tab'], .tab, .tabs")
            for tab in tab_elements:
                tab_info = await self._extract_element_info(tab, "tab")
                if tab_info:
                    navigation["tabs"].append(tab_info)
                    
        except Exception as e:
            logger.warning(f"Failed to discover navigation: {e}")
        
        return navigation
    
    async def _discover_interactions(self) -> List[Dict[str, Any]]:
        """Discover interactive behaviors and events"""
        interactions = []
        
        try:
            # Look for JavaScript event handlers
            elements_with_events = await self.page.query_selector_all("[onclick], [onchange], [onsubmit], [onload]")
            
            for element in elements_with_events:
                event_info = await self._extract_element_info(element, "interactive")
                if event_info:
                    # Extract event type
                    onclick = await element.evaluate("el => el.onclick ? 'onclick' : ''")
                    onchange = await element.evaluate("el => el.onchange ? 'onchange' : ''")
                    onsubmit = await element.evaluate("el => el.onsubmit ? 'onsubmit' : ''")
                    
                    event_info["events"] = [e for e in [onclick, onchange, onsubmit] if e]
                    interactions.append(event_info)
                    
        except Exception as e:
            logger.warning(f"Failed to discover interactions: {e}")
        
        return interactions
    
    async def _discover_content(self) -> Dict[str, Any]:
        """Discover page content structure"""
        content = {
            "headings": [],
            "paragraphs": [],
            "lists": [],
            "images": [],
            "tables": []
        }
        
        try:
            # Headings
            heading_elements = await self.page.query_selector_all("h1, h2, h3, h4, h5, h6")
            for heading in heading_elements:
                text = await heading.evaluate("el => el.textContent?.trim() || ''")
                level = await heading.evaluate("el => parseInt(el.tagName.charAt(1))")
                if text:
                    content["headings"].append({"text": text, "level": level})
            
            # Images
            image_elements = await self.page.query_selector_all("img")
            for img in image_elements:
                src = await img.evaluate("el => el.src || ''")
                alt = await img.evaluate("el => el.alt || ''")
                if src:
                    content["images"].append({"src": src, "alt": alt})
                    
        except Exception as e:
            logger.warning(f"Failed to discover content: {e}")
        
        return content
    
    async def _discover_accessibility(self) -> Dict[str, Any]:
        """Discover accessibility features"""
        accessibility = {
            "aria_labels": [],
            "roles": [],
            "landmarks": []
        }
        
        try:
            # ARIA labels
            aria_elements = await self.page.query_selector_all("[aria-label], [aria-labelledby]")
            for element in aria_elements:
                aria_label = await element.evaluate("el => el.getAttribute('aria-label') || ''")
                aria_labelledby = await element.evaluate("el => el.getAttribute('aria-labelledby') || ''")
                if aria_label or aria_labelledby:
                    accessibility["aria_labels"].append({
                        "aria_label": aria_label,
                        "aria_labelledby": aria_labelledby
                    })
            
            # ARIA roles
            role_elements = await self.page.query_selector_all("[role]")
            for element in role_elements:
                role = await element.evaluate("el => el.getAttribute('role') || ''")
                if role:
                    accessibility["roles"].append(role)
                    
        except Exception as e:
            logger.warning(f"Failed to discover accessibility: {e}")
        
        return accessibility
    
    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze basic performance metrics"""
        performance = {
            "load_time": 0,
            "resource_count": 0,
            "dom_size": 0
        }
        
        try:
            # Get performance metrics
            performance_data = await self.page.evaluate("""
                () => {
                    const perf = performance.getEntriesByType('navigation')[0];
                    return {
                        loadTime: perf ? perf.loadEventEnd - perf.loadEventStart : 0,
                        resourceCount: performance.getEntriesByType('resource').length,
                        domSize: document.querySelectorAll('*').length
                    };
                }
            """)
            
            performance["load_time"] = performance_data.get("loadTime", 0)
            performance["resource_count"] = performance_data.get("resourceCount", 0)
            performance["dom_size"] = performance_data.get("domSize", 0)
            
        except Exception as e:
            logger.warning(f"Failed to analyze performance: {e}")
        
        return performance
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import re
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        return domain_match.group(1) if domain_match else url
    
    def _create_fallback_analysis(self, url: str) -> Dict[str, Any]:
        """Create fallback analysis when scraping fails"""
        return {
            "url": url,
            "title": "Analysis Failed",
            "domain": self._extract_domain(url),
            "elements": [],
            "forms": [],
            "navigation": {},
            "interactions": [],
            "content": {},
            "accessibility": {},
            "performance": {},
            "error": "Failed to analyze website structure"
        }

async def scrape_website_sync(url: str, headless: bool = True) -> Dict[str, Any]:
    """Synchronous wrapper for website scraping"""
    async with URLScraper(headless=headless) as scraper:
        return await scraper.scrape_website(url)

def scrape_website(url: str, headless: bool = True) -> Dict[str, Any]:
    """Synchronous function to scrape website"""
    return asyncio.run(scrape_website_sync(url, headless))

def scrape_website_blocking(url: str, headless: bool = True) -> Dict[str, Any]:
    """Blocking scraper using Playwright sync API to avoid event loop conflicts."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            page.set_viewport_size({"width": 1280, "height": 720})
            page.goto(url, wait_until="networkidle", timeout=30000)

            def elem_info(el) -> Dict[str, Any]:
                tag = el.evaluate("el => el.tagName.toLowerCase()")
                type_attr = el.get_attribute('type') or ''
                text = (el.inner_text() or '').strip()
                placeholder = el.get_attribute('placeholder') or ''
                aria_label = el.get_attribute('aria-label') or ''
                role = el.get_attribute('role') or ''
                bbox = el.bounding_box() or {"x": 0, "y": 0, "width": 0, "height": 0}
                def categorize(tag: str, t: str, role: str) -> str:
                    if tag == 'button' or role == 'button':
                        return 'button'
                    if tag == 'a' or role == 'link':
                        return 'link'
                    if tag == 'input':
                        if t in ['text', 'email', 'password', 'search']:
                            return 'text_input'
                        if t in ['submit', 'button']:
                            return 'button'
                        if t in ['checkbox', 'radio']:
                            return 'selection'
                        return 'input'
                    if tag == 'textarea':
                        return 'text_area'
                    if tag == 'select':
                        return 'dropdown'
                    return 'other'
                def test_name(text: str, placeholder: str, aria: str, tag: str) -> str:
                    if text:
                        return text[:50]
                    if placeholder:
                        return f"{placeholder} input"
                    if aria:
                        return aria[:50]
                    return f"{tag} element"
                # basic selector
                element_id = el.get_attribute('id')
                if element_id:
                    selector = f"#{element_id}"
                else:
                    classes = (el.get_attribute('class') or '').strip().replace(' ', '.')
                    selector = f"{tag}.{classes}" if classes else tag
                return {
                    "tag": tag,
                    "type": type_attr,
                    "category": categorize(tag, type_attr, role),
                    "text": text,
                    "placeholder": placeholder,
                    "aria_label": aria_label,
                    "role": role,
                    "test_name": test_name(text, placeholder, aria_label, tag),
                    "selector": selector,
                    "position": bbox,
                    "interactive": tag in ['button','a','input','textarea','select'] or type_attr in ['button','submit','checkbox','radio'] or role in ['button','link','tab','menuitem'],
                    "selector_type": tag
                }

            clickable = page.query_selector_all("button, a[href], input[type='submit'], input[type='button'], [role='button'], [onclick], [tabindex]")
            inputs = page.query_selector_all("input, textarea, select, [contenteditable='true']")
            elements: List[Dict[str, Any]] = []
            for el in clickable:
                try:
                    elements.append(elem_info(el))
                except Exception:
                    pass
            for el in inputs:
                try:
                    elements.append(elem_info(el))
                except Exception:
                    pass

            # Forms
            forms: List[Dict[str, Any]] = []
            for form in page.query_selector_all('form'):
                fields = []
                for fld in form.query_selector_all('input, textarea, select'):
                    try:
                        fields.append(elem_info(fld))
                    except Exception:
                        pass
                submit = form.query_selector("input[type='submit'], button[type='submit'], button:not([type])")
                submit_info = elem_info(submit) if submit else None
                forms.append({
                    "action": form.get_attribute('action') or '',
                    "method": form.get_attribute('method') or 'get',
                    "fields": fields,
                    "submit_button": submit_info
                })

            title = page.title()
            browser.close()

            domain = re.search(r'https?://(?:www\.)?([^/]+)', url)
            domain = domain.group(1) if domain else url
            return {
                "url": url,
                "title": title,
                "domain": domain,
                "elements": elements,
                "forms": forms,
                "navigation": {"main_menu": []},
                "interactions": [],
                "content": {},
                "accessibility": {},
                "performance": {}
            }
    except Exception as e:
        logger.error(f"Blocking scrape failed for {url}: {e}")
        return {
            "url": url,
            "title": "Analysis Failed",
            "domain": url,
            "elements": [],
            "forms": [],
            "navigation": {},
            "interactions": [],
            "content": {},
            "accessibility": {},
            "performance": {},
            "error": str(e)
        }
