"""
MCP Server skeleton exposing SpecWeaver tools (parse/generate/synthesize)
"""
import json
from typing import Dict
from backend.core.requirement_parser import RequirementParser
from backend.core.llm_orchestrator import LLMOrchestrator
from backend.core.test_generator import TestCaseGenerator
from backend.core.code_synthesizer import CodeSynthesizer
from backend.core.schemas import RequirementGraph, TestSuite, ExecutionConfig
from pathlib import Path


def parse_requirement(story_md: str) -> str:
    req = RequirementParser(LLMOrchestrator()).parse(story_text=story_md)
    return req.model_dump_json(indent=2)


def generate_test_cases(requirement_graph_json: str, coverage: str = "comprehensive") -> str:
    req = RequirementGraph(**json.loads(requirement_graph_json))
    suite = TestCaseGenerator(LLMOrchestrator()).generate(req, coverage=coverage)
    return suite.model_dump_json(indent=2)


def synthesize_scripts(test_cases_json: str, requirement_graph_json: str, ui_mode: str = "real", api_mode: str = "mock") -> Dict[str, str]:
    req = RequirementGraph(**json.loads(requirement_graph_json))
    suite = TestSuite(**json.loads(test_cases_json))
    cfg = ExecutionConfig(uiMode=ui_mode, apiMode=api_mode)
    out_dir = Path("tests/generated/mcp")
    files = CodeSynthesizer().synthesize(req, suite, cfg, out_dir)
    return {k: str(v) for k, v in files.items()}
