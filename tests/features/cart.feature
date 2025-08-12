@cart
Feature: test the e-commerce website functionality

  Scenario: Add a simple product to the cart from the category page
    Given I am viewing the 'Men/Tops' category page
    And the 'Argus All-Weather Tank' is in stock
    When I click the 'Add to Cart' button for the 'Argus All-Weather Tank'
    Then a success message 'You added Argus All-Weather Tank to your shopping cart.' is displayed
    And the cart quantity indicator updates to '1'

  Scenario: Add a configurable product to the cart from its details page
    Given I am on the product details page for 'Hero Hoodie'
    When I select size 'M' and color 'Green'
    And I click the 'Add to Cart' button
    Then the mini-cart shows 'Hero Hoodie' with size 'M' and color 'Green'
    And I see a confirmation message for adding the item

  Scenario: Update item quantity in the shopping cart page
    Given I have a 'Quest Lumaflex™ Band' with quantity 1 in my cart
    When I navigate to the shopping cart page
    And I change the quantity for 'Quest Lumaflex™ Band' to '3'
    And I click the 'Update Shopping Cart' button
    Then the subtotal for 'Quest Lumaflex™ Band' should be three times its unit price
    And the cart grand total is updated accordingly

  Scenario: Remove an item from the cart
    Given I have 'Push It Messenger Bag' and 'Hero Hoodie' in my cart
    When I view the shopping cart page
    And I click the 'Remove' icon for the 'Push It Messenger Bag'
    Then the 'Push It Messenger Bag' is no longer listed in the cart
    And the cart grand total is updated to reflect only the 'Hero Hoodie'

  Scenario: Attempt to add a product without selecting required options
    Given I am on the product details page for 'Radiant Tee' which requires size and color
    When I click the 'Add to Cart' button without selecting a size or color
    Then I see a validation message 'This is a required field.' next to the size and color options
    And the item is not added to the cart

  Scenario: Attempt to register with an existing email address
    Given an account already exists for 'existing.user@example.com'
    When I try to create a new account using the email 'existing.user@example.com'
    Then I see an error message 'There is already an account with this email address.'
    And I remain on the registration page

  Scenario: Login with an invalid email address format [1]
    Given I am on the customer login page
    When I enter 'plainaddress' in the email field and any password
    And I click the 'Sign In' button
    Then I see a client-side validation message 'Please enter a valid email address (Ex: johndoe@domain.com).'

  Scenario: Login with an invalid email address format [2]
    Given I am on the customer login page
    When I enter '@missingusername.com' in the email field and any password
    And I click the 'Sign In' button
    Then I see a client-side validation message 'Please enter a valid email address (Ex: johndoe@domain.com).'

  Scenario: Login with an invalid email address format [3]
    Given I am on the customer login page
    When I enter 'username@.com' in the email field and any password
    And I click the 'Sign In' button
    Then I see a client-side validation message 'Please enter a valid email address (Ex: johndoe@domain.com).'

  Scenario: Apply a valid promotional code in the cart
    Given I have items in my shopping cart totaling over $50.00
    And a valid 10% discount code 'LUMA10' exists
    When I expand the 'Apply Discount Code' section in the cart
    And I enter 'LUMA10' and click 'Apply Discount'
    Then a success message is shown
    And the cart summary displays a 'Discount' row with the correct calculated amount
    And the order total is reduced

  Scenario: Remove an applied promotional code
    Given I have successfully applied the discount code 'LUMA10' to my cart
    When I click the 'Cancel' link next to the applied discount code
    Then the 'Discount' row is removed from the cart summary
    And the order total reverts to the original amount

  Scenario: Add a new address to the address book
    Given I am logged in and on the 'Address Book' page
    When I click 'Add New Address'
    And I fill in the form with valid details for a new address, e.g., 'Work Office'
    And I click 'Save Address'
    Then I am redirected back to the 'Address Book' page
    And the newly added 'Work Office' address is listed

  Scenario: Edit an existing address
    Given I have a saved 'Home' address in my address book
    When I click 'Edit Address' for my 'Home' address
    And I update the street address from '123 Main St' to '456 Oak Ave'
    And I click 'Save Address'
    Then the address book shows the updated street '456 Oak Ave' for my 'Home' address

  Scenario: Change the default billing address
    Given I have two addresses, 'Home' and 'Work', and 'Home' is the default billing address
    When I navigate to the 'Address Book' page
    And I click 'Change Billing Address' and select the 'Work' address
    And I save the change
    Then the 'Work' address is now marked as the 'Default Billing Address'

  Scenario: Delete an address from the address book
    Given I have an old address 'Previous Apartment' that I no longer use
    When I am on the 'Address Book' page
    And I click 'Delete Address' for the 'Previous Apartment'
    And I confirm the deletion in the popup dialog
    Then the 'Previous Apartment' address is no longer listed in my address book

  Scenario: Add an item to the wishlist
    Given I am a logged-in user viewing the 'Strive Endurance Fleece' product page
    When I click the 'Add to Wish List' button
    Then I see a success message 'Strive Endurance Fleece has been added to your Wish List.'
    And I am redirected to my 'My Wish List' page

  Scenario: View items in the wishlist
    Given I have previously added 'Hero Hoodie' and 'Push It Messenger Bag' to my wishlist
    When I navigate to my 'My Wish List' page
    Then I see both 'Hero Hoodie' and 'Push It Messenger Bag' listed
    And I can see their price and an 'Add to Cart' button for each

  Scenario: Remove an item from the wishlist
    Given my wishlist contains 'Strive Endurance Fleece'
    When I am on my 'My Wish List' page
    And I click the 'Remove item' (X) icon for 'Strive Endurance Fleece'
    And I confirm the action
    Then 'Strive Endurance Fleece has been removed from your Wish List.' message is displayed
    And the item is no longer on the page

  Scenario: Add an item from the wishlist to the cart
    Given my wishlist contains 'Quest Lumaflex™ Band'
    When I am on my 'My Wish List' page
    And I click 'Add to Cart' for 'Quest Lumaflex™ Band'
    Then the item is added to my shopping cart
    And the cart quantity indicator updates

  Scenario: Guest user cannot add item to wishlist
    Given I am a guest user viewing a product page
    When I click the 'Add to Wish List' button
    Then I am redirected to the login page

  Scenario: Product page displays 'In Stock' for available items
    Given the 'Hero Hoodie' has a stock level greater than 0
    When a shopper views the 'Hero Hoodie' product page
    Then the availability status is displayed as 'In Stock'
    And the 'Add to Cart' button is enabled

  Scenario: Product page displays 'Out of Stock' for unavailable items
    Given the 'Phoebe Zipper Sweatshirt' has a stock level of 0
    When a shopper views the 'Phoebe Zipper Sweatshirt' product page
    Then the availability status is displayed as 'Out of Stock'
    And the 'Add to Cart' button is disabled or hidden

  Scenario: API check prevents adding out-of-stock item to cart
    Given the 'Phoebe Zipper Sweatshirt' (SKU `WS09`) is out of stock
    When a user attempts to add SKU `WS09` to the cart via a direct API call
    Then the API should return an error response with status code 4xx
    And the response body should contain a message like 'The requested qty is not available'
    And the user's cart remains unchanged

  Scenario: Attempt to subscribe with an invalid email address
    Given I am on any page with the newsletter subscription form
    When I enter 'invalid-email' into the form
    And I click 'Subscribe'
    Then I see a client-side validation error 'Please enter a valid email address.'

