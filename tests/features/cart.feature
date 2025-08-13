@cart
Feature: to add a product to my cart and check out with a credit card

  Scenario: [P0] Add an in-stock product to the cart from the PDP
    Given I am on the product page for 'Anker PowerCore 10000' (SKU: ANK-PC10K) which costs $25.99
    And my cart is initially empty
    When I set the quantity to 1 and click the 'Add to Cart' button
    Then I see a confirmation message 'Anker PowerCore 10000 was added to your cart'
    And the cart icon in the header shows a count of 1
    And when I navigate to the cart page, I see 'Anker PowerCore 10000' with quantity 1 and price $25.99

  Scenario: [P1] Attempt to add more units of a product than are available in stock
    Given I am on the product page for 'Limited Edition Vinyl Record' (SKU: LE-VNYL-01)
    And the system shows 'Only 3 left in stock'
    When I set the quantity to 5 and click 'Add to Cart'
    Then I see an error message 'Only 3 units are available. Please adjust the quantity.'
    And the product is not added to my cart

  Scenario: [P2] Adding a product to the cart using the Quick Add feature from a category page
    Given I am on the 'Electronics' category page and my cart has 1 item
    And I see a product listing for 'USB-C Cable' with a 'Quick Add' button
    When I click the 'Quick Add' button for the 'USB-C Cable'
    Then the cart icon in the header updates to show a count of 2
    And a confirmation flyout appears showing the item was added

  Scenario: [P0] Add a product with specific variants to the cart [1]
    Given I am on the product page for the 'Performance T-Shirt' (SKU: PERF-TS)
    When I select the color 'Charcoal' and size 'L'
    And I click the 'Add to Cart' button
    Then the cart should contain 'Performance T-Shirt' with details 'Color: Charcoal, Size: L'
    And the SKU in the cart line item should be 'PERF-TS-CHA-L'

  Scenario: [P0] Add a product with specific variants to the cart [2]
    Given I am on the product page for the 'Performance T-Shirt' (SKU: PERF-TS)
    When I select the color 'White' and size 'M'
    And I click the 'Add to Cart' button
    Then the cart should contain 'Performance T-Shirt' with details 'Color: White, Size: M'
    And the SKU in the cart line item should be 'PERF-TS-WHT-M'

  Scenario: [P0] Add a product with specific variants to the cart [3]
    Given I am on the product page for the 'Performance T-Shirt' (SKU: PERF-TS)
    When I select the color 'Navy' and size 'XL'
    And I click the 'Add to Cart' button
    Then the cart should contain 'Performance T-Shirt' with details 'Color: Navy, Size: XL'
    And the SKU in the cart line item should be 'PERF-TS-NAV-XL'

  Scenario: [P0] Update the quantity of an item in the cart
    Given I have 1 'Smart Water Bottle' (SKU: SWB-V2, Price: $59.95) in my cart
    When I go to the shopping cart page
    And I change the quantity for 'Smart Water Bottle' from 1 to 3
    Then the line item total for 'Smart Water Bottle' updates to $179.85
    And the cart subtotal is correctly recalculated

  Scenario: [P0] Remove an item from the cart
    Given my cart contains 'Noise Cancelling Earbuds' and 'Wireless Charging Pad'
    When I go to the shopping cart page
    And I click the 'Remove' button for 'Wireless Charging Pad'
    Then the 'Wireless Charging Pad' is no longer displayed in the cart
    And the cart subtotal is updated to reflect only the price of the 'Noise Cancelling Earbuds'

  Scenario: [P1] Cart persists after session ends and I log back in
    Given I am a registered shopper and I add 'Ergonomic Keyboard' to my cart
    And I log out of my account
    When I log back into my account the next day
    And I navigate to the cart page
    Then I should see 'Ergonomic Keyboard' still in my cart

  Scenario: [P2] Attempt to update quantity to an invalid value
    Given I have 2 'Desk Lamp' items in my cart
    When I go to the shopping cart page
    And I try to update the quantity for 'Desk Lamp' to 0
    Then the item is removed from the cart
    When I try to update the quantity to -1
    Then I see an error 'Quantity must be a positive number.' and the quantity remains 2

  Scenario: [P3] View an empty cart
    Given I am a registered shopper with an empty cart
    When I navigate to the shopping cart page
    Then I see a message 'Your shopping cart is empty.'
    And I see a 'Continue Shopping' button

  Scenario: [P0] Enter a new valid shipping address
    Given I am in the checkout process at the shipping step
    When I fill in the shipping address form with valid details for '123 Main St, Anytown, CA 90210'
    And I click 'Continue to Shipping Method'
    Then my address is saved and I proceed to the next step

  Scenario: [P0] Select a previously saved shipping address
    Given I am a returning shopper with a saved address for '456 Oak Ave, Someplace, NY 10001'
    And I am in the checkout process at the shipping step
    When I select the saved address '456 Oak Ave'
    And I click 'Continue to Shipping Method'
    Then I proceed to the next step with the selected address

  Scenario: [P1] Address validation service suggests a correction
    Given I am in the checkout process at the shipping step
    When I enter the address '100 Penn Ave' with zip code '15221'
    And I click 'Continue to Shipping Method'
    Then I see a suggestion: 'Did you mean 100 S Pennsylvania Ave, Pittsburgh, PA 15221?'
    And I have the option to accept the suggestion or keep my original entry

  Scenario: [P1] Form validation for incomplete shipping address [1]
    Given I am in the checkout process at the shipping step
    And I have left the 'Street Address' field blank
    When I click 'Continue to Shipping Method'
    Then I see an error message 'Street Address is required.' next to the 'Street Address' field
    And I remain on the shipping address step

  Scenario: [P1] Form validation for incomplete shipping address [2]
    Given I am in the checkout process at the shipping step
    And I have left the 'City' field blank
    When I click 'Continue to Shipping Method'
    Then I see an error message 'City is required.' next to the 'City' field
    And I remain on the shipping address step

  Scenario: [P1] Form validation for incomplete shipping address [3]
    Given I am in the checkout process at the shipping step
    And I have left the 'Zip Code' field blank
    When I click 'Continue to Shipping Method'
    Then I see an error message 'Zip Code is required.' next to the 'Zip Code' field
    And I remain on the shipping address step

  Scenario: [P1] Form validation for incomplete shipping address [4]
    Given I am in the checkout process at the shipping step
    And I have left the 'Last Name' field blank
    When I click 'Continue to Shipping Method'
    Then I see an error message 'Last Name is required.' next to the 'Last Name' field
    And I remain on the shipping address step

  Scenario: [P3] Remove an applied discount code
    Given I have successfully applied the discount code 'SAVE20' for a -$30.00 discount
    And my order total is $120.00
    When I click the 'Remove' link next to the discount line item
    Then the discount line item disappears
    And the order total reverts to $150.00

  Scenario: [P3] A request with a different idempotency key for the same cart is treated as a new request
    Given a request to create an order for cart 'CART-XYZ-123' with idempotency key 'idem-A' has been processed
    When a new request for the same cart 'CART-XYZ-123' arrives but with a different key 'idem-B'
    Then the system treats this as a distinct, new request
    And attempts to process a new order, which may fail due to the cart already being converted to an order

  Scenario: [P1] Last item in stock is purchased by another user during checkout
    Given I have the last unit of 'Collector's Edition Watch' (SKU: CW-LMT-01) in my cart
    And I am on the final payment page
    And another user completes checkout for that same item just before I do
    When I click 'Place Order'
    Then the system re-validates inventory and finds the item is out of stock
    And I see an error message 'Sorry, Collector's Edition Watch just went out of stock and has been removed from your cart.'
    And my payment is not processed
    And I am returned to the cart page to review the changes

  Scenario: [P3] Cart is updated if an item goes out of stock before checkout begins
    Given I have 'Bluetooth Speaker' (SKU: BT-SPK-RED) in my cart from a previous session
    And since then, the item has gone out of stock
    When I log in and navigate to my cart
    Then I see a message next to the item: 'This item is now out of stock and cannot be purchased.'
    And the item's price is excluded from the cart subtotal
    And I cannot proceed to checkout until I remove it

  Scenario: [P2] Shipping options are restricted for certain addresses
    Given I have entered a P.O. Box as my shipping address
    When I proceed to the shipping method selection step
    Then the 'Overnight Courier' option is not available
    And I only see options compatible with P.O. Box delivery, like 'USPS Standard'

  Scenario: [P1] Add a new shipping address to my address book
    Given I am logged in and on the 'My Account' page
    When I navigate to the 'Address Book' section and click 'Add New Address'
    And I fill in and save a valid new address
    Then the new address appears in my list of saved addresses

  Scenario: [P1] Add a new payment method to my wallet
    Given I am logged in and on the 'My Account' page
    When I navigate to the 'Payment Methods' section and click 'Add New Card'
    And I enter valid Mastercard details and save
    Then I see the new card listed, identified by 'Mastercard ending in 1098'

  Scenario: [P2] Edit an existing shipping address
    Given I have a saved address '123 Old St'
    When I navigate to my 'Address Book' and click 'Edit' for that address
    And I change the street to '456 New Ave' and save
    Then the address in my address book is updated to '456 New Ave'

