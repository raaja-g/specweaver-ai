#!/usr/bin/env python3
"""
SpecWeaver CLI - Parse requirements and generate test cases
"""
import json
import logging
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track

from backend.core.schemas import ExecutionConfig, RequirementGraph, TestSuite
from backend.core.llm_orchestrator import LLMOrchestrator, LLMProvider
from backend.core.requirement_parser import RequirementParser  
from backend.core.test_generator import TestCaseGenerator
from backend.core.code_synthesizer import CodeSynthesizer

# Setup
app = typer.Typer(help="SpecWeaver - Automated Test Generation from Requirements")
console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def parse(
    story: Path = typer.Argument(..., help="Path to user story file"),
    output: Path = typer.Option(Path("artifacts"), help="Output directory"),
    provider: Optional[str] = typer.Option(None, help="Force LLM provider (groq/gemini/openai/local)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Parse user story into RequirementGraph"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Parsing story:[/bold blue] {story}")
    
    # Initialize orchestrator
    orchestrator = LLMOrchestrator()
    if provider:
        force_provider = LLMProvider[provider.upper()]
    else:
        force_provider = None
    
    # Parse requirement
    parser = RequirementParser(orchestrator)
    requirement = parser.parse(story_path=story)
    
    # Save output
    output.mkdir(parents=True, exist_ok=True)
    req_file = output / "requirement_graph.json"
    req_file.write_text(requirement.model_dump_json(indent=2))
    
    # Display summary
    console.print(f"[green]✓[/green] Parsed requirement: {requirement.title}")
    console.print(f"  Actor: {requirement.actor}")
    console.print(f"  Goal: {requirement.goal}")
    console.print(f"  Acceptance Criteria: {len(requirement.acceptanceCriteria)}")
    console.print(f"  Output: {req_file}")


@app.command()
def generate(
    requirement: Path = typer.Argument(..., help="Path to requirement_graph.json"),
    output: Path = typer.Option(Path("artifacts"), help="Output directory"),
    coverage: str = typer.Option("comprehensive", help="Coverage level (basic/comprehensive)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Generate test cases from RequirementGraph"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Generating test cases:[/bold blue] {requirement}")
    
    # Load requirement
    req_data = json.loads(requirement.read_text())
    req = RequirementGraph(**req_data)
    
    # Generate test cases
    orchestrator = LLMOrchestrator()
    generator = TestCaseGenerator(orchestrator)
    test_suite = generator.generate(req, coverage=coverage)
    
    # Save output
    output.mkdir(parents=True, exist_ok=True)
    tests_file = output / "test_cases.json"
    tests_file.write_text(test_suite.model_dump_json(indent=2))
    
    # Display summary
    table = Table(title="Generated Test Cases")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Priority")
    
    for tc in test_suite.test_cases:
        table.add_row(tc.id, tc.title[:40], tc.type, tc.priority)
    
    console.print(table)
    console.print(f"\n[green]✓[/green] Generated {len(test_suite.test_cases)} test cases")
    console.print(f"  Coverage: {test_suite.coverage_metrics.get('ac_coverage', 0):.1f}%")
    console.print(f"  Output: {tests_file}")


@app.command()
def synthesize(
    tests: Path = typer.Argument(..., help="Path to test_cases.json"),
    requirement: Path = typer.Option(..., help="Path to requirement_graph.json"),
    output: Path = typer.Option(Path("tests/generated"), help="Output directory"),
    ui_mode: str = typer.Option("real", help="UI execution mode (real/mock)"),
    api_mode: str = typer.Option("mock", help="API execution mode (mock/stub/real)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Synthesize executable test code"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print(f"[bold blue]Synthesizing test code:[/bold blue]")
    
    # Load inputs
    req_data = json.loads(requirement.read_text())
    req = RequirementGraph(**req_data)
    
    suite_data = json.loads(tests.read_text())
    test_suite = TestSuite(**suite_data)
    
    # Create execution config
    config = ExecutionConfig(
        uiMode=ui_mode,
        apiMode=api_mode,
        target_url="https://luma.enablementadobe.com/content/luma/us/en.html"
    )
    
    # Synthesize code
    synthesizer = CodeSynthesizer()
    generated_files = synthesizer.synthesize(req, test_suite, config, output)
    
    # Display results
    console.print(f"[green]✓[/green] Generated test files:")
    for file_type, file_path in generated_files.items():
        console.print(f"  {file_type}: {file_path}")


@app.command()
def full(
    story: Path = typer.Argument(..., help="Path to user story file"),
    output: Path = typer.Option(Path("artifacts"), help="Output directory"),
    coverage: str = typer.Option("comprehensive", help="Coverage level"),
    ui_mode: str = typer.Option("real", help="UI execution mode"),
    api_mode: str = typer.Option("mock", help="API execution mode"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Full pipeline: parse -> generate -> synthesize"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    console.print("[bold green]Running full SpecWeaver pipeline[/bold green]\n")
    
    # Step 1: Parse
    console.print("[bold]Step 1: Parsing requirement...[/bold]")
    orchestrator = LLMOrchestrator()
    parser = RequirementParser(orchestrator)
    requirement = parser.parse(story_path=story)
    
    output.mkdir(parents=True, exist_ok=True)
    req_file = output / "requirement_graph.json"
    req_file.write_text(requirement.model_dump_json(indent=2))
    console.print(f"[green]✓[/green] Parsed: {requirement.title}\n")
    
    # Step 2: Generate test cases
    console.print("[bold]Step 2: Generating test cases...[/bold]")
    generator = TestCaseGenerator(orchestrator)
    test_suite = generator.generate(requirement, coverage=coverage)
    
    tests_file = output / "test_cases.json"
    tests_file.write_text(test_suite.model_dump_json(indent=2))
    console.print(f"[green]✓[/green] Generated {len(test_suite.test_cases)} test cases\n")
    
    # Step 3: Synthesize code
    console.print("[bold]Step 3: Synthesizing test code...[/bold]")
    config = ExecutionConfig(uiMode=ui_mode, apiMode=api_mode)
    synthesizer = CodeSynthesizer()
    
    test_dir = Path("tests/generated")
    generated_files = synthesizer.synthesize(requirement, test_suite, config, test_dir)
    
    console.print(f"[green]✓[/green] Generated {len(generated_files)} files\n")
    
    # Summary
    console.print("[bold green]Pipeline Complete![/bold green]")
    console.print(f"  Requirement: {requirement.title}")
    console.print(f"  Test Cases: {len(test_suite.test_cases)}")
    console.print(f"  Coverage: {test_suite.coverage_metrics.get('ac_coverage', 0):.1f}%")
    console.print(f"  Output: {output}")
    console.print(f"  Tests: {test_dir}")
    console.print(f"\n[yellow]Run tests with:[/yellow] pytest {test_dir}")


@app.command()
def validate(
    requirement: Path = typer.Argument(..., help="Path to requirement_graph.json"),
    tests: Path = typer.Argument(..., help="Path to test_cases.json")
):
    """Validate artifacts for completeness and consistency"""
    console.print("[bold blue]Validating artifacts...[/bold blue]")
    
    # Load artifacts
    req_data = json.loads(requirement.read_text())
    req = RequirementGraph(**req_data)
    
    suite_data = json.loads(tests.read_text())
    test_suite = TestSuite(**suite_data)
    
    issues = []
    
    # Check AC coverage
    ac_ids = {ac.id for ac in req.acceptanceCriteria}
    covered_acs = set()
    for tc in test_suite.test_cases:
        covered_acs.update(tc.traceTo)
    
    uncovered = ac_ids - covered_acs
    if uncovered:
        issues.append(f"Uncovered ACs: {uncovered}")
    
    # Check test types
    types = {tc.type for tc in test_suite.test_cases}
    if "positive" not in types:
        issues.append("No positive test cases")
    
    # Display results
    if issues:
        console.print("[red]Validation issues found:[/red]")
        for issue in issues:
            console.print(f"  • {issue}")
    else:
        console.print("[green]✓ All validations passed[/green]")
    
    # Coverage report
    coverage = len(covered_acs) / len(ac_ids) * 100 if ac_ids else 0
    console.print(f"\nCoverage: {coverage:.1f}% ({len(covered_acs)}/{len(ac_ids)} ACs)")


if __name__ == "__main__":
    app()
