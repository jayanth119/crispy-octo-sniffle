from __future__ import annotations
from rich.pretty import pprint
from agno.agent import Agent, RunResponse
from agno.team import Team
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
import os 
import sys 
import json
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Schemas.knowledgeSchema import KnowledgeBundle
from Schemas.topicSchema import TopicExtraction
from Schemas.theorySchema import TheoryOutput
from Schemas.codeOutputSchema import CodeOutput
from Schemas.exampleSchema import ExampleOutput
from Schemas.useCaseSchema import UseCaseOutput
from agents.topicAgent import topic_agent
from agents.codeAgent import code_agent
from agents.exampleAgent import example_agent
from agents.theoryAgent import theory_agent
from agents.usecaseAgent import usecase_agent
from agents.knowlodgeAgent import knowledge_team
from models.google import llm

memory_db = SqliteMemoryDb(table_name="memory", db_file="multi_agent_memory.db")
memory = Memory(db=memory_db)

def run_pipeline(user_text: str) -> KnowledgeBundle:
    # 1) Extract topic
    topic_res: RunResponse = topic_agent.run(user_text)
    print(f"Topic: {topic_res.content.topic}")
    te_content = topic_res.content
    topic_struct = te_content if isinstance(te_content, TopicExtraction) else TopicExtraction(**te_content)

    topic = topic_struct.topic

    # 2) Run content agents with safe parsing
    def safe_run(agent: Agent, prompt: str, model_class):
        res = agent.run(prompt)
        content = res.content

        # Already the correct object
        if isinstance(content, model_class):
            return content

        # Try parsing
        try:
            if isinstance(content, dict):
                # Convert dict values into strings where necessary
                normalized = {
                    k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                    for k, v in content.items()
                }
                return model_class(**normalized)

            if isinstance(content, str):
                # Try loading JSON if it looks like JSON
                try:
                    parsed = json.loads(content)
                    normalized = {
                        k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                        for k, v in parsed.items()
                    }
                    return model_class(**normalized)
                except json.JSONDecodeError:
                    # If it's just plain text, wrap it into the first field
                    first_field = list(model_class.model_fields.keys())[0]
                    return model_class(**{first_field: content})

            # Last attempt: force into schema
            return model_class(**{})
        except Exception as e:
            print(f"⚠️ Parsing failed for {agent.name}: {e}")
            # Build placeholder object with "N/A" for required fields
            fallback_data = {
                f: "N/A" for f in model_class.model_fields.keys()
            }
            return model_class(**fallback_data)



    theory = safe_run(theory_agent, f"Explain the theory of {topic}.", TheoryOutput)
    code = safe_run(code_agent, f"Provide code (if applicable) for {topic}.", CodeOutput)
    examples = safe_run(example_agent, f"Give an example for {topic}.", ExampleOutput)
    use_cases = safe_run(usecase_agent, f"List real-world use cases for {topic}.", UseCaseOutput)

    kb = KnowledgeBundle(
        topic=topic,
        theory=theory,
        code=code,
        examples=examples,
        use_cases=use_cases,
        suggested_subtopics=topic_struct.subtopics,
    )

    # ===== Save into Memory DB =====
    try:
        memory.add(
            {
                "key": f"knowledge::{topic}",       # unique identifier
                "value": kb.model_dump(),          # store dict form
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "source": "multi-agent-pipeline",
                    "user_query": user_text
                }
            }
        )
        print(f"[✅ Saved KnowledgeBundle for topic '{topic}' into DB]")
    except Exception as e:
        print(f"⚠️ Failed to save KnowledgeBundle: {e}")

    return kb


if __name__ == "__main__":
    router = Team(
        name="Recursive Knowledge Router",
        mode="route",
        members=[topic_agent, knowledge_team],
        model=llm,
        memory=memory,
        add_history_to_messages=True,
        num_history_runs=5,
        enable_agentic_memory=True,
        enable_session_summaries=True,
        markdown=True,
        use_json_mode=True,
    )

    print("\n===== Multi-Agent Recursive Knowledge (Agno + Gemini) =====")
    print("Type a topic or question (e.g., 'I was reading about Artificial Neural Networks').")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_in = input("You: ").strip()
            if user_in.lower() in {"exit", "quit"}:
                break

            kb = run_pipeline(user_in)
            print("\n--- KnowledgeBundle ---")
            pprint(kb.model_dump(), expand_all=True)
            

            if kb.suggested_subtopics:
                print("\nSuggested follow-ups:")
                for i, st in enumerate(kb.suggested_subtopics[:7], 1):
                    print(f"  {i}. {st}")

            print("\n(You can ask, e.g., 'What about CNNs?' to go deeper.)\n")
        except KeyboardInterrupt:
            break
    print("\nGoodbye!")