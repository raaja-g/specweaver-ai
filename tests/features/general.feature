Feature: Checkout any items from https://luma.enablementadobe.com/content/luma/us/en.html
  As a user
  I want Checkout any items from https://luma.enablementadobe.com/content/luma/us/en.html
  So that meet their requirements

  Background:
    Given the test environment is configured
    And execution mode is set to "real" for UI and "mock" for API

  @P0 @positive @homepage_&_global_navigation @positive @scenario  Scenario: Homepage & Global Navigation: Render homepage for a first-time visitor
    Given Given the site is available
    When I perform "user.action" with params:
      """
      {
  "description": "When I open the homepage"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then I see the cookie consent banner"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "And I see the primary navigation and search"
}
      """
    Then Scenario 'Render homepage for a first-time visitor' completes successfully

  @P0 @positive @homepage_&_global_navigation @positive @scenario  Scenario: Homepage & Global Navigation: Accept cookie consent
    Given Given the site is available
    When I perform "user.action" with params:
      """
      {
  "description": "Given I have not previously set consent"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "When I accept cookies"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then my consent is recorded"
}
      """
    Then Scenario 'Accept cookie consent' completes successfully

