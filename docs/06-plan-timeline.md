### Plan & Timeline (robust)

Phase 1 (Day 1):
- Scaffold repo, schemas, templates, provider orchestrator.
- Parsing prompt, LLM integration, schema validation, generation heuristics (BDD).
- Code synthesis to pytest-bdd/Playwright/HTTPX, fixtures, mocks/stubs wiring; run on mocks.

Acceptance criteria:
- JSON schemas validated; sample story produces `requirement_graph.json` and `test_cases.json`.
- At least 1 UI and 1 API BDD scenario generated and runnable in mock mode.

Phase 2 (Days 2–3):
- UI/API skeleton: upload/compose requirement, HIL review screen, run trigger endpoint.
- Dashboard MVP: ingest Allure JSON; show pass rate, AC coverage, flakiness, trends.
- Storage automation: commit generated features/steps/tests to repo structure with metadata.
 - n8n prototype: model the agent graph with HIL nodes; connect API webhooks.

Acceptance criteria:
- UI supports upload/compose, preview artifacts, approval; toggles for uiMode/apiMode.
- Runs can be triggered from UI; results visible in dashboard (latest run).
- Auto-commit approved artifacts to repo structure.

Phase 3 (Days 4–5):
- MCP server integration hardening; add run-tests tool with streaming logs.
- Reuse-first scanner across existing tests; configurable override.
- Self-healing proposal engine and artifact outputs.
 - n8n hardening: idempotency, retries, and run history persisted.
 - Auto-PR pipeline: branch naming, commit strategy, PR template, and status checks wiring.

Acceptance criteria:
- MCP tools cover parse/generate/synthesize/run/validate.
- Reuse scanner prevents duplicate test generation in this repo.
- Self-heal suggestions stored and can be auto-applied behind review -> PR.
- Auto-PR opens with links to Allure and artifacts after a passing local run.

Phase 4 (Day 6+):
- Scalability and resilience: background workers, retries, observability.
- Advanced metrics: mutation score (API), selector confidence, time-to-green SLA.

Acceptance criteria:
- Historical metrics persisted; trend charts present.
- Retry policies and health checks in place; SLOs documented.

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

#### Risks & Mitigations
- LLM variance: strict schemas, repair loop, hybrid routing; unit tests around prompts.
- Selector drift: self-heal proposals and review gates; locator repo governance.
- Flakiness: mock-first default, timeouts stabilization, network stubbing; quarantine flaky tests.
- Secrets leakage: Gitleaks in CI; local .env gitignored; AWS Secrets Manager in prod.
- Performance: batch generation; caching embeddings; split long runs.
