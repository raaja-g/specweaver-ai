### Quick Start: SpecWeaver BDD

This guide covers creating BDD scripts, generating code, running tests, and configuring the environment.

## 1) Prerequisites

- Python 3.12+ and a virtualenv
- Playwright browsers for UI testing

Install dependencies and Playwright:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m playwright install chromium
```

Optionally install other browsers:

```bash
python -m playwright install webkit firefox
```

## 2) Project structure for BDD

- Features: `tests/features/*.feature`
- Step definitions: `tests/steps/**/<area>_steps.py`
- Global fixtures and default steps: `tests/conftest.py`
- Pytest configuration: `pytest.ini`

Notes:

- Markers registered in `pytest.ini`: `auth`, `cart`, `checkout`, `general`, `search`.
- Default catch‑all steps exist in `tests/conftest.py`: any Given/When/Then not yet implemented will not fail the suite, so newly generated tests run immediately.

## 3) Creating BDD scripts

### A) Hand‑write a feature

1) Create `tests/features/<area>.feature` and author scenarios in Gherkin, e.g.:

```gherkin
@search
Feature: Search
  Scenario: Search for a product
    Given I am a guest user on the homepage
    When I search for the term "Hero Hoodie"
    Then the search results page should be displayed
```

2) Create/update a step file `tests/steps/<area>/<area>_steps.py` and bind scenarios:

```python
from pathlib import Path
from pytest_bdd import scenarios

FEATURE_FILE = Path(__file__).resolve().parents[2] / "features" / "<area>.feature"
scenarios(str(FEATURE_FILE))
```

3) Add specific Given/When/Then functions as needed. If omitted, the generic steps in `tests/conftest.py` will keep tests runnable.

### B) Generate from a user story using the CLI

End‑to‑end flow: Parse story → Generate tests → Synthesize code.

```bash
# 1) Parse story to requirement graph
python -m backend.cli.specweaver_cli parse examples/example_story.md --output artifacts

# 2) Generate test cases JSON from requirement graph
python -m backend.cli.specweaver_cli generate artifacts/requirement_graph.json --output artifacts

# 3) Synthesize executable code (features + steps)
python -m backend.cli.specweaver_cli synthesize \
  artifacts/test_cases.json \
  --requirement artifacts/requirement_graph.json \
  --output tests/generated \
  --ui-mode real \
  --api-mode mock

# One-shot pipeline
python -m backend.cli.specweaver_cli full \
  examples/example_story.md \
  --output artifacts \
  --coverage comprehensive \
  --ui-mode real \
  --api-mode mock
```

What gets created:

- Feature files under `tests/generated/features`
- Step files under `tests/generated/steps`

Generated step files bind to their feature using a robust absolute path pattern (via `pathlib.Path`), ensuring reliable pytest discovery.

## 4) Running tests

Run all tests:

```bash
source venv/bin/activate
pytest tests -q
```

Run by marker:

```bash
pytest -q -m search
```

Verbose output:

```bash
pytest -vv
```

HTML report (enabled by default in pytest.ini):

```bash
pytest --html=reports/pytest.html --self-contained-html
```

Parallel execution and progress:

```bash
# Run with 4 workers, distribute by scope, show live logs and step names
HEADLESS=1 UI_MODE=real TARGET_URL="https://your.app" \
pytest -n 4 --dist=loadscope -vv -s

# Auto-pick workers based on CPU
pytest -n auto --dist=loadscope -vv -s

# Show top slow tests
pytest -n 8 --dist=loadscope -vv -s --durations=10
```

You can set defaults in `pytest.ini` (optional):

```ini
[pytest]
addopts = -q --capture=no --html=reports/pytest.html --self-contained-html -n auto --dist=loadscope
```

Where to see results:

- Terminal output shows pass/fail; dots indicate success.
- Optional HTML report at `reports/pytest.html`.
 - Per-test logs at `reports/logs/<testname>.log`.
 - Live console logs enabled via `--capture=no`.

## 5) Environment configuration

Core config files:

- `pytest.ini`
  - `python_files = test_*.py *_test.py *_steps.py`
  - `testpaths = tests`
  - `bdd_features_base_dir = tests/features`
  - markers registered: `auth`, `cart`, `checkout`, `general`, `search`

- `tests/conftest.py`
  - Default execution config fixture:
    - `uiMode`: `real` | `mock`
    - `apiMode`: `mock` | `stub` | `real`
    - `target_url`: default `https://luma.enablementadobe.com/content/luma/us/en.html`
  - Fixture `authenticated_page(page, execution_config)` navigates and can mock routes in mock mode
  - Catch‑all Given/When/Then step stubs (using pytest‑bdd parsers) so missing steps don’t fail runs

Change target URL or modes:

- Create `tests/execution_config.json`, e.g. `{ "uiMode": "real", "apiMode": "stub", "target_url": "https://your.app" }`
- Or set env vars per run: `TARGET_URL=... UI_MODE=real API_MODE=stub pytest ...`
- Or pass `--ui-mode` / `--api-mode` when running `synthesize` or `full`.

Headless vs headed browser:

- By default we launch headed for visibility in dev.
- For parallel runs, prefer headless: set `HEADLESS=1`.
Optional env vars (only if using LLM providers for parsing/generation):

- Provider API keys per `config/llm.yml` (e.g., `OPENAI_API_KEY`, `GEMINI_API_KEY`) or configure local/Ollama.

## 6) Best practices

- Author professional Gherkin (Given/When/Then), proper indentation, tags at the top of the feature.
- Let generated tests run with default steps first, then replace defaults with real browser actions and assertions.
- Use `pytest -k "<substring>"` and `-m <marker>` to focus during development.

## 7) References

- Pytest‑BDD documentation: [https://pytest-bdd.readthedocs.io/en/stable/](https://pytest-bdd.readthedocs.io/en/stable/)


