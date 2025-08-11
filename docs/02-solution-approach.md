### Solution Approach & Technical Design

#### Requirement Parsing
- Normalize story (title, role, goal, benefit), extract acceptance criteria, constraints.
- LLM fills a strict schema (Requirement Graph) validated by Pydantic.
 - spaCy NER/deps + rules for intents (domain-agnostic core: CRUD, auth, payments; extended via pluggable Domain Packs).
- Vector retrieval for similar past stories/examples.
 - Validation & repair loop: on schema violations, auto-issue a minimal "fix output to schema" prompt with the validator error and retry deterministically.
 - LLM strategy (hybrid):
   - Default order for cloud: Groq → Gemini → Cursor CLI → OpenAI.
   - Local first for sensitive/high-volume tasks via Ollama/vLLM (Llama 3.x). Escalate to cloud on low confidence or schema repair failures.
   - Orchestrator enforces schema/truncation and records provider provenance. Exposed via API and MCP; UI calls API.

#### Test Case Generation
- Transform graph -> condition-action-expected triples.
- Expand using decision tables, ECP/BVA, risk heuristics.
- Coverage knobs: basic/comprehensive; deduplicate via set-cover approx.
- Output JSON/YAML: id, title, priority, preconditions, steps, data, expected, tags, trace.
 - Traceability: every test case includes `traceTo: [AC-ids]`; compute an AC coverage metric and fail generation if any AC is uncovered.
 - Provider-agnostic and domain-agnostic: core heuristics (ECP/BVA, decision tables) apply to any domain; optional Domain Packs enrich with domain-specific edge cases.
 - BDD-first: emit canonical Gherkin for each test case and store under `features/`; generate step definitions in Python (pytest-bdd) that call UI/API actions. The UI shows these as a living document for HIL review/approval.
 - Reuse policy: before generating new tests, scan repository for existing equivalents (by AC trace, titles, tags) and link to them instead of creating duplicates.
 - Dependency resolution: compute inter-test dependencies (login, data seeding) and express them as shared `Background` and fixtures; order execution or mark independent via fixtures.

#### Script Generation
- Map actions to UI/API via Locator Repository (YAML) and OpenAPI.
- Jinja2 templates -> pytest + Playwright tests; fixtures for auth/data.
- Data via Faker and constraint validation.
- Selector resilience and auto-heal proposals.
 - Determinism: templates encapsulate code style; all variable parts flow from schemas. No free-form LLM output is emitted as code.
 - Offline-first: for code synthesis, prefer deterministic templating; the LLM is only used for mapping suggestions if needed and goes through the same fallback chain.
 - API tests: generate HTTPX-based step defs with contract checks (status, schema via OpenAPI) and response examples.
 - UI tests: generate Playwright step defs referencing locator repo; add self-healing suggestions recorded in artifacts when selectors fail.
 - Domain Packs: optional templates/snippets for common flows (e.g., e-commerce checkout, healthcare appointments) but core templates remain neutral.
 - Storage: after approval, commit generated features/steps/tests to repo structure automatically with metadata (traceability, versions).
 - Auto-PR: on successful local execution (all tests green in selected mode), automatically create a feature branch, commit artifacts, and open a PR with links to reports and metrics. Triggers: UI click, MCP tool, or n8n workflow completion.

#### Maintainability & Scalability
- Versioned schemas & prompts; governed locator updates.
- Stateless services; queue-based batch; caching via embeddings.
- Human-in-the-loop reviews with diffs; CI re-gen on change.
 - Change impact: when `locator-repo.yml` or OpenAPI changes, diff-resolve affected actions and re-generate only impacted tests.
 - MCP server horizontal scaling: run multiple replicas behind the IDE or CI orchestrator; stateless with shared artifact storage.
 - API/UI scaling: separate stateless API from Web UI; use background workers for long tasks; WebSocket/SSE for run status.
 - Agentic orchestration: represent the pipeline as an agent graph in n8n; each agent has a clear contract and can request help from others or external tools; HIL checkpoints are explicit nodes.
 - Mode switching: per-layer flags `uiMode` (real|mock) and `apiMode` (mock|stub|real); UI defaults UI=real, API=mock; n8n/MCP/UI can override per-run.
  - Hybrid model policy: route by sensitivity, volume, and difficulty; see Governance for examples and rules.

#### Metrics & Quality Gates

- AC coverage (100% required), duplicate-case ratio, time-to-green, flaky test rate, mutation score (API), and selector confidence.
- Block merges if coverage drops or schema validation fails.
