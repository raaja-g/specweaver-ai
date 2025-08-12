@cart
Feature: test the application

  Scenario: [P0] Successfully complete shipping details with a valid address
    Given I have a 'Radiant Tee' and a 'Strive Shoulder Pack' in my cart
    And I proceed to checkout as a guest
    When I fill the shipping address form with valid details for 'Jane Doe' at '123 Main St, Los Angeles, CA 90001'
    And I enter the email 'jane.doe@example.com' and phone number '555-123-4567'
    And I select 'Flat Rate' shipping
    Then I can proceed to the 'Payment Method' step

  Scenario: [P2] Attempt to proceed with an invalid email address format
    Given I am on the guest checkout shipping address page
    When I fill the shipping address form with the email 'jane.doe-invalid-email'
    And I click the 'Next' button
    Then I should see a validation error message 'Please enter a valid email address (Ex: johndoe@domain.com).'
    And I should remain on the shipping address page

  Scenario: [P0] Checkout using the default saved shipping address
    Given I am a registered user and logged in
    And I have at least two saved addresses, one of which is a default
    And I have items in my cart and I proceed to checkout
    Then my default shipping address is pre-selected
    When I click the 'Next' button
    Then I proceed to the payment step without entering new address details

  Scenario: [P1] Select a non-default saved shipping address
    Given I am a logged-in user with multiple saved addresses on the checkout shipping page
    When I select a different, non-default saved address from my address book
    And I click the 'Next' button
    Then the order summary should reflect the newly selected address
    And I proceed to the payment step

  Scenario: [P1] Add a new shipping address during checkout
    Given I am a logged-in user on the checkout shipping page
    When I click the 'New Address' button
    And I fill in the new address form for '100 New Way, San Francisco, CA 94105'
    And I choose to save this address to my address book
    And I proceed to the next step
    Then the new address is used for shipping
    And it appears in my list of saved addresses for future orders

  Scenario: [P2] Edit an existing address during checkout
    Given I am a logged-in user on the checkout shipping page
    When I choose to edit my default shipping address
    And I update the street address to '125 Updated Ave' and the ZIP code to '90028'
    And I save the changes
    Then the updated address is selected for the current order
    And the address is permanently updated in my address book

  Scenario: [P2] Shipping methods available are dependent on the shipping address
    Given I have provided a shipping address outside the United States
    When I proceed to the shipping method step
    Then I should not see domestic-only shipping options like 'USPS Priority Mail'
    And I should see international shipping options

  Scenario: [P0] Use the same address for shipping and billing
    Given I am on the payment page after entering my shipping address
    When the 'My billing and shipping address are the same' checkbox is checked
    And I place the order successfully
    Then the order confirmation details show identical shipping and billing addresses

  Scenario: [P1] Specify a different billing address
    Given I am on the payment page
    When I uncheck the 'My billing and shipping address are the same' checkbox
    Then a new address form for the billing address appears
    When I fill the billing address form with '777 Corporate Dr, New York, NY 10004'
    And I place the order
    Then the order confirmation shows the correct, different shipping and billing addresses

  Scenario: [P2] Attempt to proceed with an incomplete separate billing address
    Given I have unchecked 'My billing and shipping address are the same'
    When I fill the billing address form but omit the 'Street' field
    And I attempt to place the order
    Then I see a validation error 'This is a required field.' for the Street field
    And the order is not placed

  Scenario: [P1] A logged-in user selects a different saved address for billing
    Given I am a logged-in user with multiple saved addresses
    And I am on the payment page
    When I uncheck the 'My billing and shipping address are the same' checkbox
    And I select a different saved address from the dropdown for my billing address
    And I place the order
    Then the order is placed successfully using the selected billing address

  Scenario: [P2] Remove an applied promotional code
    Given I have successfully applied the discount code '20OFF'
    And the order total reflects the discount
    When I click the 'Cancel' or 'Remove' button for the applied coupon
    Then a success message 'Your coupon was successfully removed.' is displayed
    And the 'Discount' line item is removed from the Order Summary
    And the Order Total reverts to its original amount

  Scenario: [P3] Attempt to apply a discount code that does not meet cart criteria
    Given I have a cart total of $40
    And a valid discount code 'FREESHIP50' exists for orders over $50
    When I enter the code 'FREESHIP50' and apply it
    Then I see an error message indicating the minimum purchase amount has not been met
    And the discount is not applied

  Scenario: [P0] Order is placed and cart becomes empty
    Given I have successfully placed an order
    When I navigate back to the shopping cart page
    Then I see the message 'You have no items in your shopping cart.'
    And the cart icon in the header shows '0' items

  Scenario: [P1] An order confirmation email is sent to the customer's email address
    Given a customer with email 'confirmation-test@example.com' has successfully placed order '000012345'
    When the order processing is complete
    Then an email with the subject 'Your Luma order confirmation' should be sent to 'confirmation-test@example.com'
    And the email body should contain the order number '000012345'

  Scenario: [P1] Confirmation email contains correct item details
    Given order '000012345' contained '1 x Radiant Tee' and '2 x Quest Lumaflex™ Band'
    When the confirmation email for this order is inspected
    Then the email body should list 'Radiant Tee' with quantity 1
    And it should list 'Quest Lumaflex™ Band' with quantity 2

  Scenario: [P1] User is prevented from checking out when an item goes out of stock
    Given I have '1 x Summit Watch' (SKU: 24-MB04) in my cart, and its stock level is 1
    And another customer simultaneously purchases the last 'Summit Watch'
    When I proceed to the final review step of checkout
    Then I see a message 'The requested qty is not available'
    And the 'Place Order' button is disabled

  Scenario: [P1] Cart quantity is automatically updated if requested quantity exceeds stock
    Given I have '10 x Luma Analog Watch' in my cart
    And the current stock for 'Luma Analog Watch' is only 5
    When I proceed to the checkout page
    Then my cart is automatically updated to '5 x Luma Analog Watch'
    And a message is displayed: 'We updated your cart item quantity to match the available stock.'

  Scenario: [P2] User is redirected to cart with error message if item is OOS on page load
    Given I have an item in my cart that was in stock yesterday
    And the item is now out of stock
    When I visit the checkout URL directly from a bookmark
    Then I am redirected to the shopping cart page
    And a message is displayed: 'One or more items in your cart are no longer available.'

