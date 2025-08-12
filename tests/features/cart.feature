@cart
Feature: test the application

  Scenario: Handle concurrent requests for the last item
    Given product SKU "LAST-ITEM-01" has a stock level of 1 and uses optimistic locking
    When two concurrent `POST /api/v2/inventory/deduct` requests are received for 1 unit of SKU "LAST-ITEM-01"
    Then only the first request should succeed with a 200 OK status
    And the second request should fail with a 409 Conflict status
    And the final stock level for SKU "LAST-ITEM-01" should be 0

  Scenario: Restock items for a returned order
    Given product SKU "BLND-X1-PRO" has a stock level of 90
    When a `POST /api/v2/inventory/restock` request is received for 3 units of SKU "BLND-X1-PRO" from a return
    Then the API should respond with a 200 OK status
    And the new stock level for SKU "BLND-X1-PRO" should be 93

  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

