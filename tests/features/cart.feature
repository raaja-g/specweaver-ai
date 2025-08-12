@cart
Feature: test the application
  As a tester
  I want test the application
  So that ensure quality and functionality

  Background:
    Given the site is available
    And I start a clean browser session

  @P0 @positive @cart_&_mini-cart @positive @scenario  Scenario: View mini-cart
    When I open the mini-cart
    Then I see line items and subtotal

  @P0 @positive @cart_&_mini-cart @positive @scenario  Scenario: Apply coupon code
    When I apply coupon "WELCOME10"
    Then totals reflect the coupon

  @P2 @edge @auto @edge  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

  @P2 @edge @auto @edge  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

  @P2 @edge @auto @edge  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

  @P2 @edge @auto @edge  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

  @P2 @edge @auto @edge  Scenario: Edge quantity maximum
    Given I am on a product detail page
    When I set quantity to 999
    Then I see an error that quantity exceeds allowed maximum

