from typing import List, Any
from pydantic import BaseModel, Field

class VerificationReport(BaseModel):
    passed: bool
    critical_failures: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    preserved_invariants: List[Any] = Field(default_factory=list)
    changed_invariants: List[Any] = Field(default_factory=list)
    missing_invariants: List[Any] = Field(default_factory=list)
    confidence: float = 1.0

class CompressionProof(BaseModel):
    original_hash: str
    invariant_hash: str
    candidate_hash: str
    verified: bool
    exact_reconstruction: bool
    preservation_contract: str
    preserved: int
    changed: int
    warnings: List[str] = Field(default_factory=list)
    compressor_chain: List[str] = Field(default_factory=list)
