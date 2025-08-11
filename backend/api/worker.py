"""
RQ Worker job to execute tests and persist results
"""
from pathlib import Path
from datetime import datetime
import subprocess
import json
from typing import Dict

ARTIFACTS_DIR = Path("artifacts")
RUNS_FILE = ARTIFACTS_DIR / "run_status.json"
METRICS_FILE = ARTIFACTS_DIR / "metrics.json"


def _persist_run(run_id: str, record: Dict) -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    data = {}
    if RUNS_FILE.exists():
        try:
            data = json.loads(RUNS_FILE.read_text())
        except Exception:
            data = {}
    data[run_id] = record
    RUNS_FILE.write_text(json.dumps(data, indent=2))

    # Append metrics
    try:
        metrics = []
        if METRICS_FILE.exists():
            metrics = json.loads(METRICS_FILE.read_text())
        metrics.append({
            "run_id": run_id,
            "status": record.get("status"),
            "created_at": record.get("created_at"),
            "completed_at": record.get("completed_at"),
        })
        METRICS_FILE.write_text(json.dumps(metrics, indent=2))
    except Exception:
        pass


def run_tests_job(run_id: str, session_id: str, ui_mode: str, api_mode: str, auto_pr: bool = False, requirement_id: str | None = None) -> Dict:
    test_dir = Path("tests") / "approved" / session_id
    cmd = [
        "pytest", str(test_dir),
        "-q", "--tb=short",
        f"--ui-mode={ui_mode}",
        f"--api-mode={api_mode}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    record = {
        "id": run_id,
        "session_id": session_id,
        "status": "completed" if result.returncode == 0 else "failed",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "output": result.stdout,
        "errors": result.stderr,
        "exit_code": result.returncode,
        "ui_mode": ui_mode,
        "api_mode": api_mode,
        "auto_pr": auto_pr,
        "requirement_id": requirement_id,
    }
    _persist_run(run_id, record)

    # Auto-PR if requested and passed
    if auto_pr and record["status"] == "completed":
        try:
            story_id = requirement_id or session_id
            subprocess.run(["bash", "scripts/auto_pr.sh", str(story_id)], check=False)
        except Exception:
            pass

    return record
