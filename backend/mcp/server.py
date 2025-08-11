"""
MCP Server skeleton exposing SpecWeaver tools
"""
import json
from typing import Any, Dict

# Placeholder skeleton; implement real MCP protocol handling in production

def parse_requirement(story_md: str) -> str:
    from backend.core.requirement_parser import RequirementParser
    from backend.core.llm_orchestrator import LLMOrchestrator
    parser = RequirementParser(LLMOrchestrator())
    req = parser.parse(story_text=story_md)
    return req.model_dump_json(indent=2)


def generate_test_cases(requirement_graph_json: str, coverage: str = "comprehensive") -> str:
    from backend.core.schemas import RequirementGraph
    from backend.core.llm_orchestrator import LLMOrchestrator
    from backend.core.test_generator import TestCaseGenerator
    req = RequirementGraph(**json.loads(requirement_graph_json))
    suite = TestCaseGenerator(LLMOrchestrator()).generate(req, coverage=coverage)
    return suite.model_dump_json(indent=2)


def synthesize_scripts(test_cases_json: str, requirement_graph_json: str, ui_mode: str = "real", api_mode: str = "mock") -> Dict[str, str]:
    from backend.core.schemas import RequirementGraph, TestSuite, ExecutionConfig
    from backend.core.code_synthesizer import CodeSynthesizer
    import pathlib
    req = RequirementGraph(**json.loads(requirement_graph_json))
    suite = TestSuite(**json.loads(test_cases_json))
    cfg = ExecutionConfig(uiMode=ui_mode, apiMode=api_mode)
    out_dir = pathlib.Path("tests/generated/mcp")
    files = CodeSynthesizer().synthesize(req, suite, cfg, out_dir)
    return {k: str(v) for k, v in files.items()}
