### Prompt Templates

#### Parser Prompt
- System:
  - You extract a Requirement Graph from a user story.
  - Output strictly valid JSON matching the provided schema.
  - Do not include explanations or prose; return JSON only.
- User:
  - story: <paste markdown or gherkin>
  - schema: <RequirementGraph JSON Schema>
  - provider_order: [groq, gemini, cursor, openai]

Repair loop (if validation fails):
- Provide the validator error messages and the previous JSON.
- Ask: "Return corrected JSON only, no comments."

#### Test Case Generator Prompt
- System:
  - Expand Requirement Graph into test cases using ECP/BVA, decision tables, and risk heuristics.
  - Respect coverage=<basic|comprehensive> and deduplicate similar cases.
  - Ensure each case has `traceTo` AC IDs and `type` in [positive, negative, edge].
  - Emit Gherkin scenarios (BDD) for each case with consistent step phrasing.
- User:
  - requirement_graph: <RequirementGraph JSON>
  - coverage: <basic|comprehensive>
  - provider_order: [groq, gemini, cursor, openai]
  - existing_tests_index: <list of known tests to prefer>

#### Script Synthesis Prompt
- System:
  - Map semantic `steps[i].action` to locator repository/OpenAPI entries.
  - Emit code via provided Jinja2 templates.
  - Do not invent selectors; if unresolved, emit a TODO marker and continue.
  - Respect `executionMode` (mock|stub|real) by wiring mocks (WireMock/Prism/Playwright route mocking) when not `real`.
  - Propose self-healing alternatives on selector failures; write to suggestions artifact, not to code.
- User:
  - test_cases: <TestCase JSON array>
  - locator_repo: <YAML>
  - templates: <Jinja2>
  - provider_order: [groq, gemini, cursor, openai]
  - uiMode: <real|mock>
  - apiMode: <mock|stub|real>

#### Provider Normalization

- Output from any provider MUST be valid per the schemas. On failure, run the repair loop; if still failing, fall through to the next provider.
