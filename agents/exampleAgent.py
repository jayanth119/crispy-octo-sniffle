import os 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Schemas.exampleSchema import ExampleOutput
from models.google import llm
from agno.agent import Agent




example_agent = Agent(
    name="Example Agent",
    role="Generate analogy and optional I/O example.",
    model=llm,
    response_model=ExampleOutput,
    use_json_mode=True,
    markdown=False,
)
