import re
from typing import List
from .base import Compressor
from ..config import InvariaConfig
from ..ir.models import SemanticGraph

class LexicalCompressor(Compressor):
    name: str = "lexical"

    def can_handle(self, context: str, ir: SemanticGraph, config: InvariaConfig) -> bool:
        return True

    def generate_candidates(self, context: str, ir: SemanticGraph, config: InvariaConfig) -> List[str]:
        # Basic deterministic lexical transformations
        
        # 1. Whitespace normalization
        normalized = re.sub(r'\s+', ' ', context).strip()
        
        # 2. Duplicate punctuation cleanup
        cleaned = re.sub(r'([.?!,])\1+', r'\1', normalized)
        
        candidates = [normalized]
        if cleaned != normalized:
            candidates.append(cleaned)
            
        return candidates

    def estimate_cost(self, candidate: str, config: InvariaConfig) -> float:
        # Simple heuristic: length of string as a proxy for token cost
        # In later phases, use actual tokenizer
        return float(len(candidate))
