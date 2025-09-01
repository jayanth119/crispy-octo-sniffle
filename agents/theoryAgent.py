import os 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.google import llm
from Schemas.theorySchema import TheoryOutput
from agno.agent import Agent




theory_agent = Agent(
    name="Theory Agent",
    role="Explain the theory clearly and concisely.",
    model=llm,
    response_model=TheoryOutput,
    use_json_mode=True,
    markdown=False,
)
