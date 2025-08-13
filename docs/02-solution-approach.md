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

##### Decision table framework (plug-and-run)

This framework expands a flow/graph into decision-table–driven test cases with ECP/BVA built in, plus risk tagging and prioritization. It is deterministic and can be automated end-to-end.

- Inputs you provide
  - Flow graph: nodes = states/screens; edges = transitions (with guards/conditions)
  - Parameters per condition: name, type, domain/range, constraints, business rules
  - Risk hints (optional): likelihood, impact, recent defects, usage frequency

- Transform graph → decision conditions

| ID | Condition (C)                | Param   | Type    | Domain/Constraint    | Source (Node/Edge) |
| -- | ---------------------------- | ------- | ------- | -------------------- | ------------------ |
| C1 | `amount <= credit_limit`     | amount  | number  | 0..1,000,000; step 1 | Edge E12           |
| C2 | `country in allowed_markets` | country | enum    | {US, EU, IN}         | E7                 |
| C3 | `user_age >= 18`             | age     | integer | 0..120               | E3                 |

- Build ECP & BVA per parameter

| Param   | Valid Classes (ECP)                              | Invalid Classes (ECP)         | BVA Points                        |
| ------- | ------------------------------------------------ | ----------------------------- | --------------------------------- |
| amount  | [0..limit], [>0 and <limit], [exactly limit]     | negative, >limit, non-numeric | −1, 0, 1, limit−1, limit, limit+1 |
| country | {US},{EU},{IN}                                   | {others,null}                 | N/A                               |
| age     | [18..120]                                        | <18, >120, null               | 17,18,19; 119,120,121             |

- Decision table skeleton (pre-reduction)

| Rule | C1: amount vs limit             | C2: country | C3: age           | Expected Transition/Outcome |
| ---- | -------------------------------- | ----------- | ----------------- | --------------------------- |
| R1   | amount = 0 (BVA)                | US          | 18 (BVA)          | Approve                     |
| R2   | amount = limit (BVA)            | EU          | 35                | Approve                     |
| R3   | amount = limit+1 (BVA, invalid) | IN          | 40                | Reject: over limit          |
| R4   | amount = −1 (invalid)           | US          | 25                | Error: validation           |
| R5   | amount = limit−1                | IN          | 17 (BVA invalid)  | Reject: underage            |
| R6   | amount = 1                      | Other       | 30                | Error: market not allowed   |
| R7   | amount = 500k                   | EU          | 121 (BVA invalid) | Error: age invalid          |

Use pairwise/3‑wise to reduce combinations while ensuring each condition/value pair appears with every other at least once. Keep all BVA rows un‑reduced.

- Risk model and prioritization

Risk = (Impact 1–5) × (Likelihood 1–5) × (Detectability 1–5, inverse)

Defaults:
- Invalid inputs & boundary transitions → Likelihood +1, Detectability +1
- Business‑critical paths (checkout, payment, auth) → Impact +2
- Recently changed code/known issues → Likelihood +2

| Rule | Coverage Intent            | Risk (I×L×D) | Priority |
| ---- | -------------------------- | ------------ | -------- |
| R2   | Happy path @upper boundary | 4×2×2=16     | P1       |
| R3   | Limit breach               | 5×3×3=45     | P0       |
| R5   | Age boundary fail          | 4×3×3=36     | P0       |
| R6   | Geo policy violation       | 4×2×2=16     | P1       |
| R4   | Negative amount            | 3×2×2=12     | P2       |
| R7   | Max age overflow           | 3×2×2=12     | P2       |
| R1   | Zero amount edge           | 3×2×2=12     | P2       |

Prioritization rule (suggested): P0: risk ≥ 30, P1: 15–29, P2: <15 (tune per org SLA).

- Expand rules → concrete test cases

Template:
- Test ID: DT-R{n}
- Preconditions: State from source node; data setup (credit_limit, markets)
- Input Set: Concrete values chosen from ECP/BVA reps
- Steps: Drive along the graph edge(s) fulfilling rule conditions
- Expected: Transition taken + UI/API response + side effects
- Tags: ECP, BVA, NEG, domain tags (e.g., PAYMENT, GEO), risk P0/P1/P2

Example (R3):
- Pre: credit_limit = 1000; allowed_markets = {US,EU,IN}; user_age = 40
- Input: amount = 1001 (limit+1), country = IN
- Steps: Submit payment
- Expected: Reject with over_limit; no ledger entry; audit log event PAYMENT_REJECTED
- Tags: BVA, NEG, PAYMENT, P0

- Optional: Generate BDD (from decision rows)

```gherkin
Feature: Payment decisioning

Background:
  Given credit limit is <credit_limit>
  And allowed markets are <markets>

Scenario Outline: Decision outcome for amount, country, age
  When I submit amount <amount> from <country> for user aged <age>
  Then the decision should be "<outcome>"

Examples:
| credit_limit | markets  | amount | country | age | outcome             | tags                    |
| 1000         | US,EU,IN | 1001   | IN      | 40  | Reject: over limit  | @BVA @NEG @PAYMENT @P0 |
| 1000         | US,EU,IN | 1000   | EU      | 35  | Approve             | @BVA @PAYMENT @P1      |
| 1000         | US,EU,IN | -1     | US      | 25  | Error: validation   | @NEG @P2               |
```

- Minimal algorithm (for automation)
1. Parse graph → collect guards (param, operator, value/range)
2. For each param: build ECP sets + BVA points
3. Build candidate rules:
   - Start with all BVA points as fixed rules
   - Add pairwise set covering remaining ECP classes
4. Attach risk (function of path criticality + input class + change hotspots)
5. Emit artifacts: decision table (CSV), expanded test cases (CSV/JSON), BDD `.feature`

- Output schemas (CSV/JSON)

Decision table CSV

```csv
rule_id,condition_id,param,value,class(bva|ecp-valid|ecp-invalid),expected_outcome,risk,priority,tags
R3,C1,amount,1001,bva,Reject: over limit,45,P0,"BVA;NEG;PAYMENT"
```

Test case JSON

```json
{
  "id": "TC-DT-R3",
  "preconditions": {"credit_limit": 1000, "allowed_markets": ["US", "EU", "IN"], "user_age": 40},
  "inputs": {"amount": 1001, "country": "IN"},
  "path": ["Cart", "Checkout", "Decision"],
  "expected": {"decision": "Reject: over limit", "side_effects": ["no_posting", "audit_log"]},
  "tags": ["BVA", "NEG", "PAYMENT", "P0"]
}
```

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
