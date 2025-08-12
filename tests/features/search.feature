@search
Feature: test the application

  Scenario: [P3] Using the browser back button after order placement does not allow re-submission
    Given I have successfully placed an order and am on the confirmation page
    When I click the browser's back button
    Then I am taken to my empty shopping cart or an expired page
    And I cannot resubmit the same order from the previous state

