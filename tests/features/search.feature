@search
Feature: test the e-commerce website functionality

  Scenario: Search for a specific, known product name
    Given I am a guest user on the homepage
    When I enter 'Hero Hoodie' into the search bar and press Enter
    Then the search results page should be displayed
    And I should see the 'Hero Hoodie' product in the results

  Scenario: Search for a general category
    Given I am on any page with a search bar
    When I search for 'pants'
    Then the search results should include multiple products like 'Portia Capri' and 'Rhea Legging'
    And the search results title should contain 'pants'

  Scenario: Search that yields no results
    Given I am looking for a product
    When I search for 'nonexistent-product-xyz123'
    Then I should see a message indicating 'Your search returned no results.'
    And I should not see any product listings

  Scenario: Search using a product SKU
    Given I know the SKU for a specific product
    When I search for the SKU 'MH07'
    Then the search results should exclusively show the 'Hero Hoodie' product

  Scenario: Search using partial and alternative terms [1]
    Given I am on the homepage
    When I search for the term "Strive"
    Then the search results should include the product "Strive Endurance Fleece"

  Scenario: Search using partial and alternative terms [2]
    Given I am on the homepage
    When I search for the term "fleece"
    Then the search results should include the product "Strive Endurance Fleece"

  Scenario: Search using partial and alternative terms [3]
    Given I am on the homepage
    When I search for the term "lumaflex"
    Then the search results should include the product "Quest Lumaflex™ Band"

  Scenario: Search using partial and alternative terms [4]
    Given I am on the homepage
    When I search for the term "bag"
    Then the search results should include the product "Push It Messenger Bag"

  Scenario: Filter products by a single attribute
    Given I am viewing the 'Women/Tops' category
    When I apply the 'Color' filter and select 'Blue'
    Then all products displayed, like 'Ingrid Running Jacket', should be available in 'Blue'
    And the 'Now Shopping by' section should show the 'Color: Blue' filter

  Scenario: Filter products by multiple attributes
    Given I am viewing the 'Men/Hoodies & Sweatshirts' category
    When I apply the 'Size' filter 'L'
    And I apply the 'Color' filter 'Black'
    Then only products available in size 'L' and color 'Black' are displayed
    And the 'Now Shopping by' section shows both filters

  Scenario: Clear an applied filter
    Given I have filtered the 'Gear/Bags' category by 'Material: Polyester'
    When I click the 'x' icon next to the 'Material: Polyester' filter in the 'Now Shopping by' section
    Then the 'Material' filter is removed
    And the product list updates to show items of all materials

  Scenario: Sort product list by different criteria [1]
    Given I am viewing a category page with multiple products
    When I select the 'Price' option from the 'Sort By' dropdown
    Then the products are re-ordered with the Quest Lumaflex™ Band appearing before the Hero Hoodie

  Scenario: Sort product list by different criteria [2]
    Given I am viewing a category page with multiple products
    When I select the 'Product Name' option from the 'Sort By' dropdown
    Then the products are re-ordered with the Argus All-Weather Tank appearing before the Strive Endurance Fleece

