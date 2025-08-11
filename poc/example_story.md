### Sample User Story

As a registered user, I want to add a product to my cart and complete checkout using a valid credit card so that I can place an order.

#### Acceptance Criteria
- Given I’m logged in, when I add an in-stock product to cart and checkout with valid payment and address, then order succeeds and confirmation is shown.
- Promo code works if valid; shows error if invalid.
- If stock is 0, cannot add to cart; shows ‘Out of stock’.
