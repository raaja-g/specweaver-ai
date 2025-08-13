@general
Feature: to add a product to my cart and check out with a credit card

  Scenario: [P0] View details of a standard in-stock product
    Given I am a registered shopper and I am on the product page for SKU 'KC-ELITE-24'
    Then I should see the product name 'Keurig K-Elite Coffee Maker'
    And I should see the price '$189.99'
    And I should see the 'Add to Cart' button is enabled
    And I see a stock status of 'In Stock'

  Scenario: [P1] View details of an out-of-stock product
    Given I am a registered shopper and I am on the product page for SKU 'LOGI-MXM3-OOS'
    Then I should see the product name 'Logitech MX Master 3 Mouse'
    And I should see a stock status of 'Out of Stock'
    And the 'Add to Cart' button should be disabled
    And I should see an option to 'Notify Me When Available'

  Scenario: [P2] Interact with product image gallery
    Given I am on the product page for 'Bose QC45 Headphones'
    And I see a primary image and 3 thumbnail images
    When I click the second thumbnail image
    Then the primary image updates to show the second product view
    When I click the primary image
    Then a full-screen image zoom modal opens

  Scenario: [P0] Select different product variants and see updated information [1]
    Given I am on the product page for the 'TrailRunner X1 Jacket'
    When I select the color 'Ocean Blue' and size 'Medium'
    Then the product image updates to show the 'Ocean Blue' jacket
    And the SKU displayed on the page updates to 'TRX1-BLU-M'
    And the 'Add to Cart' button is enabled

  Scenario: [P0] Select different product variants and see updated information [2]
    Given I am on the product page for the 'TrailRunner X1 Jacket'
    When I select the color 'Crimson Red' and size 'Large'
    Then the product image updates to show the 'Crimson Red' jacket
    And the SKU displayed on the page updates to 'TRX1-RED-L'
    And the 'Add to Cart' button is enabled

  Scenario: [P0] Select different product variants and see updated information [3]
    Given I am on the product page for the 'TrailRunner X1 Jacket'
    When I select the color 'Forrest Green' and size 'Small'
    Then the product image updates to show the 'Forrest Green' jacket
    And the SKU displayed on the page updates to 'TRX1-GRN-S'
    And the 'Add to Cart' button is enabled

  Scenario: [P1] Apply a valid percentage-based discount code
    Given I have items in my cart with a subtotal of $150.00
    When I am on the cart page
    And I enter the valid discount code 'SAVE20' for 20% off
    And I click 'Apply'
    Then I see a discount line item of '-$30.00'
    And the new order total is $120.00

  Scenario: [P1] Apply a valid fixed-amount discount code
    Given I have items in my cart with a subtotal of $75.00
    When I am on the cart page
    And I enter the valid discount code '10OFF' for $10 off
    And I click 'Apply'
    Then I see a discount line item of '-$10.00'
    And the new order total is $65.00

  Scenario: [P2] Attempt to apply an expired discount code
    Given I am on the cart page
    When I enter the expired discount code 'SUMMER22'
    And I click 'Apply'
    Then I see an error message 'This discount code is expired.'
    And the order total remains unchanged

  Scenario: [P2] Attempt to apply a discount code that does not meet minimum purchase requirement
    Given I have items in my cart with a subtotal of $40.00
    And the discount code 'BIGSPENDER' requires a $100 minimum purchase
    When I enter the discount code 'BIGSPENDER'
    And I click 'Apply'
    Then I see an error message 'Your order must be at least $100.00 to use this code.'
    And the order total remains unchanged

