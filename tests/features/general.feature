@general
Feature: test the application
  As a tester
  I want test the application
  So that ensure quality and functionality

  Background:
    Given the site is available
    And I start a clean browser session

  @P0 @positive @homepage_&_global_navigation @positive @scenario  Scenario: Render homepage for a first-time visitor
    When I open the homepage
    Then I see the cookie consent banner
    And I see the primary navigation and search

  @P0 @positive @homepage_&_global_navigation @positive @scenario  Scenario: Accept cookie consent
    Given I have not previously set consent
    When I accept cookies
    Then my consent is recorded

  @P0 @positive @homepage_&_global_navigation @positive @scenario_outline  Scenario: Navigate to category
    When I select the "<category>" menu item
    Then I land on the "<expected_page>" listing page

  @P1 @negative @auto @negative  Scenario: Input validation - empty required field
    Given I am on the form page
    When I submit the form with an empty required field
    Then I see an inline error explaining what is required

  @P1 @negative @auto @negative  Scenario: Expired coupon is rejected
    Given I have a coupon that is expired
    When I apply the coupon
    Then I see a message that the coupon is no longer valid

  @P3 @edge @auto @edge  Scenario: Slow network retry
    Given the network is slow
    When I submit an action that supports retry
    Then the client retries and completes without duplicate side-effects

  @P1 @negative @auto @negative  Scenario: Input validation - empty required field
    Given I am on the form page
    When I submit the form with an empty required field
    Then I see an inline error explaining what is required

  @P1 @negative @auto @negative  Scenario: Expired coupon is rejected
    Given I have a coupon that is expired
    When I apply the coupon
    Then I see a message that the coupon is no longer valid

  @P3 @edge @auto @edge  Scenario: Slow network retry
    Given the network is slow
    When I submit an action that supports retry
    Then the client retries and completes without duplicate side-effects

  @P1 @negative @auto @negative  Scenario: Input validation - empty required field
    Given I am on the form page
    When I submit the form with an empty required field
    Then I see an inline error explaining what is required

  @P1 @negative @auto @negative  Scenario: Expired coupon is rejected
    Given I have a coupon that is expired
    When I apply the coupon
    Then I see a message that the coupon is no longer valid

  @P3 @edge @auto @edge  Scenario: Slow network retry
    Given the network is slow
    When I submit an action that supports retry
    Then the client retries and completes without duplicate side-effects

  @P1 @negative @auto @negative  Scenario: Input validation - empty required field
    Given I am on the form page
    When I submit the form with an empty required field
    Then I see an inline error explaining what is required

  @P1 @negative @auto @negative  Scenario: Expired coupon is rejected
    Given I have a coupon that is expired
    When I apply the coupon
    Then I see a message that the coupon is no longer valid

  @P3 @edge @auto @edge  Scenario: Slow network retry
    Given the network is slow
    When I submit an action that supports retry
    Then the client retries and completes without duplicate side-effects

  @P1 @negative @auto @negative  Scenario: Input validation - empty required field
    Given I am on the form page
    When I submit the form with an empty required field
    Then I see an inline error explaining what is required

  @P1 @negative @auto @negative  Scenario: Expired coupon is rejected
    Given I have a coupon that is expired
    When I apply the coupon
    Then I see a message that the coupon is no longer valid

