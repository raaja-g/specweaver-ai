### Web UI and Backend API

#### Goals
- Upload/compose requirements and preview parsed graphs/test cases.
- Human-in-the-loop approval of generated BDD tests before persistence.
- Dashboard with QA metrics and trends (pass rate, AC coverage, flakiness, time-to-green).
- Trigger and monitor test runs; view reports.
 - Domain-agnostic UX with optional Domain Pack selection; defaults to core engine.

#### UI Pages
- Dashboard: KPIs, trend charts, recent runs, flaky test list.
- Create Requirement: upload markdown/gherkin or compose inline; submit for parsing/generation.
- Review & Approve: side-by-side Requirement Graph, generated test cases, and Gherkin; approve per test or bulk.
- Runs: queue new run, filter by tag/suite/mode; live status; link to reports; toggles for `uiMode` and `apiMode` with defaults UI=real, API=mock.

#### API Endpoints (FastAPI, OpenAPI-described)
- POST /requirements: upload/compose story; returns draft artifact ids.
- POST /requirements/{id}/generate?coverage=basic|comprehensive&domain=<pack|none>: produce graph and cases with optional Domain Pack.
- POST /requirements/{id}/approve: persist and commit features/steps/tests.
- POST /runs: trigger run with params {suite/tags, uiMode: real|mock, apiMode: mock|stub|real}.
- GET /runs/{id}: status + links to reports.
- GET /metrics: aggregated KPIs for dashboard.

#### Storage & Structure
- On approval, write:
  - `artifacts/{id}/requirement_graph.json`
  - `artifacts/{id}/test_cases.json`
  - `features/{id}/*.feature`
  - `tests/steps/{id}/*_steps.py`
  - `tests/generated/test_{id}_*.py`
- Commit with metadata (provider provenance, versions, traceability) for audit.

#### Execution Modes
- `mock`: UI route mocking and API stubs (Prism/WireMock); stable fast runs.
- `stub`: upstream read-only, selected endpoints mocked.
- `real`: full integration; gated by policy.

#### Metrics Ingestion
- Parse pytest/Allure results; compute KPIs (pass rate, duration, flaky rate).
- Persist time-series for dashboard charts.

#### Security & Governance
- AuthN: local dev simple token; prod-ready pluggable provider.
- AuthZ: approve/write actions gated; audit logs for reviews and runs.
- Rate limiting for generation endpoints.


