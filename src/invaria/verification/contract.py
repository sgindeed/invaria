from typing import List, Set
from pydantic import BaseModel, Field

class PreservationContract(BaseModel):
    strictness: str = "strict"
    required: Set[str] = Field(default_factory=lambda: {
        "entities",
        "facts",
        "constraints",
        "numbers",
        "dates",
        "instructions"
    })
    verification_level: str = "CRITICAL"
