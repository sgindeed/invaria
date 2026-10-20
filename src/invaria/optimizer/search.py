from typing import List, Tuple
from ..config import InvariaConfig

class Optimizer:
    def __init__(self, config: InvariaConfig):
        self.config = config

    def select_best(self, valid_candidates: List[str], costs: List[float]) -> str:
        if not valid_candidates:
            raise ValueError("No valid candidates provided to the optimizer.")
        
        # Simple greedy search: select the one with the lowest cost
        best_idx = costs.index(min(costs))
        return valid_candidates[best_idx]
