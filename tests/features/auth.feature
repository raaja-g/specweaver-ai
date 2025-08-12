@auth
Feature: to add a product to my cart and check out with a credit card

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I enter my registered email 'shopper@example.com' and password 'ValidPass123!'
    And I click the 'Sign In' button
    Then I should be redirected to the account dashboard
    And I should see a welcome message 'Welcome, Jane!'

  Scenario: Login attempt with incorrect password
    Given I am on the login page
    When I enter my registered email 'shopper@example.com' and an incorrect password 'WrongPassword'
    And I click the 'Sign In' button
    Then I should remain on the login page
    And I should see an error message 'Invalid email or password. Please try again.'

  Scenario: Login attempt with a non-existent email
    Given I am on the login page
    When I enter a non-registered email 'nobody@example.com' and any password
    And I click the 'Sign In' button
    Then I should see an error message 'Invalid email or password. Please try again.'

  Scenario: Login form field validation [1]
    Given I am on the login page
    When I enter '' in the email field and 'ValidPass123!' in the password field
    And I click the 'Sign In' button
    Then I should see the validation message 'Email address is required.'
    And I should not be logged in

  Scenario: Login form field validation [2]
    Given I am on the login page
    When I enter 'shopper@example.com' in the email field and '' in the password field
    And I click the 'Sign In' button
    Then I should see the validation message 'Password is required.'
    And I should not be logged in

  Scenario: Login form field validation [3]
    Given I am on the login page
    When I enter 'invalid-email' in the email field and 'ValidPass123!' in the password field
    And I click the 'Sign In' button
    Then I should see the validation message 'Please enter a valid email address.'
    And I should not be logged in

