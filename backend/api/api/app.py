"""
SpecWeaver API - FastAPI backend
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import uuid
from datetime import datetime
import logging
import sys
import os
import difflib

# Add backend core to path
sys.path.append(str(Path(__file__).parent.parent / "core"))

from core.schemas import RequirementGraph, TestSuite, ExecutionConfig
from core.llm_orchestrator import LLMOrchestrator
from core.requirement_parser import RequirementParser
from core.test_generator import TestCaseGenerator
from core.code_synthesizer import CodeSynthesizer

# Setup
app = FastAPI(title="SpecWeaver API", version="1.0.0")
logger = logging.getLogger(__name__)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for reports
reports_dir = Path("reports")
reports_dir.mkdir(exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")

# Storage
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

# In-memory store (would use Redis/DB in production)
sessions: Dict[str, Any] = {}
test_runs: Dict[str, Any] = {}
RUNS_FILE = ARTIFACTS_DIR / "run_status.json"


def _serialize_run(run: Dict[str, Any]) -> Dict[str, Any]:
    out = run.copy()
    for k in ["created_at", "started_at", "completed_at"]:
        if isinstance(out.get(k), datetime):
            out[k] = out[k].isoformat()
    return out


def _save_runs() -> None:
    try:
        RUNS_FILE.write_text(json.dumps({k: _serialize_run(v) for k, v in test_runs.items()}, indent=2))
    except Exception:
        logger.exception("Failed to persist run status")


def _load_runs() -> None:
    if RUNS_FILE.exists():
        try:
            data = json.loads(RUNS_FILE.read_text())
            for k, v in data.items():
                for ts in ["created_at", "started_at", "completed_at"]:
                    if v.get(ts):
                        v[ts] = datetime.fromisoformat(v[ts])
            test_runs.update(data)
        except Exception:
            logger.exception("Failed to load run status")


def _append_metrics(summary: Dict[str, Any]) -> None:
    metrics_file = ARTIFACTS_DIR / "metrics.json"
    try:
        if metrics_file.exists():
            arr = json.loads(metrics_file.read_text())
        else:
            arr = []
        arr.append(summary)
        metrics_file.write_text(json.dumps(arr, indent=2))
    except Exception:
        logger.exception("Failed to append metrics")


def _read_metrics_history() -> List[Dict[str, Any]]:
    metrics_file = ARTIFACTS_DIR / "metrics.json"
    if not metrics_file.exists():
        return []
    try:
        return json.loads(metrics_file.read_text())
    except Exception:
        logger.exception("Failed to read metrics history")
        return []


class RequirementUpload(BaseModel):
    """Request to upload/parse requirement"""
    story_text: str
    domain: Optional[str] = None
    tags: Optional[List[str]] = []


class GenerateRequest(BaseModel):
    """Request to generate test cases"""
    requirement_id: str
    coverage: str = "comprehensive"
    domain_pack: Optional[str] = None
    allow_duplicates: bool = False


class ApprovalRequest(BaseModel):
    """Request to approve generated tests"""
    requirement_id: str
    test_case_ids: List[str]
    approved: bool
    notes: Optional[str] = None
    allow_duplicates: bool = False


class RunRequest(BaseModel):
    """Request to run tests"""
    session_id: str
    ui_mode: str = "real"
    api_mode: str = "mock"
    tags: Optional[List[str]] = []
    auto_pr: bool = False


@app.get("/")
async def root():
    """Health check"""
    return {"status": "healthy", "service": "SpecWeaver API"}


@app.post("/api/requirements")
async def upload_requirement(req: RequirementUpload):
    """Upload and parse a requirement"""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Parse requirement
        orchestrator = LLMOrchestrator()
        parser = RequirementParser(orchestrator)
        requirement = parser.parse(story_text=req.story_text)
        
        # Add domain if provided
        if req.domain:
            requirement.domain = req.domain
        if req.tags:
            requirement.tags.extend(req.tags)
        
        # Save to artifacts
        req_dir = ARTIFACTS_DIR / session_id
        req_dir.mkdir(exist_ok=True)
        req_file = req_dir / "requirement_graph.json"
        req_file.write_text(requirement.model_dump_json(indent=2))
        
        # Store in session
        sessions[session_id] = {
            "requirement": requirement,
            "created_at": datetime.utcnow(),
            "status": "parsed",
            "raw_text": req.story_text
        }
        
        return {
            "session_id": session_id,
            "requirement_id": requirement.id,
            "title": requirement.title,
            "actor": requirement.actor,
            "goal": requirement.goal,
            "ac_count": len(requirement.acceptanceCriteria),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to parse requirement: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/requirements/file")
async def upload_requirement_file(
    file: UploadFile = File(...),
    domain: Optional[str] = Form(default=None),
    tags: Optional[str] = Form(default=None),
):
    """Upload and parse a requirement from a file (.txt, .md, .docx, .pdf)."""
    try:
        suffix = (Path(file.filename).suffix or "").lower()
        raw = await file.read()
        text = ""
        if suffix in [".txt", ".md"]:
            text = raw.decode("utf-8", errors="ignore")
        elif suffix == ".docx":
            try:
                import docx  # type: ignore
                from io import BytesIO
                doc = docx.Document(BytesIO(raw))
                text = "\n".join([p.text for p in doc.paragraphs])
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"DOCX parsing failed: {e}")
        elif suffix == ".pdf":
            try:
                from io import BytesIO
                from pdfminer.high_level import extract_text  # type: ignore
                text = extract_text(BytesIO(raw))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"PDF parsing failed: {e}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt, .md, .docx, or .pdf")

        body = RequirementUpload(story_text=text, domain=domain, tags=(tags.split(',') if tags else []))
        return await upload_requirement(body)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("upload_requirement_file failed")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/requirements/{session_id}/generate")
async def generate_test_cases(session_id: str, req: GenerateRequest):
    """Generate test cases from requirement"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        requirement = sessions[session_id]["requirement"]
        # Pass original raw user input to generator for direct LLM BDD
        raw_text = sessions[session_id].get("raw_text")
        if raw_text:
            requirement.raw_text = raw_text  # type: ignore
        
        # Generate test cases (threadpool to avoid event loop conflicts)
        orchestrator = LLMOrchestrator()
        generator = TestCaseGenerator(orchestrator)
        test_suite = await run_in_threadpool(generator.generate, requirement, req.coverage)
        
        # Save to artifacts
        suite_file = ARTIFACTS_DIR / session_id / "test_cases.json"
        suite_file.write_text(test_suite.model_dump_json(indent=2))
        
        # Reuse scan
        duplicates: List[Dict[str, Any]] = []
        try:
            from core.utils.reuse_scanner import find_equivalent_tests
            duplicates = find_equivalent_tests(suite_file, Path("tests"))
        except Exception:
            logger.exception("Reuse scan failed")

        if duplicates and not req.allow_duplicates:
            raise HTTPException(status_code=409, detail={"duplicates": duplicates})

        # Update session
        sessions[session_id]["test_suite"] = test_suite
        sessions[session_id]["status"] = "generated"
        
        return {
            "session_id": session_id,
            "test_count": len(test_suite.test_cases),
            "coverage": test_suite.coverage_metrics,
            "test_cases": [
                {
                    "id": tc.id,
                    "title": tc.title,
                    "type": tc.type,
                    "priority": tc.priority,
                    "trace_to": tc.traceTo,
                    "preconditions": tc.preconditions,
                    "data": tc.data,  # includes raw_steps/examples if present
                }
                for tc in test_suite.test_cases
            ],
            "duplicates": duplicates
        }
    except Exception as e:
        logger.error(f"Failed to generate test cases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/requirements/{session_id}/approve")
async def approve_tests(session_id: str, req: ApprovalRequest):
    """Approve generated test cases"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        requirement = session["requirement"]
        test_suite = session["test_suite"]
        
        # Filter approved test cases
        approved_cases = [
            tc for tc in test_suite.test_cases 
            if tc.id in req.test_case_ids
        ]
        
        if not approved_cases:
            raise HTTPException(status_code=400, detail="No test cases to approve")
        
        # Reuse scan on approved set
        approved_suite_path = ARTIFACTS_DIR / session_id / "approved_test_cases.json"
        
        # Serialize test cases safely, handling datetime objects
        def safe_serialize(obj):
            if hasattr(obj, 'model_dump'):
                data = obj.model_dump()
                # Convert any datetime objects to strings
                for key, value in data.items():
                    if hasattr(value, 'isoformat'):
                        data[key] = value.isoformat()
                return data
            return str(obj)
        
        approved_suite_json = {
            "requirement_id": requirement.id,
            "test_cases": [safe_serialize(tc) for tc in test_suite.test_cases if tc.id in req.test_case_ids]
        }
        (ARTIFACTS_DIR / session_id).mkdir(exist_ok=True)
        approved_suite_path.write_text(json.dumps(approved_suite_json, indent=2))
        duplicates: List[Dict[str, Any]] = []
        try:
            from core.utils.reuse_scanner import find_equivalent_tests
            duplicates = find_equivalent_tests(approved_suite_path, Path("tests"))
        except Exception:
            logger.exception("Reuse scan failed on approval")
        if duplicates and not req.allow_duplicates:
            raise HTTPException(status_code=409, detail={"duplicates": duplicates})

        # Generate code for approved tests with proper functional organization
        config = ExecutionConfig()
        synthesizer = CodeSynthesizer()
        
        # Write directly to framework tests/ root (no per-session folders)
        test_dir = Path("tests")
        test_suite.test_cases = approved_cases  # Only approved
        generated_files = synthesizer.synthesize(requirement, test_suite, config, test_dir)
        
        # Update session
        session["approved_tests"] = req.test_case_ids
        session["generated_files"] = {k: str(v) for k, v in generated_files.items()}
        session["status"] = "approved"
        
        return {
            "session_id": session_id,
            "approved_count": len(approved_cases),
            "generated_files": list(generated_files.keys()),
            "test_directory": str(test_dir),
            "duplicates": duplicates
        }
    except Exception as e:
        logger.error(f"Failed to approve tests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/runs")
async def run_tests(req: RunRequest, background_tasks: BackgroundTasks):
    """Trigger test run"""
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    run_id = str(uuid.uuid4())
    
    # Create run record
    test_runs[run_id] = {
        "id": run_id,
        "session_id": req.session_id,
        "ui_mode": req.ui_mode,
        "api_mode": req.api_mode,
        "auto_pr": req.auto_pr,
        "requirement_id": sessions[req.session_id]["requirement"].id if req.session_id in sessions else None,
        "status": "queued",
        "created_at": datetime.utcnow()
    }
    
    # Queue background execution (RQ/Redis if available)
    # Try RQ if Redis is available, otherwise use BackgroundTasks
    use_rq = False
    if os.getenv("REDIS_URL"):
        try:
            import redis
            from rq import Queue

            conn = redis.from_url(os.getenv("REDIS_URL"))
            # Test Redis connection
            conn.ping()
            q = Queue("specweaver", connection=conn, default_timeout=3600)
            job = q.enqueue("backend.api.worker.run_tests_job", run_id, req.session_id, req.ui_mode, req.api_mode, req.auto_pr, test_runs[run_id]["requirement_id"])
            test_runs[run_id]["job_id"] = job.id
            use_rq = True
            logger.info(f"✅ Queued job {job.id} for run {run_id}")
        except Exception as e:
            logger.warning(f"❌ RQ enqueue failed ({e}), falling back to BackgroundTasks")
            background_tasks.add_task(execute_tests, run_id, req)
    else:
        logger.info("No REDIS_URL configured, using BackgroundTasks")
        background_tasks.add_task(execute_tests, run_id, req)
    
    return {
        "run_id": run_id,
        "status": "queued",
        "message": "Test run queued for execution"
    }


async def execute_tests(run_id: str, req: RunRequest):
    """Execute tests in background"""
    import subprocess
    
    try:
        test_runs[run_id]["status"] = "running"
        test_runs[run_id]["started_at"] = datetime.utcnow()
        
        # Run pytest from framework tests/ root
        test_dir = Path("tests")
        cmd = [
            "pytest", str(test_dir),
            "-q", "--tb=short",
            f"--ui-mode={req.ui_mode}",
            f"--api-mode={req.api_mode}"
        ]
        
        if req.tags:
            cmd.extend(["-m", " or ".join(req.tags)])
        
        # Ensure strict BDD by default (no generic steps)
        env = os.environ.copy()
        env.setdefault("ALLOW_GENERIC_STEPS", "0")
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        # Update run status
        test_runs[run_id]["status"] = "completed" if result.returncode == 0 else "failed"
        test_runs[run_id]["completed_at"] = datetime.utcnow()
        test_runs[run_id]["output"] = result.stdout
        test_runs[run_id]["errors"] = result.stderr
        test_runs[run_id]["exit_code"] = result.returncode
        _save_runs()

        # Append metrics summary
        _append_metrics({
            "run_id": run_id,
            "session_id": req.session_id,
            "status": test_runs[run_id]["status"],
            "created_at": _serialize_run(test_runs[run_id])["created_at"],
            "completed_at": _serialize_run(test_runs[run_id]).get("completed_at"),
        })

        # Auto-PR on pass
        if test_runs[run_id]["status"] == "completed" and test_runs[run_id].get("auto_pr"):
            try:
                story_id = test_runs[run_id].get("requirement_id") or req.session_id
                subprocess.run(["bash", "scripts/auto_pr.sh", str(story_id)], check=False)
            except Exception:
                logger.exception("Auto-PR script failed")
    except Exception as e:
        test_runs[run_id]["status"] = "error"
        test_runs[run_id]["error"] = str(e)
        _save_runs()


@app.get("/api/runs/{run_id}")
async def get_run_status(run_id: str):
    """Get test run status with logs and reports"""
    if run_id not in test_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Attempt to refresh from persisted file to avoid stale "queued" status
    try:
        if RUNS_FILE.exists():
            data = json.loads(RUNS_FILE.read_text())
            if run_id in data:
                # Coerce timestamps
                for ts in ["created_at", "started_at", "completed_at"]:
                    if data[run_id].get(ts):
                        try:
                            data[run_id][ts] = datetime.fromisoformat(data[run_id][ts])
                        except Exception:
                            pass
                test_runs[run_id].update(data[run_id])
    except Exception:
        logger.exception("Failed to refresh run status in get_run_status")
    
    run_data = test_runs[run_id].copy()
    run_data['logs'] = _get_run_logs(run_id)
    run_data['reports'] = _get_run_reports(run_id)
    return run_data


@app.post("/api/runs/{run_id}/refresh")
async def refresh_run_status(run_id: str):
    """Refresh run status from artifacts/run_status.json (for RQ worker updates)"""
    if not RUNS_FILE.exists() or run_id not in test_runs:
        return test_runs.get(run_id, {"id": run_id, "status": "unknown"})
    try:
        data = json.loads(RUNS_FILE.read_text())
        if run_id in data:
            for ts in ["created_at", "started_at", "completed_at"]:
                if data[run_id].get(ts):
                    try:
                        data[run_id][ts] = datetime.fromisoformat(data[run_id][ts])
                    except Exception:
                        pass
            test_runs[run_id].update(data[run_id])
    except Exception:
        logger.exception("Failed to refresh run status")
    return test_runs[run_id]


def _get_run_logs(run_id: str) -> List[Dict[str, Any]]:
    """Get execution logs for a run"""
    logs = []
    logs_dir = Path("artifacts/logs")
    
    # Look for log files related to this run
    if logs_dir.exists():
        for log_file in logs_dir.glob(f"*{run_id}*.log"):
            try:
                with open(log_file, 'r') as f:
                    content = f.read()
                    logs.append({
                        "file": log_file.name,
                        "content": content[-5000:] if len(content) > 5000 else content,  # Last 5KB
                        "size": log_file.stat().st_size,
                        "modified": log_file.stat().st_mtime
                    })
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")
    
    # Also check for pytest output logs
    pytest_log = Path("artifacts") / f"pytest_{run_id}.log"
    if pytest_log.exists():
        try:
            with open(pytest_log, 'r') as f:
                content = f.read()
                logs.append({
                    "file": f"pytest_{run_id}.log",
                    "content": content[-5000:] if len(content) > 5000 else content,
                    "size": pytest_log.stat().st_size,
                    "modified": pytest_log.stat().st_mtime
                })
        except Exception as e:
            logger.error(f"Error reading pytest log: {e}")
    
    return logs


def _get_run_reports(run_id: str) -> List[Dict[str, Any]]:
    """Get test reports for a run"""
    reports = []
    reports_dir = Path("reports")
    
    # Look for Allure reports
    allure_dir = reports_dir / "allure-results"
    if allure_dir.exists():
        allure_files = list(allure_dir.glob("*.json")) + list(allure_dir.glob("*.txt"))
        if allure_files:
            reports.append({
                "type": "allure",
                "name": "Allure Test Results",
                "path": str(allure_dir),
                "files": [f.name for f in allure_files],
                "url": f"/reports/allure-results/"
            })
    
    # Look for HTML reports
    for html_file in reports_dir.glob("*.html"):
        reports.append({
            "type": "html",
            "name": html_file.stem.replace('_', ' ').title(),
            "path": str(html_file),
            "url": f"/reports/{html_file.name}",
            "size": html_file.stat().st_size,
            "modified": html_file.stat().st_mtime
        })
    
    # Look for JUnit XML reports
    for xml_file in reports_dir.glob("*.xml"):
        reports.append({
            "type": "junit",
            "name": xml_file.stem.replace('_', ' ').title(),
            "path": str(xml_file),
            "url": f"/reports/{xml_file.name}",
            "size": xml_file.stat().st_size,
            "modified": xml_file.stat().st_mtime
        })
    
    return reports


@app.get("/api/metrics")
async def get_metrics():
    """Get dashboard metrics"""
    total_requirements = len(sessions)
    total_runs = len(test_runs)
    
    # Calculate pass rate
    completed_runs = [r for r in test_runs.values() if r["status"] == "completed"]
    pass_rate = len(completed_runs) / total_runs * 100 if total_runs > 0 else 0
    
    # Get recent runs
    recent_runs = sorted(
        test_runs.values(),
        key=lambda x: x["created_at"],
        reverse=True
    )[:5]
    
    return {
        "total_requirements": total_requirements,
        "total_runs": total_runs,
        "pass_rate": pass_rate,
        "recent_runs": [
            {
                "id": r["id"],
                "status": r["status"],
                "created_at": r["created_at"].isoformat()
            }
            for r in recent_runs
        ],
        "test_types": {
            "ui_real": sum(1 for r in test_runs.values() if r.get("ui_mode") == "real"),
            "ui_mock": sum(1 for r in test_runs.values() if r.get("ui_mode") == "mock"),
            "api_real": sum(1 for r in test_runs.values() if r.get("api_mode") == "real"),
            "api_mock": sum(1 for r in test_runs.values() if r.get("api_mode") == "mock")
        },
        "history": _read_metrics_history()
    }


@app.get("/api/artifacts/{session_id}/{filename}")
async def download_artifact(session_id: str, filename: str):
    """Download generated artifact"""
    file_path = ARTIFACTS_DIR / session_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/json"
    )


@app.post("/api/requirements/{session_id}/preview")
async def preview_tests(session_id: str, body: Dict[str, Any]):
    """Generate preview code for selected tests and return diffs before approval"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        session = sessions[session_id]
        requirement: RequirementGraph = session["requirement"]
        test_suite: TestSuite = session["test_suite"]
        selected_ids: List[str] = body.get("test_case_ids") or [tc.id for tc in test_suite.test_cases]

        # Filter tests
        filtered_cases = [tc for tc in test_suite.test_cases if tc.id in selected_ids]
        preview_suite = TestSuite(requirement_id=requirement.id, test_cases=filtered_cases)

        # Synthesize into artifacts preview dir
        preview_dir = ARTIFACTS_DIR / session_id / "preview"
        synthesizer = CodeSynthesizer()
        files = synthesizer.synthesize(requirement, preview_suite, ExecutionConfig(), preview_dir)

        diffs: List[Dict[str, Any]] = []
        for kind, path in files.items():
            prev_path = Path(path)
            # Map to potential existing file in tests
            existing_candidates = []
            if prev_path.suffix in {".py", ".feature"}:
                # naive mapping to tests directory by filename
                existing_candidates = list(Path("tests").rglob(prev_path.name))
            diff_text = ""
            exists = False
            if existing_candidates:
                exists = True
                try:
                    old_text = existing_candidates[0].read_text().splitlines(keepends=True)
                    new_text = prev_path.read_text().splitlines(keepends=True)
                    diff_lines = difflib.unified_diff(old_text, new_text, fromfile=str(existing_candidates[0]), tofile=str(prev_path))
                    diff_text = "".join(diff_lines)
                except Exception:
                    diff_text = ""
            diffs.append({
                "type": kind,
                "preview_path": str(prev_path),
                "exists": exists,
                "diff": diff_text
            })
        return {"session_id": session_id, "diffs": diffs}
    except Exception as e:
        logger.exception("Preview failed")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
