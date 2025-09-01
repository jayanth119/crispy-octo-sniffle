from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
import os 
import sys 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    
from Schemas.codeSchema import CodeSnippet

class CodeOutput(BaseModel):
    supported: bool
    primary: Optional[CodeSnippet] = None
    alternates: List[CodeSnippet] = Field(default_factory=list)
