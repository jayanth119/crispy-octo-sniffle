from __future__ import annotations
from typing import Optional, Dict


from pydantic import BaseModel

class ExampleOutput(BaseModel):
    simple_analogy: str
    io_example: Optional[Dict[str, str]] = None
    explanation: str


