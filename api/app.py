"""
SpecWeaver API - FastAPI backend
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
import uuid
from datetime import datetime
import logging
import sys

# Add poc to path
sys.path.append(str(Path(__file__).parent.parent / "poc"))

from poc.schemas import RequirementGraph, TestSuite, ExecutionConfig
from poc.llm_orchestrator import LLMOrchestrator
from poc.requirement_parser import RequirementParser
from poc.test_generator import TestCaseGenerator
from poc.code_synthesizer import CodeSynthesizer

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

# Storage
ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

# In-memory store (would use Redis/DB in production)
sessions = {}
test_runs = {}


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


class ApprovalRequest(BaseModel):
    """Request to approve generated tests"""
    requirement_id: str
    test_case_ids: List[str]
    approved: bool
    notes: Optional[str] = None


class RunRequest(BaseModel):
    """Request to run tests"""
    session_id: str
    ui_mode: str = "real"
    api_mode: str = "mock"
    tags: Optional[List[str]] = []


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
            "status": "parsed"
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


@app.post("/api/requirements/{session_id}/generate")
async def generate_test_cases(session_id: str, req: GenerateRequest):
    """Generate test cases from requirement"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        requirement = sessions[session_id]["requirement"]
        
        # Generate test cases
        orchestrator = LLMOrchestrator()
        generator = TestCaseGenerator(orchestrator)
        test_suite = generator.generate(requirement, coverage=req.coverage)
        
        # Save to artifacts
        suite_file = ARTIFACTS_DIR / session_id / "test_cases.json"
        suite_file.write_text(test_suite.model_dump_json(indent=2))
        
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
                    "trace_to": tc.traceTo
                }
                for tc in test_suite.test_cases
            ]
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
        
        # Generate code for approved tests
        config = ExecutionConfig()
        synthesizer = CodeSynthesizer()
        
        test_dir = Path("tests") / "approved" / session_id
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
            "test_directory": str(test_dir)
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
        "status": "queued",
        "created_at": datetime.utcnow()
    }
    
    # Queue background execution
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
        
        # Run pytest
        test_dir = Path("tests") / "approved" / req.session_id
        cmd = [
            "pytest", str(test_dir),
            "-q", "--tb=short",
            f"--ui-mode={req.ui_mode}",
            f"--api-mode={req.api_mode}"
        ]
        
        if req.tags:
            cmd.extend(["-m", " or ".join(req.tags)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Update run status
        test_runs[run_id]["status"] = "completed" if result.returncode == 0 else "failed"
        test_runs[run_id]["completed_at"] = datetime.utcnow()
        test_runs[run_id]["output"] = result.stdout
        test_runs[run_id]["errors"] = result.stderr
        test_runs[run_id]["exit_code"] = result.returncode
        
    except Exception as e:
        test_runs[run_id]["status"] = "error"
        test_runs[run_id]["error"] = str(e)


@app.get("/api/runs/{run_id}")
async def get_run_status(run_id: str):
    """Get test run status"""
    if run_id not in test_runs:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return test_runs[run_id]


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
        }
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
