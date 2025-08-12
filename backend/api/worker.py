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
    import os
    
    # Use framework structure: write and run from tests/ root
    test_dir = Path("tests")
    
    # Get browser config from environment
    browser = os.getenv("BROWSER", "chromium")
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    timeout = os.getenv("BROWSER_TIMEOUT", "30000")
    
    # Build pytest command with proper browser configuration
    # Create logs directory
    logs_dir = Path("artifacts/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "pytest", str(test_dir),
        "-v", "--tb=long",
        "--capture=no",  # Show print statements
        f"--browser={browser}",
        f"--headless={headless}",
        f"--timeout={timeout}",
        f"--ui-mode={ui_mode}",
        f"--api-mode={api_mode}",
        "--alluredir=reports/allure-results",
        f"--junitxml=reports/junit_{run_id}.xml",
        f"--html=reports/report_{run_id}.html",
        "--self-contained-html"
    ]
    
    # Set environment variables for test execution
    env = os.environ.copy()
    env.update({
        "UI_MODE": ui_mode,
        "API_MODE": api_mode,
        "BROWSER": browser,
        "HEADLESS": str(headless),
        "BROWSER_TIMEOUT": timeout
    })
    
    # Create log file for this run
    log_file = logs_dir / f"pytest_{run_id}.log"
    
    try:
        # Run with output capture to both console and log file
        with open(log_file, 'w') as f:
            f.write(f"=== Test Execution Log for Run {run_id} ===\n")
            f.write(f"Command: {' '.join(cmd)}\n")
            f.write(f"Environment: UI_MODE={ui_mode}, API_MODE={api_mode}\n")
            f.write("=" * 50 + "\n\n")
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=300)
            
            # Write output to log file
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\n\nExit Code: {result.returncode}\n")
    
    except subprocess.TimeoutExpired:
        result = type('Result', (), {
            'returncode': -1, 
            'stdout': 'Test execution timed out after 300 seconds', 
            'stderr': 'Timeout'
        })()
    except Exception as e:
        result = type('Result', (), {
            'returncode': -2, 
            'stdout': '', 
            'stderr': f'Execution error: {str(e)}'
        })()
    
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
