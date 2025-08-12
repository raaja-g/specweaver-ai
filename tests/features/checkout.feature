@checkout
Feature: test the e-commerce website functionality

  Scenario: Successful checkout with valid shipping and payment information
    Given I am a guest user with 'Strive Endurance Fleece' in my cart
    When I proceed to checkout
    And I fill in shipping details with email 'guest.user@example.com', name 'John Doe', address '123 Main St', city 'Austin', state 'Texas', ZIP '78701', country 'United States' and phone '5125551234'
    And I select the 'Fixed' shipping method
    And I provide valid credit card information
    And I click 'Place Order'
    Then I see the 'Thank you for your purchase!' confirmation page
    And I receive an order confirmation email at 'guest.user@example.com'

  Scenario: Checkout fails due to an invalid shipping ZIP code
    Given I am a guest at the checkout shipping address step
    When I fill in the shipping address with an invalid ZIP code 'ABCDE'
    And I click the 'Next' button
    Then I see a validation error message 'Provided Zip/Postal Code is incorrect.'
    And I remain on the shipping address step

  Scenario: Checkout fails due to a declined credit card
    Given I have filled in valid shipping information and proceeded to the payment step
    When I enter deliberately invalid or declined credit card details
    And I click 'Place Order'
    Then I see an error message 'Your payment could not be processed. Please check your details and try again.'
    And the order is not placed

  Scenario: Verify order summary updates with shipping method change
    Given I am on the checkout page with a subtotal of $58.00
    When I select the 'Fixed' shipping method with a cost of $5.00
    Then the Order Summary shows a Shipping cost of $5.00 and an Order Total of $63.00
    When I select the 'Best Way' shipping method with a cost of $10.00
    Then the Order Summary shows a Shipping cost of $10.00 and an Order Total of $68.00

  Scenario: View list of recent orders
    Given I am a logged-in user with previous orders
    When I navigate to 'My Account' and then to the 'My Orders' section
    Then I see a list of my orders with their order number, date, ship-to name, total, and status
    And the orders are paginated if the list is long

  Scenario: View details of a specific order
    Given I am on the 'My Orders' page
    When I click the 'View Order' link for a specific order
    Then I am taken to the order details page
    And I can see the items ordered, shipping address, billing address, shipping method, and payment method

  Scenario: Reorder from a past order
    Given I am viewing the details of a completed order
    When I click the 'Reorder' button
    Then all in-stock items from that order are added to my current shopping cart
    And I am redirected to the shopping cart page

  Scenario: View empty order history for a new user
    Given I am a newly registered user who has not placed any orders
    When I navigate to the 'My Orders' section
    Then I see a message 'You have placed no orders.'

  Scenario: Stock level decreases after a successful order is placed
    Given the 'Argus All-Weather Tank' has an inventory of 50
    When a customer successfully purchases 2 units of 'Argus All-Weather Tank'
    Then the inventory level for 'Argus All-Weather Tank' in the database is updated to 48

