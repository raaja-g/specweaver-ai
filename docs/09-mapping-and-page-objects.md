### Mapping and Page Objects

- Locator repository maps semantic actions to selectors and steps.

Example actions:
- go_to_checkout: click #cart-icon; click text=Checkout
- enter_payment(card): fill #card-number; fill #expiry; fill #cvv
- place_order: click button:has-text(Place order)

- API mapping via OpenAPI for endpoints, auth, and payload schemas.

#### Locator Repository (YAML example)

```yaml
version: 1
pages:
  product:
    add_to_cart:
      - click: "text=Add to cart"
  cart:
    open:
      - click: "#cart-icon"
    checkout:
      - click: "text=Checkout"
  checkout:
    enter_address:
      - fill: { selector: "#address-line1", value: "{{address.line1}}" }
      - fill: { selector: "#city", value: "{{address.city}}" }
      - fill: { selector: "#zip", value: "{{address.zip}}" }
    enter_payment:
      - fill: { selector: "#card-number", value: "{{payment.cardNumber}}" }
      - fill: { selector: "#expiry", value: "{{payment.expiry}}" }
      - fill: { selector: "#cvv", value: "{{payment.cvv}}" }
    place_order:
      - click: "button:has-text('Place order')"
```

Resolution rules:
- `action` uses the `page.action` dot-notation from test steps.
- Template variables `{{...}}` are replaced from step `params` at render-time.
- Keep selectors stable; proposals for alternates are stored for review, not auto-applied.
 - Self-healing: when a selector fails, capture DOM snapshot and propose alternatives ranked by similarity; write suggestions to `artifacts/self_heal_suggestions.json` for review.

#### API Mapping

- For each `operationId` in OpenAPI, generate a canonical step name (e.g., `orders.create`) and parameter schema.
- Validate responses against the referenced schema; support Prism/WireMock for mock/stub execution modes.
