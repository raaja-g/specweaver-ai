# SpecWeaver AI

A framework to parse user stories, generate structured test cases, and synthesize runnable automation scripts.

- Domain: Domain-agnostic core (optional Domain Packs for e-commerce, healthcare, fintech, etc.)
- Tests: pytest + Playwright
- NLP/AI: LLM + spaCy

Docs:
- `docs/01-architecture.md` — high-level diagram, components, artifacts
- `docs/02-solution-approach.md` — parsing, generation, synthesis, quality gates
- `docs/03-tech-stack.md` — stack and justification
- `docs/04-poc.md` — POC layout and commands
- `docs/08-schemas.md` — JSON schemas for RequirementGraph and TestCase
- `docs/09-mapping-and-page-objects.md` — locator YAML and resolution rules
- `docs/11-prompts.md` — prompt patterns and repair loop
 - `docs/10-governance-quality.md` — orchestration policy and MCP operational quality
 - `docs/12-ui-and-api.md` — UI pages, API endpoints, storage, execution modes
 - `docs/13-agentic-orchestration.md` — agent roles and n8n workflows

Quickstart (POC):
- Create `poc/` per `docs/04-poc.md` (or use provided scaffold when added)
- Generate artifacts: `python poc/parse_and_generate.py --story poc/example_story.md --out poc/artifacts`
- Optional codegen: `python poc/codegen.py --cases poc/artifacts/test_cases.json --locators locator-repo.yml --out tests`
- Run tests: `pytest -q -n auto`

Web UI/API:
- Start dev server: `uvicorn ui.app:app --reload --port 8080`
- Features: upload/compose requirement, HIL review, trigger test runs, metrics dashboard
- Storage: approved artifacts auto-committed into framework structure (features, steps, tests)

MCP (Docker Desktop) quickstart:
- Build: `docker build -t specweaver-mcp .`
- Run: `docker run --rm -it -e GROQ_API_KEY=$GROQ_API_KEY -e GOOGLE_API_KEY=$GOOGLE_API_KEY -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8765:8765 specweaver-mcp`
- Register server in Cursor as a custom MCP endpoint; use tools `parse_requirement`, `generate_test_cases`, `synthesize_scripts`, `validate_artifacts`, `run_tests`.
