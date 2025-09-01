from __future__ import annotations
from typing import List

from pydantic import BaseModel, Field
import os 
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Schemas.theorySchema import TheoryOutput
from Schemas.codeOutputSchema import CodeOutput
from Schemas.exampleSchema import ExampleOutput
from Schemas.useCaseSchema import UseCaseOutput

class KnowledgeBundle(BaseModel):
    topic: str
    theory: TheoryOutput
    code: CodeOutput
    examples: ExampleOutput
    use_cases: UseCaseOutput
    suggested_subtopics: List[str] = Field(default_factory=list)
