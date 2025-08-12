@auth
Feature: test the application

  Scenario: Successful login with valid credentials
    When I enter my registered email "customer@example.com" into the "Email" field
    And I enter my password "Password123!" into the "Password" field
    And I click the "Log In" button
    Then I should be redirected to the account dashboard
    And I should see a welcome message with my name "John Doe"

  Scenario: Attempt to login with an incorrect password
    When I enter my registered email "customer@example.com" into the "Email" field
    And I enter an incorrect password "WrongPassword" into the "Password" field
    And I click the "Log In" button
    Then I should see an error message "Invalid email or password."
    And I should remain on the login page

  Scenario: Attempt to login with an unregistered email
    When I enter an unregistered email "nouser@example.com" into the "Email" field
    And I enter a password "SomePassword" into the "Password" field
    And I click the "Log In" button
    Then I should see an error message "Invalid email or password."

  Scenario Outline: Login form field validation
    When I enter "<Email>" into the "Email" field
    And I enter "<Password>" into the "Password" field
    And I click the "Log In" button
    Then I should see a validation error message "<ErrorMessage>"

  Examples:
    | Email | Password | ErrorMessage |
    |  | Password123! | Email is required. |
    | customer@example.com |  | Password is required. |
    | invalid-email | Password123! | Please enter a valid email address. |

  Scenario: Successful logout
    Given I am a logged-in user
    When I click the "Logout" link
    Then I should be redirected to the homepage
    And I should see a message confirming "You have been logged out."

  Scenario: Attempt to register with an existing email
    Given an account with the email "customer@example.com" already exists
    When I fill in the registration form with email "customer@example.com"
    And I click the "Create Account" button
    Then I should see an error message "An account with this email already exists."
    And I should remain on the registration page

