"""
SpecWeaver MCP Server

Implements MCP stdio and websocket transports and exposes tools:
- parse_requirement
- generate_test_cases
- synthesize_scripts
- run_tests

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

class ToolError(Exception):
    pass


async def mcp_handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    method = request.get("method")
    params = request.get("params", {})
    try:
        if method == "parse_requirement":
            story_md = params.get("story_md", "")
            req = RequirementParser(LLMOrchestrator()).parse(story_text=story_md)
            return {"ok": True, "result": req.model_dump()}
        if method == "generate_test_cases":
            requirement_graph = RequirementGraph(**params.get("requirement_graph"))
            coverage = params.get("coverage", "comprehensive")
            suite = TestCaseGenerator(LLMOrchestrator()).generate(requirement_graph, coverage=coverage)
            return {"ok": True, "result": suite.model_dump()}
        if method == "synthesize_scripts":
            requirement_graph = RequirementGraph(**params.get("requirement_graph"))
            suite = TestSuite(**params.get("test_suite"))
            cfg = ExecutionConfig(
                uiMode=params.get("ui_mode", "real"),
                apiMode=params.get("api_mode", "mock"),
            )
            out_dir = Path(params.get("out_dir", "tests/generated/mcp"))
            files = CodeSynthesizer().synthesize(requirement_graph, suite, cfg, out_dir)
            return {"ok": True, "result": {k: str(v) for k, v in files.items()}}
        if method == "run_tests":
            # Simple local run via pytest for generated dir
            out_dir = Path(params.get("test_dir", "tests/generated/mcp"))
            ui_mode = params.get("ui_mode", "real")
            api_mode = params.get("api_mode", "mock")
            import subprocess

            cmd = ["pytest", str(out_dir), "-q", "--tb=short", f"--ui-mode={ui_mode}", f"--api-mode={api_mode}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return {
                "ok": True,
                "result": {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                },
            }
        raise ToolError(f"Unknown method: {method}")
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Transports
async def stdio_server() -> None:
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, asyncio.StreamReader())
    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(asyncio.streams.FlowControlMixin, asyncio.StreamWriter)
    # Fallback: simple stdin/stdout loop using anyio for portability would be better; using sys.stdin/sys.stdout here
    import sys
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
        except Exception:
            print(json.dumps({"ok": False, "error": "invalid_json"}))
            sys.stdout.flush()
            continue
        resp = await mcp_handle_request(req)
        print(json.dumps(resp))
        sys.stdout.flush()


async def websocket_server(host: str, port: int) -> None:
    import websockets

    async def handler(websocket):
        async for message in websocket:
            try:
                req = json.loads(message)
            except Exception:
                await websocket.send(json.dumps({"ok": False, "error": "invalid_json"}))
                continue
            resp = await mcp_handle_request(req)
            await websocket.send(json.dumps(resp))

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
