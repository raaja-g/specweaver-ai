@auth
Feature: to add a product to my cart and check out with a credit card

  Scenario: [P3] Change my account password
    Given I am logged into my account
    When I go to 'Account Settings' and choose 'Change Password'
    And I enter my current password correctly
    And I enter and confirm a new valid password
    Then I see a success message 'Your password has been updated'
    And I am logged out and prompted to log in with my new password

