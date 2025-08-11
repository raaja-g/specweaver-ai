### Proposed Technology Stack

- Core: Python 3.11+, pytest, Playwright, Jinja2, Pydantic
- NLP/AI: Primary Groq (Llama 3.x variants), fallback Gemini 1.5, fallback Cursor CLI, fallback OpenAI; spaCy
- Storage: Git, JSON/YAML artifacts, optional vector DB (FAISS/Chroma)
- Reporting: Allure or pytest-html; CI: GitHub Actions; Docker for reproducibility
 - CLI: Typer
 - DevX/Quality: ruff, black, mypy, pytest-sugar
 - Schema/Validation: jsonschema, Pydantic v2; optional datamodel-code-generator
 - MCP: Model Context Protocol server (stdio/WebSocket), ide clients (Cursor)
 - Containerization: Docker Desktop for local MCP server
 - BDD: pytest-bdd, Gherkin feature files, Allure BDD integration
 - API: httpx/requests; schema validation via OpenAPI (prance/jsonschema)
 - Stubs/Mocks: WireMock (HTTP), Prism (OpenAPI mock), Playwright route mocking for UI
 - Web UI: FastAPI + Jinja2 or React frontend; Tailwind for styling; Chart.js for dashboards
 - Backend API: FastAPI (OpenAPI-first), Celery/RQ for workers, Redis for queue, SQLite/Postgres for results
 - Observability: Prometheus metrics, basic logs; Allure results ingestion
 - Orchestration: n8n (self-hosted) for agent workflows and human checkpoints
 - Domain Abstraction: Domain Pack plugin interface (YAML/JSON + Python hooks)

#### Justification
- Python: rich ecosystem for testing, NLP, templating.
- Playwright+pytest: reliable, parallel E2E with fixtures.
- Jinja2+schemas: deterministic, maintainable codegen.
- Groq first: fast, low-latency LLM inference for iterative parsing/generation.
- Gemini fallback: strong reasoning and long-context support.
- Cursor CLI fallback: leverages IDE-local capabilities when online providers fail.
- OpenAI fallback: widely available, stable APIs.
- spaCy: deterministic enrichments (NER/Deps) complement LLMs.
 - Typer: simple, type-safe CLI for developer ergonomics.
 - ruff/black/mypy: fast linting/formatting and static typing for reliability.
 - jsonschema/Pydantic: strict validation and clear error reporting.
 - pytest-bdd: readable, living documentation; step reuse and backgrounds for dependencies.
 - WireMock/Prism: reliable local mocks/stubs; switchable per environment.
 - Playwright route mocking: fast UI-layer test doubles without external services.
 - FastAPI: modern, type-safe API with built-in OpenAPI and easy async handling.
 - Celery/RQ + Redis: background job processing for long test runs.
 - Chart.js: simple, effective charts for QA metrics and trends.
 - n8n: visual, extensible workflow engine to compose agents, approvals, and external tools; easy Docker deployment.
 - Domain Pack plugins: allow swapping domain-specific enrichments without changing the core engine.
