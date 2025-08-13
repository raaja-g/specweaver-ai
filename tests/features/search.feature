@search
Feature: to add a product to my cart and check out with a credit card

  Scenario: [P0] Search for a product by its full name
    Given I am on the homepage
    When I type 'Sony WH-1000XM5 Headphones' into the search bar and press Enter
    Then the search results page appears
    And the first result is 'Sony WH-1000XM5 Headphones'

  Scenario: [P1] Search yields no results
    Given I am on the homepage
    When I type 'asdfghjkl' into the search bar and press Enter
    Then the search results page shows a message 'No results found for "asdfghjkl".'
    And it suggests alternative search terms or popular products

  Scenario: [P2] Search results page is paginated
    Given a search for 'laptop' returns 50 results and the page size is 20
    When I perform the search
    Then I see the first 20 results on the page
    And I see pagination controls showing 'Page 1 of 3'
    When I click on '2'
    Then the page reloads with results 21-40

  Scenario: [P1] Filter search results by brand and price [1]
    Given I have searched for 'smartphone'
    When I apply the 'Brand' filter for 'Samsung'
    And I apply the 'Price' filter for '$500 - $1000'
    Then all the products displayed in the results are from 'Samsung'
    And all have a price 'between $500 and $1000'

  Scenario: [P1] Filter search results by brand and price [2]
    Given I have searched for 'smartphone'
    When I apply the 'Brand' filter for 'Apple'
    And I apply the 'Price' filter for 'Over $1000'
    Then all the products displayed in the results are from 'Apple'
    And all have a price 'over $1000'

  Scenario: [P1] Filter search results by brand and price [3]
    Given I have searched for 'smartphone'
    When I apply the 'Brand' filter for 'Google'
    And I apply the 'Price' filter for '$250 - $500'
    Then all the products displayed in the results are from 'Google'
    And all have a price 'between $250 and $500'

