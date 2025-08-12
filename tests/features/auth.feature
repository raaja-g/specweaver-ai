@auth
Feature: test the e-commerce website functionality

  Scenario: Successful new account registration
    Given I am a new user on the 'Create New Customer Account' page
    When I enter 'Jane', 'Doe', a unique email like 'jane.doe.12345@example.com', and a strong password 'ValidPass123!'
    And I confirm the password 'ValidPass123!'
    And I click the 'Create an Account' button
    Then I am redirected to the 'My Account' dashboard
    And I see a success message 'Thank you for registering with Main Website Store.'

  Scenario: Attempt to register with mismatched passwords
    Given I am on the 'Create New Customer Account' page
    When I enter my personal information and the password 'ValidPass123!'
    And I enter a different password 'Mismatched456!' in the confirmation field
    And I click 'Create an Account'
    Then I see an error message 'Please enter the same value again.' below the password confirmation field
    And my account is not created

  Scenario: Attempt to register with invalid field data [1]
    Given I am on the account registration page
    When I fill the 'Email' with 'not-an-email' and submit the form
    Then I should see the validation error message 'Please enter a valid email address (Ex: johndoe@domain.com).'

  Scenario: Attempt to register with invalid field data [2]
    Given I am on the account registration page
    When I fill the 'Password' with 'short' and submit the form
    Then I should see the validation error message 'Minimum length of this field must be equal or greater than 8 symbols.'

  Scenario: Attempt to register with invalid field data [3]
    Given I am on the account registration page
    When I fill the 'First Name' with '' and submit the form
    Then I should see the validation error message 'This is a required field.'

  Scenario: Attempt to register with invalid field data [4]
    Given I am on the account registration page
    When I fill the 'Last Name' with '' and submit the form
    Then I should see the validation error message 'This is a required field.'

  Scenario: Successful login with valid credentials
    Given I am a registered user with email 'jane.doe.12345@example.com' and password 'ValidPass123!'
    When I navigate to the Login page
    And I enter my email and password
    And I click the 'Sign In' button
    Then I am redirected to the 'My Account' page
    And the page header shows 'Welcome, Jane Doe!'

  Scenario: User logs out successfully
    Given I am logged in as 'Jane Doe'
    When I click the dropdown arrow next to my name in the header
    And I select the 'Sign Out' option
    Then I am redirected to the 'You are signed out' page
    And the header no longer shows my name

  Scenario: Login with an invalid password
    Given I am a registered user
    When I attempt to log in with my correct email and an incorrect password
    Then I see an error message 'The account sign-in was incorrect or your account is disabled temporarily. Please wait and try again later.'
    And I remain on the Login page

  Scenario: Registered user manages subscription from account dashboard
    Given I am a logged-in user who is subscribed to the newsletter
    When I navigate to the 'Newsletter Subscription' section of my account
    And I uncheck the 'General Subscription' box
    And I click 'Save'
    Then I see a success message 'The subscription has been saved.'
    And my subscription status is updated to 'not subscribed'

