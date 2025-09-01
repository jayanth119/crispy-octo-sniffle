import os 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.google import llm
from Schemas.useCaseSchema import UseCaseOutput
from agno.agent import Agent

usecase_agent = Agent(
    name="Use Case Agent",
    role="List real-world applications and industries.",
    model=llm,
    response_model=UseCaseOutput,
    use_json_mode=True,
    markdown=False,
)

