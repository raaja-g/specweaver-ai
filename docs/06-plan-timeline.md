### Plan & Timeline (robust)

Phase 1 (Day 1):
- Scaffold repo, schemas, templates, provider orchestrator.
- Parsing prompt, LLM integration, schema validation, generation heuristics (BDD).
- Code synthesis to pytest-bdd/Playwright/HTTPX, fixtures, mocks/stubs wiring; run on mocks.

Phase 2 (Days 2–3):
- UI/API skeleton: upload/compose requirement, HIL review screen, run trigger endpoint.
- Dashboard MVP: ingest Allure JSON; show pass rate, AC coverage, flakiness, trends.
- Storage automation: commit generated features/steps/tests to repo structure with metadata.
 - n8n prototype: model the agent graph with HIL nodes; connect API webhooks.

Phase 3 (Days 4–5):
- MCP server integration hardening; add run-tests tool with streaming logs.
- Reuse-first scanner across existing tests; configurable override.
- Self-healing proposal engine and artifact outputs.
 - n8n hardening: idempotency, retries, and run history persisted.
 - Auto-PR pipeline: branch naming, commit strategy, PR template, and status checks wiring.

Phase 4 (Day 6+):
- Scalability and resilience: background workers, retries, observability.
- Advanced metrics: mutation score (API), selector confidence, time-to-green SLA.

#### Decisions (confirmed)
- Domain/flows: Domain and workflow agnostic (use Domain Packs optionally).
- LLM: Cloud LLMs with fallback order Groq → Gemini → Cursor CLI → OpenAI.
- Coverage level for POC: comprehensive.
- Target demo environment (UI): https://luma.enablementadobe.com/content/luma/us/en.html
- Default execution mode: API=mock, UI=real.
- Self-healing: auto-apply behind review (apply after approval with diff).
- Reuse scope: scan this repository’s test structure first; reuse preferred in-place.
- Web UI stack: FastAPI backend + React (SPA) frontend.
- Results store: file-based Allure JSON for current runs + DB-backed metrics for trends.
