@checkout
Feature: test the application

  Scenario: Toggle between monthly and yearly billing
    Given I am on the pricing page
    And the 'Scale' plan shows a price of '$599 /mo'
    And the billing toggle is set to 'Billed Monthly'
    When I click the toggle to select 'Billed Yearly'
    Then the 'Scale' plan should show a price of '$549 /mo'
    And the toggle should indicate 'Billed Yearly' is active

