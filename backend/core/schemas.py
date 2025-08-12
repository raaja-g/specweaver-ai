"""
Pydantic models for RequirementGraph and TestCase schemas
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class AcceptanceCriteria(BaseModel):
    """Single acceptance criteria in Given-When-Then format"""
    id: str = Field(..., description="Unique ID for this AC")
    given: str = Field(..., description="Precondition")
    when: str = Field(..., description="Action/trigger")
    then: str = Field(..., description="Expected outcome")
    notes: Optional[str] = Field(None, description="Additional notes")


class DomainEntity(BaseModel):
    """Domain entity referenced in the requirement"""
    name: str = Field(..., description="Entity name (e.g., Product, User)")
    fields: List[str] = Field(default_factory=list, description="Entity fields")


class RequirementGraph(BaseModel):
    """Structured representation of a user story"""
    id: str = Field(..., description="Unique identifier for the requirement")
    title: str = Field(..., description="Title of the requirement")
    actor: str = Field(..., description="Who wants the feature")
    goal: str = Field(..., description="What they want to achieve")
    benefit: str = Field(..., description="Why they want it")
    preconditions: List[str] = Field(default_factory=list, description="Preconditions for the requirement")
    acceptanceCriteria: List[AcceptanceCriteria] = Field(..., description="Acceptance criteria in Given-When-Then format")
    constraints: List[str] = Field(default_factory=list, description="Constraints for the requirement")
    domainEntities: List[DomainEntity] = Field(default_factory=list, description="Domain entities involved")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions about the system")
    risks: List[str] = Field(default_factory=list, description="Potential risks")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    url: Optional[str] = Field(None, description="URL of the application to test (for dynamic generation)")
    raw_text: Optional[str] = Field(None, description="Original user input to pass directly to LLM for BDD generation")
    domain: Optional[str] = Field(None, description="Domain hint")
    version: str = Field(default="1.0.0", description="Schema version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    provider_metadata: Optional[Dict[str, Any]] = Field(None, description="LLM provider info")


class TestStep(BaseModel):
    """Single step in a test case"""
    action: str = Field(..., description="Semantic action (e.g., product.add_to_cart)")
    params: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")


class TestCase(BaseModel):
    """Structured test case"""
    id: str = Field(..., description="Test case ID (e.g., TC-CHK-001)")
    title: str = Field(..., description="Test case title")
    priority: Literal["P0", "P1", "P2", "P3"] = Field(..., description="Priority level")
    type: Literal["positive", "negative", "edge"] = Field(..., description="Test type")
    traceTo: List[str] = Field(..., description="AC IDs this test covers")
    preconditions: List[str] = Field(default_factory=list)
    steps: List[TestStep]
    data: Dict[str, Any] = Field(default_factory=dict, description="Test data")
    expected: List[str] = Field(..., description="Expected outcomes")
    tags: List[str] = Field(default_factory=list)
    domain: Optional[str] = Field(None, description="Inherited from RequirementGraph")
    version: str = Field(default="1.0.0", description="Schema version")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TestSuite(BaseModel):
    """Collection of test cases"""
    requirement_id: str
    test_cases: List[TestCase]
    coverage_metrics: Dict[str, Any] = Field(default_factory=dict)
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionConfig(BaseModel):
    """Execution mode configuration"""
    uiMode: Literal["real", "mock"] = Field(default="real")
    apiMode: Literal["mock", "stub", "real"] = Field(default="mock")
    target_url: Optional[str] = Field(None)
    timeout: int = Field(default=30000, description="Timeout in ms")
    parallel: bool = Field(default=True)
    retry_count: int = Field(default=2)


class LocatorEntry(BaseModel):
    """Single locator mapping"""
    action: str
    selector: str
    method: Literal["click", "fill", "select", "hover", "wait"]
    params: Optional[Dict[str, Any]] = None


class LocatorRepository(BaseModel):
    """Collection of UI locators"""
    version: int = Field(default=1)
    pages: Dict[str, Dict[str, List[Dict[str, Any]]]]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    auto_generated: bool = Field(default=True)
    confidence_scores: Optional[Dict[str, float]] = None
