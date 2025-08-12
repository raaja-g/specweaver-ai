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
    
    def _extract_json_snippet(self, raw: str) -> str:
        """Extract a JSON object/array from raw LLM output (strips code fences, prefaces)."""
        if not raw:
            return ""
        text = raw.strip()
        # Strip code fences if present
        if text.startswith("```"):
            # remove first fence line and trailing fence
            try:
                first_nl = text.find("\n")
                text = text[first_nl+1:]
                if text.endswith("```"):
                    text = text[: -3]
            except Exception:
                pass
        # Find JSON object or array
        s_obj, e_obj = text.find("{"), text.rfind("}")
        s_arr, e_arr = text.find("["), text.rfind("]")
        if s_obj != -1 and e_obj != -1 and e_obj > s_obj:
            return text[s_obj: e_obj + 1]
        if s_arr != -1 and e_arr != -1 and e_arr > s_arr:
            return text[s_arr: e_arr + 1]
        return text

    def _coerce_gwt_from_text(self, text: str) -> tuple[str, str, str]:
        """Best-effort extraction of Given/When/Then from a description string."""
        try:
            # Simple regex for Given/When/Then order
            m = re.search(r"Given\s+(.+?)\s+When\s+(.+?)\s+Then\s+(.+)", text, re.IGNORECASE | re.DOTALL)
            if m:
                return m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
        except Exception:
            pass
        # Fallback generic
        return ("the system is ready", "user performs the action", "the expected outcome occurs")

    def _extract_story_parts(self, story: str) -> Dict[str, Any]:
        """Extract parts from user story using regex"""
        parts = {
            "actor": "",
            "goal": "",
            "benefit": "",
            "acceptance_criteria": [],
            "url": ""
        }
        
        # Extract URL if present
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, story)
        if url_match:
            parts["url"] = url_match.group(0)
            logger.info(f"Extracted URL: {parts['url']}")
        else:
            # Also try to extract domain-like patterns
            domain_pattern = r'(?:test|check|verify)\s+(?:the\s+)?(?:website\s+)?(?:at\s+)?(?:https?://)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            domain_match = re.search(domain_pattern, story, re.IGNORECASE)
            if domain_match:
                domain = domain_match.group(1)
                if not domain.startswith(('http://', 'https://')):
                    parts["url"] = f"https://{domain}"
                else:
                    parts["url"] = domain
                logger.info(f"Extracted domain URL: {parts['url']}")
            else:
                logger.info("No URL or domain found in input")
        
        logger.info(f"Final extracted parts: {parts}")
        
        # Try to match "As a... I want... so that..." pattern
        story_pattern = r"As a\s+(.+?)[,\s]+I want\s+(.+?)\s+so that\s+(.+?)(?:\.|$)"
        if match := re.search(story_pattern, story, re.IGNORECASE):
            parts["actor"] = match.group(1).strip()
            parts["goal"] = match.group(2).strip()
            parts["benefit"] = match.group(3).strip()
        else:
            # Handle free-form text - extract meaningful parts
            if "test" in story.lower():
                parts["actor"] = "tester"
                if "ecommerce" in story.lower() or "commerce" in story.lower():
                    parts["goal"] = "test the e-commerce website functionality"
                    parts["benefit"] = "ensure the website works correctly for users"
                elif "site" in story.lower() or "website" in story.lower():
                    parts["goal"] = "test the website functionality"
                    parts["benefit"] = "ensure the website meets quality standards"
                else:
                    parts["goal"] = "test the application"
                    parts["benefit"] = "ensure quality and functionality"
            elif "user" in story.lower():
                parts["actor"] = "user"
                parts["goal"] = "use the application"
                parts["benefit"] = "accomplish their tasks"
            else:
                parts["actor"] = "user"
                parts["goal"] = story.strip()
                parts["benefit"] = "meet their requirements"
        
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
        
        logger.info(f"Parsing story text: {story_text[:100]}...")
        
        # Extract parts using regex
        extracted = self._extract_story_parts(story_text)
        logger.info(f"Extracted parts: {extracted}")
        
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
        snippet = self._extract_json_snippet(response.content or "")
        valid, error = self.orchestrator.validate_json_response(snippet, self.schema)
        if not valid:
            logger.info("Parser: non-JSON/invalid JSON from LLM; attempting repair/fallback")
            repaired = self.orchestrator.repair_json(snippet, error, self.schema)
            if repaired:
                snippet = self._extract_json_snippet(repaired)
            else:
                # Fallback: create minimal valid structure
                snippet = self._create_fallback_graph(story_text, extracted)
        
        # Parse to Pydantic model
        try:
            raw = (snippet or "").strip()
            if not raw:
                raise ValueError("Empty LLM response")
            data = json.loads(raw)
            
            # Coerce/normalize common LLM schema deviations before validation
            try:
                # actor, title, goal, benefit may come as objects
                if isinstance(data.get("actor"), dict):
                    actor_obj = data.get("actor") or {}
                    data["actor"] = actor_obj.get("name") or actor_obj.get("role") or actor_obj.get("value") or "user"
                if isinstance(data.get("title"), dict):
                    data["title"] = data["title"].get("text") or data["title"].get("value") or "User Story"
                if isinstance(data.get("goal"), dict):
                    data["goal"] = data["goal"].get("text") or data["goal"].get("value") or "perform action"
                if isinstance(data.get("benefit"), dict):
                    data["benefit"] = data["benefit"].get("text") or data["benefit"].get("value") or "achieve outcome"
                # version as string
                if "version" in data and not isinstance(data["version"], str):
                    data["version"] = str(data["version"]) 
                # acceptanceCriteria coercion
                ac_list = data.get("acceptanceCriteria") or []
                coerced_ac = []
                for i, ac in enumerate(ac_list, 1):
                    if not isinstance(ac, dict):
                        # try to parse from a text line
                        text = str(ac)
                        given, when, then = self._coerce_gwt_from_text(text)
                        coerced_ac.append({"id": f"AC-{i}", "given": given, "when": when, "then": then})
                        continue
                    g = ac.get("given") or ac.get("Given")
                    w = ac.get("when") or ac.get("When")
                    t = ac.get("then") or ac.get("Then")
                    if not (g and w and t):
                        # try description field
                        desc = ac.get("description") or ac.get("text") or ""
                        if desc:
                            g2, w2, t2 = self._coerce_gwt_from_text(desc)
                            g = g or g2
                            w = w or w2
                            t = t or t2
                    coerced_ac.append({
                        "id": ac.get("id") or f"AC-{i}",
                        "given": g or "the system is ready",
                        "when": w or "user performs the action",
                        "then": t or "the expected outcome occurs"
                    })
                if coerced_ac:
                    data["acceptanceCriteria"] = coerced_ac
            except Exception:
                logger.exception("Parser: normalization step failed; proceeding with raw data")

            # Ensure URL is preserved from extracted parts
            if extracted.get("url") and not data.get("url"):
                data["url"] = extracted["url"]
                logger.info(f"Added extracted URL to LLM response: {data['url']}")
            
            # Repair domainEntities if needed
            if "domainEntities" in data and isinstance(data["domainEntities"], list):
                repaired_entities = []
                for ent in data["domainEntities"]:
                    if isinstance(ent, str):
                        repaired_entities.append({
                            "name": ent,
                            "description": f"Extracted entity: {ent}"
                        })
                    elif isinstance(ent, dict):
                        repaired_entities.append(ent)
                data["domainEntities"] = repaired_entities
            
            # Add metadata
            data["provider_metadata"] = {
                "provider": response.provider.value,
                "model": response.model,
                "latency_ms": response.latency_ms
            }
            
            logger.info(f"Final RequirementGraph data: {data}")
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
            "url": extracted.get("url", ""),
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
            url=extracted.get("url", ""),
            acceptanceCriteria=[
                AcceptanceCriteria(id="AC-1", given="the system is ready", when="user performs the action", then="the expected outcome occurs"),
                AcceptanceCriteria(id="AC-2", given="the application is accessible", when="I navigate to the homepage", then="the homepage loads successfully"),
            ],
            domainEntities=[],
            assumptions=["System is accessible", "User has valid credentials"],
            risks=["Network failures", "Data validation errors"],
            tags=["minimal", "needs-enrichment"]
        )
