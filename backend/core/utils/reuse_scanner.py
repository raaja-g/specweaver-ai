"""
Reuse Scanner - detect existing equivalent tests in repo
"""
from pathlib import Path
from typing import List, Dict
import json

def find_equivalent_tests(test_cases_json: Path, tests_root: Path = Path('tests')) -> List[Dict]:
    candidates = []
    suite = json.loads(test_cases_json.read_text())
    new_titles = {tc['title'] for tc in suite.get('test_cases', [])}
    new_traces = set()
    for tc in suite.get('test_cases', []):
        for tr in tc.get('traceTo', []):
            new_traces.add(tr)
    for py in tests_root.rglob('test_*.py'):
        txt = py.read_text(errors='ignore')
        for title in new_titles:
            if title[:40] in txt:
                candidates.append({"file": str(py), "reason": f"title match: {title[:40]}"})
        for tr in new_traces:
            if tr in txt:
                candidates.append({"file": str(py), "reason": f"trace match: {tr}"})
    return candidates
