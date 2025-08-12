Feature: test the e-commerce website functionality
  As a tester
  I want test the e-commerce website functionality
  So that ensure the website works correctly for users

  Background:
    Given the test environment is configured
    And execution mode is set to "real" for UI and "mock" for API

  @P0 @positive @e-commerce_core_functionality @positive @scenario  Scenario: E-commerce Core Functionality: Browse products successfully
    Given Given I am on the e-commerce website
    When I perform "navigation.goto" with params:
      """
      {
  "target": "When I navigate to the product catalog"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then I see available products"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "And I can view product details"
}
      """
    Then Scenario 'Browse products successfully' completes successfully

