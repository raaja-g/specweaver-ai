@checkout
Feature: test the application
  As a tester
  I want test the application
  So that ensure quality and functionality

  Background:
    Given the site is available
    And I start a clean browser session

  @P2 @edge @auto @edge  Scenario: Idempotent order submission
    Given I am on the payment confirmation page
    When I click 'Place Order' multiple times in quick succession
    Then only a single order is created

  @P2 @edge @auto @edge  Scenario: Idempotent order submission
    Given I am on the payment confirmation page
    When I click 'Place Order' multiple times in quick succession
    Then only a single order is created

  @P2 @edge @auto @edge  Scenario: Idempotent order submission
    Given I am on the payment confirmation page
    When I click 'Place Order' multiple times in quick succession
    Then only a single order is created

  @P2 @edge @auto @edge  Scenario: Idempotent order submission
    Given I am on the payment confirmation page
    When I click 'Place Order' multiple times in quick succession
    Then only a single order is created

