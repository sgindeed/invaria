from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SourceSpan(BaseModel):
    start_char: int
    end_char: int
    text: str

class SemanticNode(BaseModel):
    id: str
    type: str
    value: Any
    normalized_value: Optional[Any] = None
    source_span: Optional[SourceSpan] = None
    confidence: float = 1.0
    provenance: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Entity(SemanticNode):
    type: str = "entity"

class Fact(SemanticNode):
    type: str = "fact"
    subject: str
    predicate: str
    object: str

class Constraint(SemanticNode):
    type: str = "constraint"
    polarity: str = "positive" # "positive" or "negative"

class NumericalInvariant(SemanticNode):
    type: str = "number"
    unit: Optional[str] = None

class TemporalInvariant(SemanticNode):
    type: str = "temporal"
    relation: str = "at" # "before", "after", "at"

class Instruction(SemanticNode):
    type: str = "instruction"
    modality: str = "must" # "must", "should", "may", etc.

class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SemanticGraph(BaseModel):
    nodes: Dict[str, SemanticNode] = Field(default_factory=dict)
    edges: List[GraphEdge] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
