Feature: ecommerce website https://luma.enablementadobe.com/content/luma/us/en.html
  As a user
  I want ecommerce website https://luma.enablementadobe.com/content/luma/us/en.html
  So that meet their requirements

  Background:
    Given the test environment is configured
    And execution mode is set to "real" for UI and "mock" for API

  @P0 @positive @cart_&_mini-cart @positive @scenario  Scenario: Cart & Mini-cart: View mini-cart
    Given Given I have at least one item in my cart
    When I perform "user.action" with params:
      """
      {
  "description": "When I open the mini-cart"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then I see line items and subtotal"
}
      """
    Then Scenario 'View mini-cart' completes successfully

  @P0 @positive @cart_&_mini-cart @positive @scenario  Scenario: Cart & Mini-cart: Apply coupon code
    Given Given I have at least one item in my cart
    When I perform "cart.apply_coupon" with params:
      """
      {
  "code": "WELCOME10"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then totals reflect the coupon"
}
      """
    Then Scenario 'Apply coupon code' completes successfully

