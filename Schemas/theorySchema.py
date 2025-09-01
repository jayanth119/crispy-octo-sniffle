from __future__ import annotations
from typing import List

from pydantic import BaseModel, Field
class TheoryOutput(BaseModel):
    overview: str
    key_concepts: List[str]
    mechanism: str
    cautions: List[str] = Field(default_factory=list)
