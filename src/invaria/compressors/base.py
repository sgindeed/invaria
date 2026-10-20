from abc import ABC, abstractmethod
from typing import Any, List, Optional
from ..config import InvariaConfig
from ..ir.models import SemanticGraph

class Compressor(ABC):
    name: str

    @abstractmethod
    def can_handle(self, context: str, ir: SemanticGraph, config: InvariaConfig) -> bool:
        pass

    @abstractmethod
    def generate_candidates(self, context: str, ir: SemanticGraph, config: InvariaConfig) -> List[str]:
        pass

    @abstractmethod
    def estimate_cost(self, candidate: str, config: InvariaConfig) -> float:
        pass
