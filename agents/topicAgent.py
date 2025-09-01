import os 
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
from models.google import llm
from Schemas.topicSchema import TopicExtraction 

from agno.agent import Agent


topic_agent = Agent(
    name="Topic Extractor",
    role="Identify canonical topic and propose subtopics.",
    model=llm,
    response_model=TopicExtraction,
    use_json_mode=True,
    markdown=False,
)


