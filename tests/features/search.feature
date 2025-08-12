@search
Feature: test the application

  Scenario: Filter resources by type
    Given I am on the Resources page
    When I click the 'Webinars' filter button
    Then the list of content should update to show only webinars
    And each item in the list should have a 'Webinar' tag

  Scenario: Search for specific topics within the Resource center [1]
    Given I am on the Resources page
    When I enter "churn" into the search bar and press Enter
    Then I should see a list of results related to "churn"
    And the top result title should contain the word "Churn"

  Scenario: Search for specific topics within the Resource center [2]
    Given I am on the Resources page
    When I enter "saas metrics" into the search bar and press Enter
    Then I should see a list of results related to "saas metrics"
    And the top result title should contain the word "SaaS"

  Scenario: Search for specific topics within the Resource center [3]
    Given I am on the Resources page
    When I enter "dunning" into the search bar and press Enter
    Then I should see a list of results related to "dunning"
    And the top result title should contain the word "Dunning"

