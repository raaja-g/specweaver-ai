# Implementation TODO

## MVP (Phase 1)
- [ ] CLI parse -> RequirementGraph (poc/parse_and_generate.py)
- [ ] Pydantic models for schemas (poc/schemas.py)
- [ ] Generate TestCases JSON from RequirementGraph (basic heuristics)
- [ ] Codegen: emit BDD feature files from TestCases (poc/codegen.py + templates)
- [ ] Sample story input (poc/example_story.md)
- [ ] Execution mode config (config/execution-modes.yml) with uiMode=real, apiMode=mock
- [ ] Sample locator repo (locators/locator-repo.yml)
- [ ] README quickstart for MVP

## Phase 2 (UI/API)
- [ ] FastAPI endpoints: requirements, generate, approve, runs, metrics
- [ ] React UI pages: dashboard, create, review/approve, runs (with uiMode/apiMode toggles)
- [ ] Persist artifacts to repo structure on approval
- [ ] Dashboard ingest of Allure JSON; display KPIs

## Phase 3 (MCP, n8n, Auto-PR)
- [ ] MCP server tools: parse, generate, synthesize, validate, run
- [ ] n8n workflow: trigger → parse → design → reuse → HIL → synthesize → local run → auto-PR
- [ ] Auto-PR script with branch naming and PR template usage
- [ ] Reuse scanner to avoid duplicate tests within repo

## Phase 4 (Scale, Quality)
- [ ] Self-healing proposals + auto-apply behind review
- [ ] Hybrid routing (local open model + cloud fallbacks)
- [ ] Historical metrics (DB schema + trends)
- [ ] CI: unit/integration tests, container scanning, deployment

## Security & Ops
- [ ] Gitleaks enforced in CI
- [ ] .env usage locally, AWS Secrets Manager in prod
- [ ] Health/readiness endpoints; basic monitoring/alerts

## Open Questions
- [ ] Provide cloud API keys (Groq, Gemini; OpenAI fallback) for real LLM runs
- [ ] Confirm access constraints to demo site (https://luma.enablementadobe.com/content/luma/us/en.html)
- [ ] Preferred DB (Postgres vs SQLite) for metrics
- [ ] AWS account details for Secrets Manager and container registry
