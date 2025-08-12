@general
Feature: to add a product to my cart and check out with a credit card

  Scenario: View details of an in-stock product with multiple variants
    Given I am on the product page for 'TrailMax Hiking Backpack' (SKU: HBP-GRN-40L)
    Then I should see the product name 'TrailMax Hiking Backpack'
    And I should see the price '$99.95'
    And I should see a gallery with at least 3 product images
    And I should see a color selector with options 'Forest Green', 'Ocean Blue', and 'Slate Grey'
    And I should see a stock status message 'In Stock'

  Scenario: View details of a product that is out of stock
    Given I am on the product page for 'Limited Edition Compass' (SKU: CMP-LTD-01)
    Then I should see the product name 'Limited Edition Compass'
    And I should see a stock status message 'Out of Stock'
    And the 'Add to Cart' button should be disabled
    And I should see an option to 'Notify me when back in stock'

  Scenario: Selecting a different product variant updates the page
    Given I am on the product page for 'TrailMax Hiking Backpack' (SKU: HBP-GRN-40L)
    When I select the color 'Ocean Blue'
    Then the main product image should update to show the blue backpack
    And the SKU displayed on the page should update to 'HBP-BLU-40L'

  Scenario: View product reviews and ratings
    Given I am on the product page for 'TrailMax Hiking Backpack'
    When I scroll down to the 'Reviews' section
    Then I should see an average star rating, such as '4.7 out of 5 stars'
    And I should see a list of customer reviews with reviewer names, ratings, and comments

  Scenario: Apply a valid percentage-based discount code
    Given I am on the cart page with a subtotal of $200.00
    When I enter the valid discount code 'SAVE15' in the discount code field
    And I click 'Apply'
    Then I see a message 'Discount code SAVE15 applied successfully.'
    And a line item for 'Discount (15%)' appears with a value of '-$30.00'
    And the order total is updated to $170.00

  Scenario: Apply a valid fixed-amount discount code
    Given I am on the cart page with a subtotal of $80.00
    When I enter the valid discount code 'TENOFF' in the discount code field
    And I click 'Apply'
    Then a line item for 'Discount' appears with a value of '-$10.00'
    And the order total is updated to $70.00

  Scenario: Attempt to apply a discount code that does not meet minimum spend
    Given I am on the cart page with a subtotal of $45.00
    When I enter the discount code 'SAVE50' which requires a $50 minimum spend
    And I click 'Apply'
    Then I should see an error message 'This discount code requires a minimum purchase of $50.00.'

  Scenario: Invalid and expired discount code validation [1]
    Given I am on the cart page
    When I enter the discount code 'INVALIDCODE'
    And I click 'Apply'
    Then I should see an error message 'Discount code 'INVALIDCODE' is not valid.'
    And the order total should not change

  Scenario: Invalid and expired discount code validation [2]
    Given I am on the cart page
    When I enter the discount code 'EXPIRED2020'
    And I click 'Apply'
    Then I should see an error message 'This discount code is expired.'
    And the order total should not change

  Scenario: Invalid and expired discount code validation [3]
    Given I am on the cart page
    When I enter the discount code 'ALREADYUSED'
    And I click 'Apply'
    Then I should see an error message 'This discount code has already been used.'
    And the order total should not change

  Scenario: User can switch to a different saved card after a decline
    Given I am a logged-in user with two saved credit cards, 'Visa ending in 4242' and 'Mastercard ending in 5555'
    And my payment attempt with the Visa card was declined
    When I select the 'Mastercard ending in 5555'
    And I submit the payment again
    Then the payment should be authorized successfully
    And I should proceed to the order review page

