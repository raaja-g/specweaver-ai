@checkout
Feature: test the application

  Scenario: Successfully deduct stock for an order
    Given product SKU "BLND-X1-PRO" has a stock level of 100
    When a `POST /api/v2/inventory/deduct` request is received for 2 units of SKU "BLND-X1-PRO"
    Then the API should respond with a 200 OK status
    And the new stock level for SKU "BLND-X1-PRO" should be 98

  Scenario: Idempotent order submission
    Given I am on the payment confirmation page
    When I click 'Place Order' multiple times in quick succession
    Then only a single order is created

  Scenario: Idempotent order submission
    Given I am on the payment confirmation page
    When I click 'Place Order' multiple times in quick succession
    Then only a single order is created

  Scenario: Idempotent order submission
    Given I am on the payment confirmation page
    When I click 'Place Order' multiple times in quick succession
    Then only a single order is created

