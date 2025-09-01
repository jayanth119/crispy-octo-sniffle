from __future__ import annotations
from typing import Optional

from pydantic import BaseModel



class CodeSnippet(BaseModel):
    language: str
    title: str
    code: str
    notes: Optional[str] = None
