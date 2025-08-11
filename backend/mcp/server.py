"""
SpecWeaver MCP Server

Implements MCP stdio (NDJSON framing: one JSON per line) and websocket transports
and exposes tools:
- parse_requirement
- generate_test_cases
- synthesize_scripts
- run_tests
- health

Request format:
  { "id": <string|number>, "method": <str>, "params": { ... } }

Response format:
  { "id": <same as request>, "ok": true, "result": { ... } }
  or
  { "id": <same as request>, "ok": false, "error": { "code": <str>, "message": <str> } }

Start (stdio):
  python -m backend.mcp.server --transport stdio

Start (websocket):
  python -m backend.mcp.server --transport ws --host 127.0.0.1 --port 8765
"""
from __future__ import annotations

import argparse
import asyncio
import json
from typing import Dict, Any
from pathlib import Path

from backend.core.requirement_parser import RequirementParser
from backend.core.llm_orchestrator import LLMOrchestrator
from backend.core.test_generator import TestCaseGenerator
from backend.core.code_synthesizer import CodeSynthesizer
from backend.core.schemas import RequirementGraph, TestSuite, ExecutionConfig

# Minimal MCP protocol structures

SERVER_VERSION = "0.1.0"


class ToolError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


async def mcp_handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method")
    params = request.get("params", {})
    try:
        if method == "health":
            return {"ok": True, "result": {"version": SERVER_VERSION}}

        if method == "parse_requirement":
            story_md = params.get("story_md")
            if story_md is None:
                raise ToolError("invalid_params", "story_md is required")
            try:
                req = RequirementParser(LLMOrchestrator()).parse(story_text=story_md)
            except Exception as e:
                raise ToolError("parse_error", str(e))
            return {"ok": True, "result": req.model_dump()}

        if method == "generate_test_cases":
            rg = params.get("requirement_graph")
            if not isinstance(rg, dict):
                raise ToolError("invalid_params", "requirement_graph object is required")
            requirement_graph = RequirementGraph(**rg)
            coverage = params.get("coverage", "comprehensive")
            suite = TestCaseGenerator(LLMOrchestrator()).generate(requirement_graph, coverage=coverage)
            return {"ok": True, "result": suite.model_dump()}

        if method == "synthesize_scripts":
            rg = params.get("requirement_graph")
            ts = params.get("test_suite")
            if not (isinstance(rg, dict) and isinstance(ts, dict)):
                raise ToolError("invalid_params", "requirement_graph and test_suite are required")
            requirement_graph = RequirementGraph(**rg)
            suite = TestSuite(**ts)
            cfg = ExecutionConfig(
                uiMode=params.get("ui_mode", "real"),
                apiMode=params.get("api_mode", "mock"),
            )
            out_dir = Path(params.get("out_dir", "tests/generated/mcp"))
            files = CodeSynthesizer().synthesize(requirement_graph, suite, cfg, out_dir)
            return {"ok": True, "result": {k: str(v) for k, v in files.items()}}

        if method == "run_tests":
            out_dir = Path(params.get("test_dir", "tests/generated/mcp"))
            ui_mode = params.get("ui_mode", "real")
            api_mode = params.get("api_mode", "mock")
            import subprocess
            cmd = ["pytest", str(out_dir), "-q", "--tb=short", f"--ui-mode={ui_mode}", f"--api-mode={api_mode}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {"ok": True, "result": {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}}

        raise ToolError("unknown_method", f"Unknown method: {method}")
    except ToolError as te:
        return {"ok": False, "error": {"code": te.code, "message": te.message}}
    except Exception as e:
        return {"ok": False, "error": {"code": "internal_error", "message": str(e)}}


# Transports
async def stdio_server() -> None:
    import sys
    # NDJSON: one request per line, one response per line
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            sys.stdout.write(json.dumps({"id": None, "ok": False, "error": {"code": "invalid_json", "message": "Failed to parse JSON"}}) + "\n")
            sys.stdout.flush()
            continue
        resp = await mcp_handle_request(req)
        resp_with_id = {"id": req.get("id")}
        resp_with_id.update(resp)
        sys.stdout.write(json.dumps(resp_with_id) + "\n")
        sys.stdout.flush()


async def websocket_server(host: str, port: int) -> None:
    import websockets

    async def handler(websocket):
        async for message in websocket:
            try:
                req = json.loads(message)
            except Exception:
                await websocket.send(json.dumps({"id": None, "ok": False, "error": {"code": "invalid_json", "message": "Failed to parse JSON"}}))
                continue
            resp = await mcp_handle_request(req)
            resp_with_id = {"id": req.get("id")}
            resp_with_id.update(resp)
            await websocket.send(json.dumps(resp_with_id))

    async with websockets.serve(handler, host, port):
        await asyncio.Future()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "ws"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.transport == "stdio":
        asyncio.run(stdio_server())
    else:
        asyncio.run(websocket_server(args.host, args.port))


if __name__ == "__main__":
    main()
