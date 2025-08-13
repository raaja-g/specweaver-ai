@checkout
Feature: to add a product to my cart and check out with a credit card

  Scenario: [P0] Successful payment with a valid Visa card
    Given I am at the payment step of the checkout process
    And I have entered a valid shipping address and selected a shipping method
    When I enter valid Visa credit card details and my billing address
    And I click 'Place Order'
    Then the payment is processed successfully
    And I am redirected to the Order Confirmation page
    And I see an order confirmation number

  Scenario: [P0] Declined payment due to an invalid card number
    Given I am at the payment step of the checkout process
    When I enter an invalid credit card number '4111111111111112'
    And I fill out the remaining card details and click 'Place Order'
    Then I see an error message 'The credit card number is invalid. Please check the number and try again.'
    And my card is not charged
    And I remain on the payment page

  Scenario: [P1] Declined payment due to insufficient funds
    Given I am at the payment step and using a card with insufficient funds
    When I enter all valid card details and click 'Place Order'
    Then the payment gateway declines the transaction
    And I see an error message 'Your payment was declined. Please try a different card or contact your bank.'
    And my card is not charged

  Scenario: [P1] Payment form validation for various card errors [1]
    Given I am at the payment step of checkout
    When I enter '4242424242424242' with an '01/20' and '123'
    And I click 'Place Order'
    Then I should see the error message 'Card has expired. Please use a different card.'
    And the order is not placed

  Scenario: [P1] Payment form validation for various card errors [2]
    Given I am at the payment step of checkout
    When I enter '4242424242424242' with an '12/29' and '12'
    And I click 'Place Order'
    Then I should see the error message 'Invalid security code.'
    And the order is not placed

  Scenario: [P1] Payment form validation for various card errors [3]
    Given I am at the payment step of checkout
    When I enter '12345' with an '12/29' and '123'
    And I click 'Place Order'
    Then I should see the error message 'Invalid card number.'
    And the order is not placed

  Scenario: [P0] View order confirmation page after successful checkout
    Given I have just successfully completed a checkout
    Then I am on the 'Thank You' or 'Order Confirmation' page
    And I see a unique order number like 'ORD-2023-A7B3C9'
    And I see a summary of the items I purchased
    And I see the shipping address and total amount charged

  Scenario: [P1] Receive an order confirmation email
    Given I have successfully placed an order with email 'shopper@example.com'
    When I check the inbox for 'shopper@example.com'
    Then I should have an email with the subject 'Your order ORD-2023-A7B3C9 has been received!'
    And the email body should contain the order details and a link to view the order status

  Scenario: [P1] View list of past orders in my account
    Given I am a registered shopper and have placed at least two orders in the past
    When I log in and navigate to the 'My Account' -> 'Order History' section
    Then I see a list of my past orders, each with an order number, date, total amount, and status

  Scenario: [P2] View details of a specific past order
    Given I am on the 'Order History' page
    And I see an order with number 'ORD-2022-X5Y4Z1'
    When I click on the order number 'ORD-2022-X5Y4Z1'
    Then I am taken to the order detail page for that order
    And I can see the items, quantities, prices, shipping address, and tracking information if available

  Scenario: [P2] Order status is displayed correctly in history [1]
    Given I am viewing my order history
    When I look at order 'ORD-2023-A7B3C9'
    Then its status should be displayed as 'Processing'

  Scenario: [P2] Order status is displayed correctly in history [2]
    Given I am viewing my order history
    When I look at order 'ORD-2023-A6F1B8'
    Then its status should be displayed as 'Shipped'

  Scenario: [P2] Order status is displayed correctly in history [3]
    Given I am viewing my order history
    When I look at order 'ORD-2023-Z2P5K7'
    Then its status should be displayed as 'Delivered'

  Scenario: [P2] Order status is displayed correctly in history [4]
    Given I am viewing my order history
    When I look at order 'ORD-2023-C4L9M3'
    Then its status should be displayed as 'Cancelled'

  Scenario: [P2] User double-clicks the 'Place Order' button
    Given a registered shopper is on the final checkout review page with a unique cart ID 'CART-XYZ-123'
    When the user clicks the 'Place Order' button twice in quick succession
    Then the system generates an idempotency key for the first request
    And the first API call to `POST /api/v1/orders` succeeds, creating order 'ORD-98765'
    And the second API call with the same idempotency key is received
    Then the system recognizes the duplicate request
    And returns the success response for the original order 'ORD-98765' without creating a new order
    And only one charge is made to the customer's card

  Scenario: [P2] Network client retries an order submission after a timeout
    Given a client is submitting an order via `POST /api/v1/orders` with idempotency key 'idem-key-abc'
    And the first request is successfully processed by the server, but the response is lost due to a network error
    When the client's retry logic sends the exact same request again with 'idem-key-abc'
    Then the server's idempotency layer identifies it as a duplicate of a completed request
    And the server returns the originally generated successful response
    And no new order is created or payment processed

  Scenario: [P3] Idempotency key is respected for a failed initial transaction
    Given an order submission with idempotency key 'idem-key-fail' fails due to 'Insufficient Funds'
    When the client retries the same request with the same key 'idem-key-fail'
    Then the server should not re-process the payment
    And should immediately return the original 'Insufficient Funds' error response

  Scenario: [P1] Inventory is successfully reserved and decremented upon order placement
    Given there are 10 units of 'Yoga Mat Pro' (SKU: YMP-GRN) in stock
    And I have 2 units in my cart and proceed to checkout
    When I successfully place my order
    Then the inventory level for SKU 'YMP-GRN' is atomically decremented to 8
    And the items are reserved for my order 'ORD-12345'

  Scenario: [P2] Inventory is released back into stock if a payment fails
    Given there is 1 unit of 'Standing Desk' (SKU: DSK-STND-WHT) in stock
    And I place the item in my cart and proceed to the payment page
    When my payment is declined
    Then the temporary reservation of the item is released
    And the inventory count for SKU 'DSK-STND-WHT' remains at 1 and is available for other customers

  Scenario: [P0] Select a shipping method and see updated total
    Given I am on the shipping method selection step of checkout
    And my order subtotal is $50.00
    And the 'Standard Shipping' option is selected by default with a cost of $5.99
    Then the order total is displayed as $55.99
    When I select 'Express Shipping' with a cost of $15.99
    Then the order total updates to $65.99

  Scenario: [P1] Free shipping is automatically applied for qualifying orders
    Given the store offers free standard shipping on orders over $75
    And my cart subtotal is $89.00
    When I proceed to the shipping method selection step
    Then the 'Standard Shipping' option is displayed with a cost of '$0.00 (Free)'
    And the order total reflects the free shipping

  Scenario: [P1] Shipping costs are calculated correctly for different destinations [1]
    Given I have items in my cart
    And I have entered a shipping address in 'Continental US'
    When I view the available shipping methods
    Then the cost for 'Standard Shipping' should be '$5.99'
    And the cost for 'Express Shipping' should be '$15.99'

  Scenario: [P1] Shipping costs are calculated correctly for different destinations [2]
    Given I have items in my cart
    And I have entered a shipping address in 'Alaska/Hawaii'
    When I view the available shipping methods
    Then the cost for 'Standard Shipping' should be '$12.99'
    And the cost for 'Express Shipping' should be '$25.99'

  Scenario: [P1] Shipping costs are calculated correctly for different destinations [3]
    Given I have items in my cart
    And I have entered a shipping address in 'Canada'
    When I view the available shipping methods
    Then the cost for 'Standard Shipping' should be '$19.99'
    And the cost for 'Express Shipping' should be '$39.99'

  Scenario: [P2] Delete a saved payment method
    Given I have a saved 'Visa ending in 4242' in my wallet
    When I navigate to 'Payment Methods' and click 'Delete' for that card
    And I confirm the deletion in the confirmation prompt
    Then the card 'Visa ending in 4242' is no longer listed in my wallet

