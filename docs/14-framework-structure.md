### Framework Structure & Organization

#### Repository Layout
```
specweaver-ai/
├── features/                    # BDD feature files
│   ├── api/                    # API test features
│   │   └── orders/
│   │       └── create_order.feature
│   └── ui/                     # UI test features
│       └── checkout/
│           └── guest_checkout.feature
├── tests/
│   ├── steps/                  # Step definitions
│   │   ├── api/
│   │   │   └── api_steps.py
│   │   └── ui/
│   │       └── ui_steps.py
│   ├── fixtures/               # Shared fixtures
│   │   ├── auth.py
│   │   └── data.py
│   └── generated/              # Auto-generated tests
│       └── test_checkout_*.py
├── artifacts/                   # Generation artifacts
│   ├── {story-id}/
│   │   ├── requirement_graph.json
│   │   ├── test_cases.json
│   │   └── self_heal_suggestions.json
│   └── reports/                # Test reports
│       └── allure/
├── locators/                    # UI element mappings
│   └── locator-repo.yml
├── api/                         # OpenAPI specs
│   └── openapi.yml
├── domain-packs/                # Optional domain extensions
│   └── ecommerce/
│       ├── intents.yml
│       └── templates/
├── config/                      # Configuration
│   ├── .env.example
│   ├── pytest.ini
│   └── execution-modes.yml
├── docker/                      # Docker configs
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── mcp/                         # MCP server
│   ├── server.py
│   └── tools/
├── ui/                          # Web UI (React)
│   ├── src/
│   └── package.json
├── api/                         # Backend API (FastAPI)
│   ├── app.py
│   └── routers/
└── n8n/                         # Workflow definitions
    └── workflows/
        └── test-generation.json
```

#### Naming Conventions
- Features: `{domain}_{action}.feature` (e.g., `checkout_guest.feature`)
- Step files: `{layer}_steps.py` (e.g., `ui_steps.py`, `api_steps.py`)
- Test IDs: `TC-{DOMAIN}-{SEQ}` (e.g., `TC-CHK-001`)
- Branches: `feature/tests/{story-id}-{slug}`
- Artifacts: timestamped and story-id indexed

#### Test Organization
- Group by layer (UI/API) then by domain/module
- Shared steps in common files
- Domain-specific steps in dedicated files
- Fixtures for cross-cutting concerns (auth, data, mocks)

#### Versioning Strategy
- Artifacts include schema version and prompt version
- Migration scripts for schema changes
- Backward compatibility for at least 2 versions
