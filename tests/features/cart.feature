@cart
Feature: Auto Synthesized

  Scenario: Add a single, in-stock product to an empty cart
    Given I am logged in and viewing the product 'Waterproof Shell Jacket' (SKU: WJK-RED-M) which is in stock
    And my shopping cart is empty
    When I click the 'Add to Cart' button
    Then a confirmation pop-up appears with the message 'Waterproof Shell Jacket has been added to your cart'
    And the cart icon in the header updates to show 1 item

  Scenario: Add the same product to the cart again
    Given I have 1 'Waterproof Shell Jacket' (SKU: WJK-RED-M) in my cart
    And I am viewing the product page for 'Waterproof Shell Jacket'
    When I click the 'Add to Cart' button again
    Then the cart icon in the header still shows 1 unique item
    And when I navigate to the cart page
    Then the quantity for 'Waterproof Shell Jacket' should be 2

  Scenario: Attempt to add an out-of-stock product to the cart
    Given I am viewing the product 'Solar-Powered Lantern' (SKU: SPL-001) which is out of stock
    Then the 'Add to Cart' button should be disabled
    When I attempt to add the item to the cart via a direct API call to '/api/cart/add'
    Then the API should return a 409 Conflict status
    And the response body should contain an error message 'Item SKU: SPL-001 is out of stock'

  Scenario: Add a specific quantity of an item to the cart [1]
    Given I am on the product page for 'Merino Wool Socks' (SKU: MWS-GRY-L) priced at $18.50
    When I select a quantity of '1'
    And I click 'Add to Cart'
    And I navigate to the cart page
    Then the line item for 'Merino Wool Socks' should show quantity '1' and a total of '$18.50'

  Scenario: Add a specific quantity of an item to the cart [2]
    Given I am on the product page for 'Merino Wool Socks' (SKU: MWS-GRY-L) priced at $18.50
    When I select a quantity of '3'
    And I click 'Add to Cart'
    And I navigate to the cart page
    Then the line item for 'Merino Wool Socks' should show quantity '3' and a total of '$55.50'

  Scenario: Add a specific quantity of an item to the cart [3]
    Given I am on the product page for 'Merino Wool Socks' (SKU: MWS-GRY-L) priced at $18.50
    When I select a quantity of '5'
    And I click 'Add to Cart'
    And I navigate to the cart page
    Then the line item for 'Merino Wool Socks' should show quantity '5' and a total of '$92.50'

  Scenario: View items in the cart
    Given I have added a 'TrailMax Hiking Backpack' at $99.95 and two 'Energy Gel Packs' at $2.49 each to my cart
    When I navigate to the shopping cart page
    Then I should see a line item for 'TrailMax Hiking Backpack' with quantity 1 and price $99.95
    And I should see a line item for 'Energy Gel Pack' with quantity 2 and price $4.98
    And the cart subtotal should be displayed as '$104.93'

  Scenario: Update the quantity of an item in the cart
    Given I have a 'TrailMax Hiking Backpack' with quantity 1 in my cart
    When I am on the shopping cart page
    And I change the quantity for 'TrailMax Hiking Backpack' to '3'
    Then the line item total for the backpack should update to '$299.85'
    And the cart subtotal should update to '$299.85'

  Scenario: Remove an item from the cart
    Given I have a 'TrailMax Hiking Backpack' and 'Merino Wool Socks' in my cart
    When I am on the shopping cart page
    And I click the 'Remove' button for 'Merino Wool Socks'
    Then the 'Merino Wool Socks' line item should be removed from the cart
    And the cart subtotal should be updated to only reflect the price of the backpack

  Scenario: Cart displays a warning when item stock is low
    Given an item 'Headlamp' (SKU: HLP-05) has only 3 units left in stock
    And I have 2 'Headlamp' items in my cart
    When I view the shopping cart
    And I update the quantity for 'Headlamp' to 4
    Then a warning message 'Only 3 units available. Quantity updated.' is displayed next to the item
    And the quantity field for 'Headlamp' is automatically adjusted to 3

  Scenario: Cart contents persist after logging out and back in
    Given I am a logged-in shopper
    And I have added a 'Waterproof Shell Jacket' to my cart
    When I log out of my account
    And I log back in with the same credentials
    And I navigate to the shopping cart page
    Then I should see the 'Waterproof Shell Jacket' in my cart

  Scenario: Merging guest cart with account cart upon login
    Given I am not logged in and have a 'Fleece Pullover' in my guest cart
    And my registered account cart contains a 'Hiking Boot' from a previous session
    When I log into my account
    And I navigate to the shopping cart page
    Then my cart should contain both the 'Fleece Pullover' and the 'Hiking Boot'

  Scenario: Cart item is removed if it goes out of stock between sessions
    Given I am a logged-in shopper with a 'Limited Edition Tent' in my cart
    And I log out
    And an administrator marks the 'Limited Edition Tent' as out of stock
    When I log back into my account
    And I view my cart
    Then the cart should be empty
    And I should see a message 'Some items in your cart are no longer available and have been removed.'

  Scenario: Cart is cleared after a successful order
    Given I am a logged-in shopper with items in my cart
    When I successfully complete the checkout process and place an order
    And I navigate back to the shopping cart page
    Then my cart should be empty
    And I should see a message 'Your cart is empty.'

  Scenario: Enter a new valid shipping address
    Given I am on the shipping address step of the checkout
    When I fill in the shipping address form with valid data for 'Jane Doe'
    And I click the 'Continue to Shipping Method' button
    Then I should be taken to the shipping method selection page

  Scenario: Select a previously saved shipping address
    Given I am a logged-in shopper with a saved address for '123 Main St, Anytown, USA 12345'
    And I am on the shipping address step of the checkout
    When I select the saved address '123 Main St'
    And I click the 'Continue to Shipping Method' button
    Then the shipping details are pre-filled
    And I am taken to the shipping method selection page

  Scenario: Address validation service suggests a correction
    Given I am on the shipping address step of the checkout
    When I enter '123 Main Stret' and ZIP code '90210'
    And I click 'Continue to Shipping Method'
    Then I should see a suggestion: 'Did you mean 123 Main Street, Beverly Hills, CA 90210?'
    And I should have options to 'Use Suggested Address' or 'Use Address as Entered'

  Scenario: Shipping address form field validation [1]
    Given I am on the shipping address step of the checkout
    When I fill in the form but leave the 'First Name' blank
    And I click 'Continue to Shipping Method'
    Then I should see a validation error 'First Name is required.' next to the field

  Scenario: Shipping address form field validation [2]
    Given I am on the shipping address step of the checkout
    When I fill in the form but leave the 'Street Address' blank
    And I click 'Continue to Shipping Method'
    Then I should see a validation error 'Street Address is required.' next to the field

  Scenario: Shipping address form field validation [3]
    Given I am on the shipping address step of the checkout
    When I fill in the form but leave the 'ZIP Code' blank
    And I click 'Continue to Shipping Method'
    Then I should see a validation error 'A valid ZIP Code is required.' next to the field

  Scenario: Shipping address form field validation [4]
    Given I am on the shipping address step of the checkout
    When I fill in the form but leave the 'City' blank
    And I click 'Continue to Shipping Method'
    Then I should see a validation error 'City is required.' next to the field

  Scenario: Certain items restrict shipping options
    Given my cart contains a 'Bear Spray' canister, which has shipping restrictions
    When I proceed to the shipping method step
    Then 'Overnight Shipping' and 'Expedited Shipping' options should be disabled or not visible
    And only 'Standard Ground Shipping' should be available

  Scenario: Go back from review page to edit the cart
    Given I am on the 'Order Review' page
    When I click the 'Edit Cart' link
    Then I am taken back to the shopping cart page
    And I can modify my cart's contents

