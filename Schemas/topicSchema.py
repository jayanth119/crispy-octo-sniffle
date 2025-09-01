from __future__ import annotations
from typing import List, Optional, Dict


from pydantic import BaseModel, Field
class TopicExtraction(BaseModel):
    topic: str
    confidence: float = Field(..., ge=0, le=1)
    subtopics: List[str] = Field(default_factory=list)
    rationale: Optional[str] = None