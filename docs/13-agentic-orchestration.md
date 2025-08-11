### Agentic Orchestration (n8n)

#### Agent Roles
- Requirement Parser Agent: normalizes and extracts Requirement Graph; schema-validated; escalates on ambiguity.
- Test Case Designer Agent: expands graph to cases with ECP/BVA; computes AC coverage; proposes BDD scenarios.
- Reuse Scanner Agent: finds existing equivalent tests and suggests reuse.
- Synthesizer Agent: maps actions to UI/API, renders features/steps/tests; obeys executionMode.
- Self-Heal Advisor Agent: proposes selector alternatives on failures.
- Runner Agent: triggers pytest-bdd runs and forwards results to the dashboard.
- Governance Agent: enforces policies (reuse-first, mode discipline), collects provenance, and requests HIL approvals.
 - Domain Knowledge Agent (optional): supplies domain-specific enrichments when a Domain Pack is selected; otherwise bypassed.

#### n8n Workflow Sketch
- Trigger (API/UI webhook/MCP tool) → Parser → Designer → Reuse Scanner → HIL Approval (manual node) → Synthesizer → Local Run (mock|stub|real) → If PASS then Commit + Auto-PR → Runner (CI) → Metrics Ingest → Dashboard update.
- Error branches: fallback to next LLM provider; human escalation on repeated schema violations.

#### Integration Points
- API webhooks for start/approve/run; MCP calls can also trigger workflows.
- Workers execute heavy tasks; n8n coordinates handoffs and retries.

#### Deployment
- Run n8n via Docker. Persist `.n8n` for credentials/workflows. Use environment variables for provider keys.


