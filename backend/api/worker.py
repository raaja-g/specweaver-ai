"""
RQ Worker job to execute tests
"""
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, Any

# test_runs will be persisted by API via file; worker only executes and returns status

def run_tests_job(run_id: str, session_id: str, ui_mode: str, api_mode: str) -> Dict[str, Any]:
    test_dir = Path("tests") / "approved" / session_id
    cmd = [
        "pytest", str(test_dir),
        "-q", "--tb=short",
        f"--ui-mode={ui_mode}",
        f"--api-mode={api_mode}"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "run_id": run_id,
        "status": "completed" if result.returncode == 0 else "failed",
        "completed_at": datetime.utcnow().isoformat(),
        "output": result.stdout,
        "errors": result.stderr,
        "exit_code": result.returncode,
    }
