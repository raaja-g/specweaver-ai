@search
Feature: test the application
  As a tester
  I want test the application
  So that ensure quality and functionality

  Background:
    Given the site is available
    And I start a clean browser session

  @P0 @positive @search @positive @scenario_outline  Scenario: Execute keyword search
    When I search for "<query>"
    Then I see results relevant to "<query>"
    And the total result count is displayed

  @P0 @positive @search @positive @scenario  Scenario: No-results state
    When I search for "zzzxxyy"
    Then I see a friendly no results message

