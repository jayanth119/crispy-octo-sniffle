import os 
import sys 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.google import llm
from agents.codeAgent import code_agent
from agents.exampleAgent import example_agent
from agents.theoryAgent import theory_agent
from agents.usecaseAgent import usecase_agent

from agno.team import Team



knowledge_team = Team(
    name="Knowledge Team",
    mode="coordinate",
    members=[theory_agent, code_agent, example_agent, usecase_agent],
    model=llm,
    show_members_responses=True,
    markdown=True,
    instructions=["Return only the final KnowledgeBundle as JSON."],
    use_json_mode=True,
)
