"""
Domain Detection and Context Loading
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DomainDetector:
    """Detects domain from requirements and loads appropriate context"""
    
    def __init__(self, domains_dir: str = "config/domains"):
        self.domains_dir = Path(domains_dir)
        self.domains = self._load_domains()
    
    def _load_domains(self) -> Dict[str, Dict[str, Any]]:
        """Load all available domain configurations"""
        domains = {}
        
        if not self.domains_dir.exists():
            logger.warning(f"Domains directory {self.domains_dir} not found")
            return domains
        
        for domain_file in self.domains_dir.glob("*.yml"):
            try:
                with open(domain_file, 'r') as f:
                    domain_config = yaml.safe_load(f)
                    domain_name = domain_config.get('domain', domain_file.stem)
                    domains[domain_name] = domain_config
                    logger.info(f"Loaded domain: {domain_name}")
            except Exception as e:
                logger.error(f"Failed to load domain {domain_file}: {e}")
        
        return domains
    
    def detect_domain(self, requirement_text: str, url: str = "") -> str:
        """
        Detect domain from requirement text and URL
        
        Args:
            requirement_text: The requirement description
            url: Optional URL that might indicate domain
            
        Returns:
            Detected domain name or 'generic'
        """
        text_lower = requirement_text.lower()
        url_lower = url.lower()
        
        # E-commerce keywords
        ecommerce_keywords = [
            'ecommerce', 'e-commerce', 'shop', 'cart', 'checkout', 'product', 
            'buy', 'purchase', 'payment', 'order', 'catalog', 'inventory',
            'store', 'retail', 'marketplace', 'coupon', 'discount'
        ]
        
        # Banking keywords  
        banking_keywords = [
            'bank', 'banking', 'account', 'transfer', 'payment', 'loan',
            'credit', 'debit', 'balance', 'transaction', 'financial', 'money'
        ]
        
        # Healthcare keywords
        healthcare_keywords = [
            'health', 'medical', 'doctor', 'patient', 'appointment', 'hospital',
            'clinic', 'prescription', 'medicine', 'diagnosis', 'treatment'
        ]
        
        # Check URL patterns first
        if any(word in url_lower for word in ['shop', 'store', 'ecommerce', 'cart']):
            return 'ecommerce'
        elif any(word in url_lower for word in ['bank', 'financial', 'credit']):
            return 'banking'  
        elif any(word in url_lower for word in ['health', 'medical', 'hospital']):
            return 'healthcare'
        elif any(word in url_lower for word in ['google.com', 'search', 'gmail', 'youtube']):
            return 'generic'
        
        # Check text content
        if any(word in text_lower for word in ecommerce_keywords):
            return 'ecommerce'
        elif any(word in text_lower for word in banking_keywords):
            return 'banking'
        elif any(word in text_lower for word in healthcare_keywords):
            return 'healthcare'
        
        # Default to generic
        return 'generic'
    
    def get_domain_context(self, domain: str) -> Dict[str, Any]:
        """
        Get domain-specific context for BDD generation
        
        Args:
            domain: Domain name
            
        Returns:
            Domain context dictionary
        """
        if domain in self.domains:
            return self.domains[domain]
        
        # Return generic context if domain not found
        return {
            'domain': 'generic',
            'description': 'Generic web application testing',
            'context': 'This is a generic web application. Focus on core functionality, navigation, user interface, search capabilities, and overall user experience.',
            'functional_areas': [
                'Page Loading & Navigation',
                'Search Functionality', 
                'User Interface Elements',
                'Content Display',
                'Form Interactions',
                'Error Handling',
                'Performance & Responsiveness'
            ],
            'example_features': '''
Feature: Page Navigation
As a user
I want to navigate through the website
So that I can access different sections

Background:
Given the website is accessible

Scenario: Load homepage successfully
When I navigate to the homepage
Then the page loads completely
And all main elements are visible

Scenario: Navigate to different sections
When I click on navigation links
Then I am taken to the correct pages
And the content loads properly

Feature: Search Functionality  
As a user
I want to search for information
So that I can find what I need

Scenario: Perform basic search
When I enter a search query
Then I see relevant results
And the results are properly formatted
            ''',
            'realistic_data': {
                'search_queries': ['test query', 'example search', 'sample text'],
                'navigation_items': ['Home', 'About', 'Contact', 'Services'],
                'test_data': ['sample input', 'test value', 'example text']
            }
        }
    
    def list_available_domains(self) -> list:
        """Return list of available domains"""
        return list(self.domains.keys())
