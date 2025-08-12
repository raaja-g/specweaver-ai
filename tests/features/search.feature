Feature: ecommerce website https://luma.enablementadobe.com/content/luma/us/en.html
  As a user
  I want ecommerce website https://luma.enablementadobe.com/content/luma/us/en.html
  So that meet their requirements

  Background:
    Given the test environment is configured
    And execution mode is set to "real" for UI and "mock" for API

  @P0 @positive @search @positive @scenario_outline  Scenario: Search: Execute keyword search
    Given Given I am on any page with a search input
    When I perform "search.execute" with params:
      """
      {
  "query": "\u003cquery\u003e"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then I see results relevant to \"\u003cquery\u003e\""
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "And the total result count is displayed"
}
      """
    Then Scenario 'Execute keyword search' completes successfully

  @P0 @positive @search @positive @scenario  Scenario: Search: No-results state
    Given Given I am on any page with a search input
    When I perform "search.execute" with params:
      """
      {
  "query": "zzzxxyy"
}
      """
    When I perform "user.action" with params:
      """
      {
  "description": "Then I see a friendly no results message"
}
      """
    Then Scenario 'No-results state' completes successfully

