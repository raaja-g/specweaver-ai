Feature: test the e-commerce website functionality
  As a tester
  I want test the e-commerce website functionality
  So that ensure the website works correctly for users

  Background:
    Given the test environment is configured
    And execution mode is set to "real" for UI and "mock" for API

  @P0 @positive @e-commerce_core_functionality @positive @scenario  Scenario: E-commerce Core Functionality: Add product to cart
    Given Given I am on the e-commerce website
    When I perform "cart.add_item" with params:
      """
      {
  "button": "Add to Cart"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then the product is added to my cart"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "And the cart count updates"
}
      """
    Then Scenario 'Add product to cart' completes successfully

