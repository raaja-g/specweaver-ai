Feature: test the e-commerce website functionality
  As a tester
  I want test the e-commerce website functionality
  So that ensure the website works correctly for users

  Background:
    Given the test environment is configured
    And execution mode is set to "real" for UI and "mock" for API

  @P1 @negative @e-commerce_core_functionality @negative @scenario  Scenario: E-commerce Core Functionality: Handle invalid actions gracefully
    Given Given I am on the e-commerce website
    When I perform "user.action" with params:
      """
      {
  "description": "When I perform an invalid action"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then I see appropriate error handling"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "And the system remains stable"
}
      """
    Then Scenario 'Handle invalid actions gracefully' completes successfully

