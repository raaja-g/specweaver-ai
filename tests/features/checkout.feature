@checkout
Feature: Auto Synthesized

  Scenario: View available shipping methods and costs
    Given I am on the shipping method step of checkout with a subtotal of $50.00
    Then I should see 'Standard Shipping (5-7 business days)' with a price of '$5.99'
    And I should see 'Expedited Shipping (2-3 business days)' with a price of '$12.99'
    And I should see 'Overnight Shipping (1 business day)' with a price of '$25.99'

  Scenario: Select a shipping method and see the order total update
    Given I am on the shipping method step and the order total is '$104.93'
    And 'Standard Shipping' at $5.99 is selected by default
    When I select 'Expedited Shipping' at '$12.99'
    Then the displayed Order Total should update to '$117.92'
    And when I click 'Continue to Payment'
    Then I am taken to the payment information page

  Scenario: Free shipping is applied for orders over a certain amount
    Given my cart subtotal is '$155.00', which is over the $100 free shipping threshold
    When I proceed to the shipping method step
    Then 'Standard Shipping' should be displayed with a price of '$0.00' or 'Free'
    And it should be selected by default

  Scenario: Successful payment with a valid Visa credit card
    Given I am on the payment step of checkout
    And the order total is $117.92
    When I enter a valid Visa card number '4242424242424242'
    And I enter expiration date '12/25' and CVV '123'
    And I click 'Review Order'
    Then my payment should be authorized successfully
    And I should be taken to the final order review page

  Scenario: Payment attempt with an invalid card number format
    Given I am on the payment step of checkout
    When I enter an invalid card number '12345'
    And I click 'Review Order'
    Then the payment should be declined client-side
    And I should see an error message 'Please enter a valid credit card number.' below the card number field
    And no payment authorization request should be sent

  Scenario: Payment attempt with a card that has an invalid CVV
    Given I am on the payment step of checkout
    When I enter a valid Mastercard number and expiration date
    And I enter an invalid CVV '999'
    And I click 'Review Order'
    Then the payment gateway should decline the transaction
    And I should see an error message 'Your card was declined. Please check your CVV and try again.'

  Scenario: Pay with different valid card types [1]
    Given I am on the payment step of checkout
    When I enter a valid Visa number '4242424242424242'
    And I enter a valid expiration date and CVV
    And I click 'Review Order'
    Then the card type logo for Visa should be displayed
    And I should be taken to the final order review page

  Scenario: Pay with different valid card types [2]
    Given I am on the payment step of checkout
    When I enter a valid Mastercard number '5555555555555555'
    And I enter a valid expiration date and CVV
    And I click 'Review Order'
    Then the card type logo for Mastercard should be displayed
    And I should be taken to the final order review page

  Scenario: Pay with different valid card types [3]
    Given I am on the payment step of checkout
    When I enter a valid American Express number '378282246310005'
    And I enter a valid expiration date and CVV
    And I click 'Review Order'
    Then the card type logo for American Express should be displayed
    And I should be taken to the final order review page

  Scenario: Payment is declined due to insufficient funds
    Given I am on the payment step and have entered card details for a card with insufficient funds
    When I submit the payment
    Then the payment gateway should decline the transaction
    And I should see the error message 'Your card was declined due to insufficient funds.'
    And my card should not be charged
    And I should be able to edit my payment information

  Scenario: Payment is declined due to an expired card
    Given I am on the payment step of checkout
    When I enter card details with an expiration date in the past, like '01/20'
    And I submit the payment
    Then I should see an error message 'This card is expired. Please use a different card or check the expiration date.'
    And the transaction should not be processed

  Scenario: Payment is declined due to a generic processor error
    Given I am on the payment step and have entered valid card details
    And the payment processor returns a generic 'Do Not Honor' decline code
    When I submit the payment
    Then I should see a generic error message 'Your card was declined by the bank. Please try another card or contact your bank.'
    And my card should not be charged

  Scenario: Review and successfully place an order
    Given I am on the final 'Order Review' page
    And I can see my shipping address, payment method, and all items with a final total of '$117.92'
    When I click the 'Place Order' button
    Then the order is processed successfully
    And I am redirected to an 'Order Confirmation' page
    And I see a message 'Thank you for your order!'
    And I am shown a unique Order Confirmation Number, like 'ORD-2023-C8XF2G'

  Scenario: Receive an order confirmation email
    Given I have successfully placed an order with confirmation number 'ORD-2023-C8XF2G'
    And my registered email is 'shopper@example.com'
    When I check my email inbox
    Then I should have received an email with the subject 'Your Order Confirmation ORD-2023-C8XF2G'
    And the email body should contain the order details, including items, cost, and shipping address

  Scenario: Inventory check fails right before final submission
    Given I am on the 'Order Review' page for an order containing 'Limited Edition Tent'
    And just before I click 'Place Order', another user buys the last 'Limited Edition Tent'
    When I click the 'Place Order' button
    Then the order submission fails
    And I am shown an error message 'One or more items in your order are now out of stock. Please review your cart.'
    And I am redirected back to the shopping cart page to make adjustments

  Scenario: View list of past orders
    Given I am a logged-in shopper and have previously placed at least two orders
    When I navigate to 'My Account' and click on 'Order History'
    Then I should see a list of my past orders
    And each list item should display the Order Number, Date Placed, Total Amount, and Status (e.g., 'Processing', 'Shipped')

  Scenario: View details of a specific past order
    Given I am on the 'Order History' page
    When I click on the order with number 'ORD-2023-A9B1C2'
    Then I am taken to the order details page for that order
    And I can see the full order summary, including items purchased, prices, shipping address, and payment method used

  Scenario: Order history pagination
    Given I am a shopper with 35 past orders and the page size is 10
    When I navigate to my 'Order History' page
    Then I should see the 10 most recent orders
    And I should see pagination controls to navigate to pages 2, 3, and 4

  Scenario: No orders are displayed for a new user
    Given I am a newly registered shopper and have not placed any orders
    When I navigate to my 'Order History' page
    Then I should see a message 'You have not placed any orders yet.'

  Scenario: Double-clicking the 'Place Order' button only creates one order
    Given a shopper is on the 'Order Review' page with a valid order ready for submission
    When the shopper double-clicks the 'Place Order' button in quick succession
    Then the system should process the first request to create an order
    And the system should reject the second request with a 'duplicate request' or similar error
    And only one order with a unique ID should be created in the database
    And the customer should only be charged once

  Scenario: 'Place Order' button is disabled after the first click
    Given a shopper is on the 'Order Review' page
    When the shopper clicks the 'Place Order' button
    Then the 'Place Order' button should be immediately disabled
    And the button text should change to 'Processing...'

  Scenario: API rejects order creation with a duplicate idempotency key
    Given the client generates a unique idempotency key 'uuid-abc-123' for an order submission
    When the client sends a POST request to '/api/orders' with the idempotency key
    Then the server successfully creates the order and stores the result against the key
    And when the client immediately sends the exact same POST request again with key 'uuid-abc-123'
    Then the server should not create a new order
    And the API should return the stored successful response from the first request with a 200 OK status

