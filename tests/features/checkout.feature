@checkout
Feature: test the application

  Scenario: [P2] Attempt to proceed with a missing required field
    Given I am on the guest checkout shipping address page
    When I fill all shipping address fields except for 'City'
    And I click the 'Next' button
    Then I should see a validation error message 'This is a required field.' for the City field
    And I should remain on the shipping address page

  Scenario: [P1] Provide shipping information for different US states and ZIP codes [1]
    Given I am on the guest checkout shipping address page
    When I enter the email 'test@example.com' and phone '555-555-5555'
    And I fill the address with '456 Oak Avenue', 'Anytown', 'Texas', and '75001'
    And I select a shipping method
    Then I should be able to proceed to the next step

  Scenario: [P1] Provide shipping information for different US states and ZIP codes [2]
    Given I am on the guest checkout shipping address page
    When I enter the email 'test@example.com' and phone '555-555-5555'
    And I fill the address with '789 Pine Lane', 'Springfield', 'Illinois', and '62704'
    And I select a shipping method
    Then I should be able to proceed to the next step

  Scenario: [P1] Provide shipping information for different US states and ZIP codes [3]
    Given I am on the guest checkout shipping address page
    When I enter the email 'test@example.com' and phone '555-555-5555'
    And I fill the address with '101 Maple Court', 'Metropolis', 'New York', and '10001'
    And I select a shipping method
    Then I should be able to proceed to the next step

  Scenario: [P1] Provide shipping information for different US states and ZIP codes [4]
    Given I am on the guest checkout shipping address page
    When I enter the email 'test@example.com' and phone '555-555-5555'
    And I fill the address with '212 Birch Road', 'Gotham', 'New Jersey', and '07002'
    And I select a shipping method
    Then I should be able to proceed to the next step

  Scenario: [P0] Default shipping method is pre-selected and its cost is applied
    Given I have provided a valid shipping address in California
    When I land on the shipping method selection step
    Then the 'Flat Rate - Fixed' shipping method is selected by default
    And the order summary shows a shipping cost of '$5.00'

  Scenario: [P1] Change shipping method and verify total cost update
    Given the 'Flat Rate - Fixed' method is selected with a total of '$80.00'
    When I select the 'Best Way - Table Rate' shipping method
    Then the shipping cost in the order summary updates to '$10.00'
    And the order total updates to '$85.00'

  Scenario: [P1] Verify shipping costs for different order values [1]
    Given I have items in my cart totaling '49.99'
    And I have provided a valid US shipping address
    When I select the 'Best Way - Table Rate' shipping method
    Then the calculated shipping fee in the order summary should be '10.00'
    And the order total should be correct

  Scenario: [P1] Verify shipping costs for different order values [2]
    Given I have items in my cart totaling '50.00'
    And I have provided a valid US shipping address
    When I select the 'Best Way - Table Rate' shipping method
    Then the calculated shipping fee in the order summary should be '5.00'
    And the order total should be correct

  Scenario: [P1] Verify shipping costs for different order values [3]
    Given I have items in my cart totaling '100.00'
    And I have provided a valid US shipping address
    When I select the 'Best Way - Table Rate' shipping method
    Then the calculated shipping fee in the order summary should be '5.00'
    And the order total should be correct

  Scenario: [P1] Verify shipping costs for different order values [4]
    Given I have items in my cart totaling '0.00'
    And I have provided a valid US shipping address
    When I select the 'Best Way - Table Rate' shipping method
    Then the calculated shipping fee in the order summary should be '0.00'
    And the order total should be correct

  Scenario: [P0] Successfully pay with a new credit card
    Given I am on the payment step of checkout
    When I select the 'Credit Card' payment method
    And I enter valid credit card number '4242424242424242', expiry '12/25', and CVV '123'
    And I ensure the billing address matches my shipping address
    And I click 'Place Order'
    Then my payment is processed successfully
    And I am taken to the order confirmation page

  Scenario: [P1] A registered user pays with a saved credit card
    Given I am a logged-in user with a saved credit card
    When I reach the payment step
    Then my saved card is available for selection
    And I select my saved card 'ending in 1111'
    And I click 'Place Order'
    Then I am taken to the order confirmation page

  Scenario: [P2] Attempt to pay with an expired credit card
    Given I am on the payment step of checkout
    When I enter a credit card number '4242424242424242' with an expiration date in the past, like '01/20'
    And I click 'Place Order'
    Then I see an error message 'Credit card expiration date is not valid.'
    And I remain on the payment page

  Scenario: [P2] Attempt to pay with an invalid CVV
    Given I am on the payment step of checkout
    When I enter valid credit card details but an invalid CVV 'ABC'
    And I click 'Place Order'
    Then I see an error message 'Please enter a valid credit card verification number.'
    And I remain on the payment page

  Scenario: [P1] Successfully apply a valid promotional code
    Given I have items in my cart and I am on the checkout page
    When I expand the 'Apply Discount Code' section
    And I enter a valid code '20OFF'
    And I click 'Apply Discount'
    Then a success message 'Your coupon was successfully applied.' is displayed
    And the Order Summary updates to show a 'Discount' line item
    And the Order Total is reduced accordingly

  Scenario: [P2] Attempt to apply invalid or expired promotional codes [1]
    Given I am on the checkout page
    When I enter the discount code 'INVALIDCODE'
    And I click 'Apply Discount'
    Then I should see the error message 'The coupon code "INVALIDCODE" is not valid.'

  Scenario: [P2] Attempt to apply invalid or expired promotional codes [2]
    Given I am on the checkout page
    When I enter the discount code 'EXPIRED2020'
    And I click 'Apply Discount'
    Then I should see the error message 'The coupon code "EXPIRED2020" is not valid.'

  Scenario: [P2] Attempt to apply invalid or expired promotional codes [3]
    Given I am on the checkout page
    When I enter the discount code ''
    And I click 'Apply Discount'
    Then I should see the error message 'This is a required field.'

  Scenario: [P0] Review and confirm all order details are correct before placing order
    Given I am on the final review step of checkout
    And my shipping address is '123 Main St, Los Angeles, CA 90001'
    And my shipping method is 'Flat Rate' for '$5.00'
    And my cart contains '1 x Radiant Tee' for '$22.00'
    Then I verify the shipping address, shipping method, and items are all correct in the summary
    And the total is calculated correctly as '$27.00'
    When I click 'Place Order'
    Then I am redirected to the 'Thank you for your purchase!' page

  Scenario: [P1] Navigate back to edit shipping information from the review step
    Given I am on the final review step of checkout
    When I click the 'Edit' link for the shipping address
    Then I am taken back to the shipping address page
    When I update the address and proceed back to the review step
    Then the review page reflects the updated shipping address

  Scenario: [P1] Verify order number is present on confirmation page
    Given I have just clicked 'Place Order' and the transaction was successful
    When I am on the order confirmation page
    Then I see the heading 'Thank you for your purchase!'
    And I see the text 'Your order number is:' followed by a numeric order ID

  Scenario: [P1] Confirmation email contains correct shipping and billing information
    Given order '000012345' had a shipping address in 'Los Angeles' and billing address in 'New York'
    When the confirmation email for this order is inspected
    Then the email should display the 'Los Angeles' address under 'Shipping Address'
    And the email should display the 'New York' address under 'Billing Address'

  Scenario: [P2] Confirmation email is not sent for a failed order
    Given a customer attempts to place an order but the payment is declined
    When the order placement fails
    Then an order confirmation email MUST NOT be sent to the customer's email address

  Scenario: [P2] Validation message for invalid phone number format
    Given I am on the guest checkout shipping page
    When I enter 'INVALID-PHONE' in the phone number field
    And I attempt to proceed to the next step
    Then I should see a validation error message like 'Please enter a valid phone number.'
    And I should remain on the shipping page

  Scenario: [P2] Validation message for invalid ZIP code format
    Given I am on the guest checkout shipping page
    When I select 'United States' as the country
    And I enter 'ABCDE' in the ZIP code field
    And I attempt to proceed to the next step
    Then I should see a validation error message indicating the ZIP code format is incorrect for the selected country

  Scenario: [P2] Test boundary validation for required text fields [1]
    Given I am on the guest checkout shipping page
    When I enter '' in the 'First Name' field
    And I fill all other fields correctly
    And I attempt to proceed
    Then the system should respond with 'an error message 'This is a required field.''

  Scenario: [P2] Test boundary validation for required text fields [2]
    Given I am on the guest checkout shipping page
    When I enter 'J' in the 'First Name' field
    And I fill all other fields correctly
    And I attempt to proceed
    Then the system should respond with 'no error message'

  Scenario: [P2] Test boundary validation for required text fields [3]
    Given I am on the guest checkout shipping page
    When I enter 'Johnathan Maximillian' in the 'First Name' field
    And I fill all other fields correctly
    And I attempt to proceed
    Then the system should respond with 'no error message'

  Scenario: [P2] Test boundary validation for required text fields [4]
    Given I am on the guest checkout shipping page
    When I enter 'NameWith$pecialChar' in the 'First Name' field
    And I fill all other fields correctly
    And I attempt to proceed
    Then the system should respond with 'an error message 'Invalid character in name.''

  Scenario: [P2] Real-time validation on field blur
    Given I am on the guest checkout shipping page
    When I type an invalid email 'test@test' into the email field
    And I click or tab into another field
    Then a validation error message for the email field should appear immediately without me clicking 'Next'

  Scenario: [P1] Stock is reserved for a short period upon reaching payment step
    Given the stock for 'Radiant Tee' is 2
    And I add 2 'Radiant Tee' to my cart and proceed to the payment page
    When another user tries to add 'Radiant Tee' to their cart
    Then they should see an 'Out of Stock' message
    And my stock reservation should expire after 15 minutes of inactivity

  Scenario: [P2] A generic card decline shows a user-friendly message
    Given I am on the payment page and have entered details for a card that will be declined
    When I click 'Place Order'
    Then the payment gateway returns a 'DECLINED' response
    And I see a message 'Your payment could not be processed. Please check your card details or try a different payment method.'
    And I remain on the payment page with my cart contents intact

  Scenario: [P3] A payment gateway timeout is handled without placing the order
    Given I am on the payment page
    When I click 'Place Order' and the payment gateway API does not respond within the 30-second timeout
    Then I see a message 'The payment service is temporarily unavailable. Please try again in a few minutes.'
    And no order is created in the system
    And my cart is not emptied

  Scenario: [P2] Specific error messages are shown for different decline reasons [1]
    Given I am on the payment page
    When I attempt to pay with a card that triggers a 'insufficient_funds' from the payment gateway
    Then I should see the user-friendly message: 'Your card was declined due to insufficient funds.'

  Scenario: [P2] Specific error messages are shown for different decline reasons [2]
    Given I am on the payment page
    When I attempt to pay with a card that triggers a 'incorrect_cvc' from the payment gateway
    Then I should see the user-friendly message: 'The security code (CVV) you entered is incorrect.'

  Scenario: [P2] Specific error messages are shown for different decline reasons [3]
    Given I am on the payment page
    When I attempt to pay with a card that triggers a 'do_not_honor' from the payment gateway
    Then I should see the user-friendly message: 'Your bank has declined this transaction. Please contact your bank for more information.'

  Scenario: [P2] Specific error messages are shown for different decline reasons [4]
    Given I am on the payment page
    When I attempt to pay with a card that triggers a 'invalid_account' from the payment gateway
    Then I should see the user-friendly message: 'The credit card number you entered is invalid.'

  Scenario: [P2] User can retry payment with a different card after a failure
    Given my first payment attempt with card A was declined
    And I am still on the payment page
    When I enter the details for a valid card B
    And I click 'Place Order' again
    Then the payment is processed successfully
    And I am taken to the order confirmation page

  Scenario: [P3] Rapidly clicking 'Place Order' button only creates one order
    Given I am on the final review step and all my details are correct
    When I double-click the 'Place Order' button very quickly
    Then the button should become disabled after the first click
    And only one order (e.g. '000012346') is created in the system
    And my payment method is charged only once

  Scenario: [P3] (API) Submitting an order with a duplicate idempotency key does not create a new order
    Given a client application is submitting an order via API
    When an API POST request to '/api/orders' is made with idempotency key 'uuid-xyz-123'
    Then order '000012347' is created and a 201 response is returned
    When the same API POST request with idempotency key 'uuid-xyz-123' is sent again due to a network retry
    Then a 200 response with the original order '000012347' data is returned
    And a new order is not created

  Scenario: [P3] Refreshing the order confirmation page does not re-submit the order
    Given I have successfully placed order '000012348' and am on the confirmation page
    When I refresh the browser page
    Then I remain on the confirmation page for order '000012348'
    And no new transaction or order is created

