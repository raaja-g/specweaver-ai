### Governance & Quality

- Determinism: schemas + templates; LLM outputs validated/corrected.
- Guardrails: token/size limits, similarity checks, unit tests for generators.
- Metrics: coverage vs ACs, mutation score (API), flakiness, time-to-green.
- Auto-heal: propose selector alternatives; require review for changes.

#### LLM Orchestration Policy

- Provider order: Groq → Gemini → Cursor CLI → OpenAI.
- Record provenance: provider, model, temperature, prompt version embedded in artifacts.
- Retry & backoff: bounded attempts per provider; fast-fail on repeated schema violations.
- Cost/latency budget: prefer Groq (low latency) for iterative steps; fall back only when errors occur or capability is insufficient.

#### MCP Operational Quality

- Health endpoints for IDE: readiness/liveness probes; tool discovery.
- Deterministic tool I/O: strict JSON schemas for MCP tool inputs/outputs.
- Versioned tools: include `mcpToolVersion` and `schemaVersion` in responses.
 - Reuse-first rule: block generation when an equivalent existing test is detected, unless explicitly overridden. Emit trace links to reused tests.
 - Mode discipline: enforce `uiMode`/`apiMode` policies per branch/CI to avoid accidental real env usage; UI must surface current mode clearly.

#### UI HIL & Audit

- Require explicit human approval in UI before persisting generated tests.
- Keep an immutable audit log of prompts, artifacts, approvals, and provider provenance.
- Show diffs in the UI for re-generation; require sign-off before write.

#### Agentic Governance

- Agent roles have explicit contracts and metrics (success, latency, escalation rate).
- Handoffs are logged with context; failures trigger fallback or human escalation in n8n.
- Workflows are versioned; only approved versions run in CI.

#### SCM & PR Policy
- Auto-PR is allowed only when local run passes in the selected `executionMode` and docs-lint succeeds locally.
- Branch naming: `feature/tests/<story-id>-<slug>`; PR includes links to Allure report and artifacts.
- Require at least one reviewer and the docs-lint workflow to pass before merge.
