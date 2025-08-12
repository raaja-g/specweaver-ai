#!/usr/bin/env python3
"""
Test script to demonstrate URL scraping functionality
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from core.url_scraper import scrape_website
from core.dynamic_test_generator import DynamicTestGenerator

def test_url_scraping():
    """Test the URL scraping functionality"""
    print("🚀 Testing URL Scraping Functionality")
    print("=" * 50)
    
    # Test URL
    test_url = "https://www.google.com"
    print(f"Testing with URL: {test_url}")
    
    try:
        # Test URL scraping
        print("\n1. Scraping website structure...")
        analysis = scrape_website(test_url, headless=True)
        
        if analysis.get("error"):
            print(f"❌ Scraping failed: {analysis['error']}")
            return
        
        print("✅ Website analysis completed!")
        print(f"   - Title: {analysis.get('title', 'N/A')}")
        print(f"   - Domain: {analysis.get('domain', 'N/A')}")
        print(f"   - Elements found: {len(analysis.get('elements', []))}")
        print(f"   - Forms found: {len(analysis.get('forms', []))}")
        print(f"   - Navigation items: {len(analysis.get('navigation', {}).get('main_menu', []))}")
        
        # Test dynamic test generation
        print("\n2. Generating dynamic BDD tests...")
        generator = DynamicTestGenerator()
        features = generator.generate_tests_from_website(test_url, headless=True)
        
        print(f"✅ Generated {len(features)} BDD features!")
        
        for i, feature in enumerate(features, 1):
            print(f"\n   Feature {i}: {feature.get('feature_name', 'Unknown')}")
            scenarios = feature.get('scenarios', [])
            print(f"   - Scenarios: {len(scenarios)}")
            
            for j, scenario in enumerate(scenarios, 1):
                scenario_name = scenario.get('name', 'Unknown')
                scenario_type = scenario.get('type', 'scenario')
                print(f"     {j}. {scenario_name} ({scenario_type})")
                
                if scenario_type == 'scenario_outline' and 'examples' in scenario:
                    examples = scenario.get('examples', [])
                    print(f"       Examples: {len(examples)}")
        
        print("\n🎯 Dynamic test generation successful!")
        print("The system now creates tests based on actual website structure!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_scraping()
