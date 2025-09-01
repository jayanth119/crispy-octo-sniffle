import os 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agno.agent import Agent
from models.google import llm 
from Schemas.codeOutputSchema import CodeOutput

code_agent = Agent(
    name="Code Agent",
    role="Provide code examples if applicable.",
    model=llm,
    response_model=CodeOutput,
    use_json_mode=True,
    markdown=False,
)

