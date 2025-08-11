"""
Requirement Parser - Parses user stories into RequirementGraph
"""
import json
import re
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from .schemas import RequirementGraph, AcceptanceCriteria, DomainEntity
from .llm_orchestrator import LLMOrchestrator

logger = logging.getLogger(__name__)


class RequirementParser:
    """Parse user stories into structured RequirementGraph"""
    
    def __init__(self, orchestrator: Optional[LLMOrchestrator] = None):
        self.orchestrator = orchestrator or LLMOrchestrator()
        self.schema = self._get_requirement_schema()
    
    def _get_requirement_schema(self) -> Dict[str, Any]:
        """Get RequirementGraph JSON schema"""
        return {
            "type": "object",
            "required": ["id", "title", "actor", "goal", "benefit", "acceptanceCriteria"],
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "actor": {"type": "string"},
                "goal": {"type": "string"},
                "benefit": {"type": "string"},
                "acceptanceCriteria": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "given", "when", "then"],
                        "properties": {
                            "id": {"type": "string"},
                            "given": {"type": "string"},
                            "when": {"type": "string"},
                            "then": {"type": "string"}
                        }
                    }
                }
            }
        }
    
    def _extract_story_parts(self, story: str) -> Dict[str, Any]:
        """Extract parts from user story using regex"""
        parts = {
            "actor": "",
            "goal": "",
            "benefit": "",
            "acceptance_criteria": []
        }
        
        # Try to match "As a... I want... so that..." pattern
        story_pattern = r"As a\s+(.+?)[,\s]+I want\s+(.+?)\s+so that\s+(.+?)(?:\.|$)"
        if match := re.search(story_pattern, story, re.IGNORECASE):
            parts["actor"] = match.group(1).strip()
            parts["goal"] = match.group(2).strip()
            parts["benefit"] = match.group(3).strip()
        
        # Extract acceptance criteria
        ac_section = re.search(r"Acceptance Criteria:?\s*(.+)", story, re.IGNORECASE | re.DOTALL)
        if ac_section:
            ac_text = ac_section.group(1)
            # Look for Given-When-Then patterns
            gwt_pattern = r"Given\s+(.+?)[,\s]+when\s+(.+?)[,\s]+then\s+(.+?)(?:\.|$)"
            for match in re.finditer(gwt_pattern, ac_text, re.IGNORECASE):
                parts["acceptance_criteria"].append({
                    "given": match.group(1).strip(),
                    "when": match.group(2).strip(),
                    "then": match.group(3).strip()
                })
            
            # Also look for bullet points
            if not parts["acceptance_criteria"]:
                for line in ac_text.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        parts["acceptance_criteria"].append({"text": line[1:].strip()})
        
        return parts
    
    def _build_prompt(self, story: str, extracted_parts: Dict[str, Any]) -> str:
        """Build prompt for LLM"""
        return f"""
Parse this user story into a structured RequirementGraph JSON.

User Story:
{story}

Extracted hints:
- Actor: {extracted_parts.get('actor', 'not found')}
- Goal: {extracted_parts.get('goal', 'not found')}
- Benefit: {extracted_parts.get('benefit', 'not found')}
- Acceptance Criteria found: {len(extracted_parts.get('acceptance_criteria', []))}

Generate a complete RequirementGraph with:
1. Unique ID (e.g., REQ-001)
2. Clear title summarizing the story
3. Actor, goal, and benefit
4. All acceptance criteria in Given-When-Then format
5. Relevant domain entities (Product, Cart, Order, etc.)
6. Any assumptions and risks
7. Appropriate tags

Return ONLY valid JSON matching the RequirementGraph schema.
"""
    
    def parse(self, story_path: Optional[Path] = None, story_text: Optional[str] = None) -> RequirementGraph:
        """
        Parse user story into RequirementGraph
        
        Args:
            story_path: Path to story file (.md, .txt, .docx)
            story_text: Story text directly
        """
        # Load story
        if story_path:
            story_text = Path(story_path).read_text()
        elif not story_text:
            raise ValueError("Either story_path or story_text must be provided")
        
        # Extract parts using regex
        extracted = self._extract_story_parts(story_text)
        
        # Build prompt
        prompt = self._build_prompt(story_text, extracted)
        
        # Call LLM
        system_prompt = """You are an expert requirements analyst. 
Parse user stories into structured JSON following the RequirementGraph schema exactly.
Focus on clarity, completeness, and testability of acceptance criteria."""
        
        response = self.orchestrator.call(
            prompt=prompt,
            system=system_prompt,
            task_type="parsing"
        )
        
        # Validate and repair if needed
        valid, error = self.orchestrator.validate_json_response(response.content, self.schema)
        if not valid:
            logger.warning(f"Initial parse invalid: {error}")
            repaired = self.orchestrator.repair_json(response.content, error, self.schema)
            if repaired:
                response.content = repaired
            else:
                # Fallback: create minimal valid structure
                response.content = self._create_fallback_graph(story_text, extracted)
        
        # Parse to Pydantic model
        try:
            data = json.loads(response.content)
            # Add metadata
            data["provider_metadata"] = {
                "provider": response.provider.value,
                "model": response.model,
                "latency_ms": response.latency_ms
            }
            return RequirementGraph(**data)
        except Exception as e:
            logger.error(f"Failed to create RequirementGraph: {e}")
            # Return minimal valid graph
            return self._create_minimal_graph(story_text, extracted)
    
    def _create_fallback_graph(self, story: str, extracted: Dict[str, Any]) -> str:
        """Create fallback RequirementGraph JSON"""
        graph = {
            "id": "REQ-001",
            "title": extracted.get("goal", "User Story")[:100],
            "actor": extracted.get("actor", "user"),
            "goal": extracted.get("goal", "perform action"),
            "benefit": extracted.get("benefit", "achieve outcome"),
            "acceptanceCriteria": [],
            "domainEntities": [],
            "assumptions": [],
            "risks": [],
            "tags": ["auto-generated", "needs-review"]
        }
        
        # Add acceptance criteria
        for i, ac in enumerate(extracted.get("acceptance_criteria", []), 1):
            if "given" in ac:
                graph["acceptanceCriteria"].append({
                    "id": f"AC-{i}",
                    "given": ac["given"],
                    "when": ac["when"],
                    "then": ac["then"]
                })
            elif "text" in ac:
                # Try to parse text into GWT
                graph["acceptanceCriteria"].append({
                    "id": f"AC-{i}",
                    "given": "the system is ready",
                    "when": "user performs action",
                    "then": ac["text"]
                })
        
        # If no AC found, create one from the goal
        if not graph["acceptanceCriteria"]:
            graph["acceptanceCriteria"].append({
                "id": "AC-1",
                "given": f"I am a {graph['actor']}",
                "when": f"I {graph['goal']}",
                "then": f"I {graph['benefit']}"
            })
        
        return json.dumps(graph)
    
    def _create_minimal_graph(self, story: str, extracted: Dict[str, Any]) -> RequirementGraph:
        """Create minimal valid RequirementGraph"""
        return RequirementGraph(
            id="REQ-001",
            title=extracted.get("goal", "User Story")[:100],
            actor=extracted.get("actor", "user"),
            goal=extracted.get("goal", "perform action"),
            benefit=extracted.get("benefit", "achieve outcome"),
            acceptanceCriteria=[
                AcceptanceCriteria(
                    id="AC-1",
                    given="the system is ready",
                    when="user performs the action",
                    then="the expected outcome occurs"
                )
            ],
            domainEntities=[],
            assumptions=["System is accessible", "User has valid credentials"],
            risks=["Network failures", "Data validation errors"],
            tags=["minimal", "needs-enrichment"]
        )
