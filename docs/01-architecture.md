### High-Level Architecture

- Input: User story (freeform or Gherkin)
- Parsing Engine: LLM + spaCy + rules -> Requirement Graph
- Test Case Generator: decision tables, ECP/BVA, risk heuristics -> structured cases (JSON/YAML)
- Script Synthesis: Jinja2 templates -> pytest + Playwright tests
- Mapping: locator repo (UI) + OpenAPI (API)
- Data: Faker + constraints
- Runner/Reporter: pytest xdist + Allure/HTML


#### Architecture Diagram

```mermaid
flowchart LR
  subgraph Input
    US["User Story\n(Gherkin or Freeform)"]
  end

  subgraph Parsing
    PE["Parsing Engine\nLLM + spaCy + Rules"]
    RG["Requirement Graph\n(Pydantic JSON)"]
  end

  subgraph Generation
    TCG["Test Case Generator\nECP/BVA, Decision Tables, Risk"]
    TCS["Test Cases\n(JSON/YAML)"]
  end

  subgraph Synthesis
    CSM["Code Synthesis Module\nJinja2 -> pytest-bdd + Playwright/HTTPX"]
    TESTS["Executable Tests\n(features + step defs)"]
  end

  subgraph Execution
    RUN["Runner/Reporter\npytest-bdd + xdist + Allure BDD"]
    RPTS["Reports\n(HTML/Allure)"]
  end

  US --> PE --> RG --> TCG --> TCS --> CSM --> TESTS --> RUN --> RPTS

  subgraph Refs
    LOC["Locator Repository\n(Page Objects YAML)"]
    OAS["OpenAPI Spec\n(API mapping)"]
    TMP["Templates\n(Jinja2)"]
    VDB["Vector DB\n(Embeddings)"]
    CFG["Config\n(mock|stub|real)"]
  end

  PE <---> VDB
  CSM ---- TMP
  CSM ---- LOC
  CSM ---- OAS

  subgraph Governance
    HIL["Human-in-the-loop Reviews"]
    VER["Schema Validation & Guardrails"]
    REUSE["Test Reuse Scanner\n(prefer existing)"]
    HEAL["Self-Healing Engine\n(selector proposals)"]
  end

  RG --> VER
  TCS --> VER
  TESTS --> REUSE --> HIL --> RUN
  LOC --> HEAL
  CFG --> RUN
  CFG --> CSM
  CFG --> PE
```

#### Component Responsibilities

- Parsing Engine: Normalize story, extract acceptance criteria, produce a validated `RequirementGraph`.
- Test Case Generator: Expand graph to decision-table-driven cases with ECP/BVA and risk tagging.
- Code Synthesis Module: Resolve semantic actions to UI/API via locator repository and OpenAPI; render tests using Jinja2.
- Runner/Reporter: Execute tests with `pytest -n auto`; collect Allure/HTML reports.
- Governance: Schema validation, deterministic codegen, human review gates, drift detection.

#### Artifacts & Interfaces

- Inputs: user story (Markdown/Gherkin), `locator-repo.yml`, OpenAPI spec.
- Outputs: `artifacts/requirement_graph.json`, `artifacts/test_cases.json|yaml`, generated tests under `tests/`.
- Interfaces: prompt templates, JSON schemas, Jinja template variables, mapping repo format and resolution rules.


### MCP Integration (IDE-native)

This framework is exposed as an MCP server so it can be used directly from MCP-capable IDEs (e.g., Cursor) via standard tools.

```mermaid
flowchart LR
  subgraph IDE
    MCPClient["MCP Client\n(Cursor/IDE)"]
  end

  subgraph Web["Web UI"]
    UI["Dashboard + HIL\n(Upload/Compose, Review, Run)"]
  end

  subgraph Backend["API Service"]
    API["REST API\n(HIL, Runs, Artifacts)"]
    QUEUE["Worker/Queue\n(Test Runs)"]
  end

  subgraph Container["Docker Desktop: specweaver-mcp"]
    MCPS["MCP Server\n(stdio / WebSocket)"]
    ORCH["LLM Orchestrator\nGroq → Gemini → Cursor CLI → OpenAI"]
    CORE["SpecWeaver Core\nParsing/Gen/Synthesis"]
  end

  subgraph Orchestration
    N8N["n8n Workflow Orchestrator\n(Agent graph & handoffs)"]
  end

  subgraph Stores
    GIT["Repo Structure\n(features/tests/artifacts)"]
    RPT["Results & Metrics\n(Allure + DB)"]
  end

  subgraph External
    GROQ["Groq API"]
    GEM["Gemini API"]
    CUR["Cursor CLI"]
    OAI["OpenAI API"]
  end

  UI <--> API
  API --> QUEUE
  API <--> GIT
  API <--> RPT
  API <--> N8N

  MCPClient <--> MCPS
  MCPS --> CORE
  CORE <--> ORCH
  CORE <--> GIT
  CORE <--> RPT
  CORE <--> N8N
  ORCH --> GROQ
  ORCH --> GEM
  ORCH --> CUR
  ORCH --> OAI
```

Exposed MCP tools:
- `parse_requirement(story_md)` → `requirement_graph.json`
- `generate_test_cases(requirement_graph, coverage)` → `test_cases.json`
- `synthesize_scripts(test_cases, locator_repo)` → files under `tests/`
- `validate_artifacts(requirement_graph, test_cases)` → issues list
- `run_tests(pytest_args)` → report paths

Transport: stdio in local dev; WebSocket/HTTP bridge enabled from the Docker container for IDE connectivity.

### UI + API Responsibilities

- Web UI: Upload/enter requirements, show generated test proposals (HIL approval), trigger runs, and display dashboard metrics/trends.
- API Service: Endpoints for parse/generate/synthesize, approvals, run orchestration, artifact storage, and results ingestion.
- Queue/Workers: Execute long-running tasks (generation and test runs) and stream status to UI.
- Artifact Store: Persist requirement graphs, test cases, generated features/step defs/tests under the framework’s structure.
- Results Store: Ingest Allure/pytest results to power dashboard KPIs and trends.


