@general
Feature: test the e-commerce website functionality

  Scenario: View all details of a simple product
    Given I am on the product details page for 'Push It Messenger Bag'
    Then I can see the product name 'Push It Messenger Bag'
    And I can see its price, SKU 'WB04', and 'In Stock' status
    And I can see a detailed product description and additional information

  Scenario: View available options for a configurable product
    Given I am viewing the 'Strive Endurance Fleece'
    Then I can see selectable options for 'Size' including 'XS', 'S', 'M', 'L', 'XL'
    And I can see selectable options for 'Color' including 'Black', 'Blue', 'Orange'

  Scenario: Image gallery functionality
    Given I am viewing the 'Hero Hoodie' which has multiple images
    When I click on a thumbnail image
    Then the main product image updates to show the selected thumbnail's image

  Scenario: View customer reviews for a product
    Given I am on the product details page for a product with existing reviews
    When I click on the 'Reviews' tab
    Then I can see a list of reviews with ratings, author, and comments

  Scenario: Attempt to apply an invalid or expired promotional code
    Given I have items in my shopping cart
    When I enter an invalid code 'INVALIDCODE123' and click 'Apply Discount'
    Then an error message 'The coupon code "INVALIDCODE123" is not valid.' is displayed
    And the order total remains unchanged

  Scenario: Attempt to apply a promotional code that does not meet criteria [1]
    Given a promotion 'FREESHIP' exists with the requirement 'Order total must be over $100'
    And my cart does not meet this requirement
    When I try to apply the code 'FREESHIP'
    Then I see an error message 'The coupon code "FREESHIP" is not valid.'
    And the discount is not applied

  Scenario: Attempt to apply a promotional code that does not meet criteria [2]
    Given a promotion 'TEE20' exists with the requirement 'Cart must contain an item from the 'Tees' category'
    And my cart does not meet this requirement
    When I try to apply the code 'TEE20'
    Then I see an error message 'The coupon code "TEE20" is not valid.'
    And the discount is not applied

  Scenario: Submit a product review successfully
    Given I am a logged-in user viewing the product page for 'Hero Hoodie'
    When I click on the 'Add Your Review' link
    And I select a 5-star rating
    And I enter my nickname as 'HappyShopper'
    And I enter the summary 'Great Hoodie!' and the review 'Very comfortable and warm.'
    And I click 'Submit Review'
    Then I see a confirmation message 'You submitted your review for moderation.'

  Scenario: Attempt to submit a review without a rating
    Given I am a logged-in user on the review form for a product
    When I fill in all fields except for the star rating
    And I click 'Submit Review'
    Then I see a validation error message asking me to select a rating
    And the review is not submitted

  Scenario: Attempt to submit a review without a review text
    Given I am on the review form for a product
    When I select a rating but leave the 'Review' text field empty
    And I click 'Submit Review'
    Then I see a validation error 'This is a required field.' for the review text area
    And the review is not submitted

  Scenario: Guest user is prompted to log in to write a review
    Given I am a guest user viewing the 'Radiant Tee' product page
    And I see the 'Be the first to review this product' link
    When I click the link to add a review
    Then I am prompted with 'Only registered users can write reviews. Please Sign in or create an account'

  Scenario: Subscribe with a valid email from the footer
    Given I am a visitor on the homepage
    When I enter a valid email 'new.subscriber@example.com' into the newsletter subscription form in the footer
    And I click the 'Subscribe' button
    Then I see a success message 'Thank you for your subscription.'

  Scenario: Attempt to subscribe with an already subscribed email
    Given the email 'already.subscribed@example.com' is already in the subscription list
    When I try to subscribe again with 'already.subscribed@example.com'
    Then I see a message 'This email address is already subscribed.'

