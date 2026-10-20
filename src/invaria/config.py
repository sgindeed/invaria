from typing import Optional, Literal
from pydantic import BaseModel, Field

class InvariaConfig(BaseModel):
    mode: Literal["semantic", "invariant", "reversible"] = "invariant"
    provider: Optional[str] = None
    model: Optional[str] = None
    tokenizer: Optional[str] = None
    verify: bool = True
    logging_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    
    # Optimizer settings
    target_tokens: Optional[int] = None
