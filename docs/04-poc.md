### Proof of Concept (POC)

#### Goal
Take a sample user story and produce validated `requirement_graph.json` and `test_cases.json`; optionally synthesize Playwright tests.

#### Directory Layout

```
poc/
  parse_and_generate.py     # CLI: parse story -> graph -> cases
  codegen.py                # Optional: render pytest+Playwright
  schemas.py                # Pydantic models
  templates/
    test_pytest_playwright.j2
    steps_ui_playwright.j2
    steps_api_httpx.j2
  features/
    checkout.feature
  ui/
    app.py                 # FastAPI (UI + API) or separate frontend
    templates/
      dashboard.html
      hil_review.html
    static/
      app.css
  artifacts/
    requirement_graph.json
    test_cases.json
  example_story.md
requirements.txt
```

#### Dependencies

```
openai
pydantic>=2
jinja2
typer
faker
pyyaml
groq
google-generativeai
httpx
pytest-bdd
prance
fastapi
uvicorn
redis
rq
celery
aiofiles
python-multipart
sqlalchemy
alembic
jinja2
python-dotenv
n8n (external docker)
```

#### Run

```
python poc/parse_and_generate.py --story poc/example_story.md --out poc/artifacts --coverage basic --provider auto
python poc/codegen.py --cases poc/artifacts/test_cases.json --locators locator-repo.yml --out tests
pytest -q -n auto --maxfail=1

# Start API/UI locally (dev)
uvicorn ui.app:app --reload --port 8080

# Optional: start n8n locally
docker run -it --rm -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
```

#### Example `test_cases.json`

```json
[
  {
    "id": "TC-CHK-001",
    "title": "Checkout succeeds with valid card and in-stock product",
    "priority": "P0",
    "type": "positive",
    "traceTo": ["AC-1"],
    "preconditions": ["user_logged_in"],
    "steps": [
      {"action": "product.add_to_cart", "params": {"sku": "SKU-123", "qty": 1}},
      {"action": "cart.open", "params": {}},
      {"action": "cart.checkout", "params": {}},
      {"action": "checkout.enter_address", "params": {"address": {"line1": "123 Main", "city": "NYC", "zip": "10001"}}},
      {"action": "checkout.enter_payment", "params": {"payment": {"cardNumber": "4242424242424242", "expiry": "12/30", "cvv": "123"}}},
      {"action": "checkout.place_order", "params": {}}
    ],
    "data": {},
    "expected": ["order_confirmation_visible", "order_id_generated"],
    "tags": ["checkout", "payment", "happy_path"]
  }
]
```

#### Notes

- Use any stable demo site for a visual run, or keep to JSON generation to avoid external dependencies.
- Embed schema and prompt versions in the artifacts for traceability.
- Provider order (auto): Groq → Gemini → Cursor CLI → OpenAI. You can force a provider via `--provider groq|gemini|cursor|openai`.

#### MCP (Docker Desktop) Quickstart

```
docker build -t specweaver-mcp .
docker run --rm -it \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e GOOGLE_API_KEY=$GOOGLE_API_KEY \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -p 8765:8765 \
  specweaver-mcp
```

Then register the MCP server in your IDE (Cursor) as a custom MCP endpoint (WebSocket or stdio bridge) and use the tools:
- `parse_requirement`, `generate_test_cases`, `synthesize_scripts`, `validate_artifacts`, `run_tests`.