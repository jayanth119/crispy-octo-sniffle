from __future__ import annotations
from typing import List, Optional

from pydantic import BaseModel, Field


class UseCaseOutput(BaseModel):
    applications: List[str]
    industries: List[str]
    maturity_notes: Optional[str] = None


