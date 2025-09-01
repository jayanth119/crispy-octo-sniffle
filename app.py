from __future__ import annotations
import os
import sys
import json
import time
from datetime import datetime
from typing import Any

import streamlit as st
import speech_recognition as sr

# Adjust path so the project's modules (Schemas, agents, models) can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Import the multi-agent pipeline components ---
from agno.agent import Agent, RunResponse
from agno.team import Team
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.memory.v2.memory import Memory
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

# ------------------------ Memory setup ------------------------
memory_db = SqliteMemoryDb(table_name="memory", db_file="multi_agent_memory.db")
memory = Memory(db=memory_db)

# ------------------------ Pipeline function ------------------------
def run_pipeline(user_text: str, show_steps: bool = False) -> KnowledgeBundle:
    """Run the multi-agent pipeline and return a KnowledgeBundle."""
    # 1) Extract topic
    topic_res: RunResponse = topic_agent.run(user_text)
    te_content = topic_res.content
    topic_struct = te_content if isinstance(te_content, TopicExtraction) else TopicExtraction(**te_content)
    topic = topic_struct.topic

    def safe_run(agent: Agent, prompt: str, model_class: Any):
        res = agent.run(prompt)
        content = res.content

        if show_steps:
            with st.expander(f"{agent.name} — Prompt & Raw Output"):
                st.markdown(f"**Prompt**: {prompt}")
                st.write("**Raw Output:**")
                st.write(content)

        if isinstance(content, model_class):
            return content

        try:
            if isinstance(content, dict):
                normalized = {
                    k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                    for k, v in content.items()
                }
                return model_class(**normalized)

            if isinstance(content, str):
                try:
                    parsed = json.loads(content)
                    normalized = {
                        k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
                        for k, v in parsed.items()
                    }
                    return model_class(**normalized)
                except json.JSONDecodeError:
                    first_field = list(model_class.model_fields.keys())[0]
                    return model_class(**{first_field: content})

            return model_class(**{})
        except Exception as e:
            print(f"⚠️ Parsing failed for {agent.name}: {e}")
            fallback_data = {f: "N/A" for f in model_class.model_fields.keys()}
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

    try:
        memory.add(
            {
                "key": f"knowledge::{topic}",
                "value": kb.model_dump(),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "source": "multi-agent-streamlit-app",
                    "user_query": user_text,
                },
            }
        )
    except Exception as e:
        print(f"⚠️ Failed to save KnowledgeBundle: {e}")

    return kb

# ------------------------ Streamlit UI ------------------------

st.set_page_config(page_title=" Multi-Agent Knowledge Explorer", layout="wide")

# Simple modern CSS
st.markdown(
    """
    <style>
    .stApp {background: linear-gradient(180deg,#0f172a 0%, #0b1220 100%); color: #e6eef8}
    .card {background: rgba(255,255,255,0.03); padding:16px; border-radius:12px; box-shadow: 0 6px 18px rgba(2,6,23,0.6);}
    .muted {color: #9fb0d6}
    .huge {font-size:28px; font-weight:700}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<div class='huge'>Scorify — Multi-Agent Knowledge Explorer</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Speak, type, explore — get theory, code, examples and use-cases generated by your agent team.</div>", unsafe_allow_html=True)
with col2:
    pass 
    # if st.b
    # utton("About"):
    #     st.info("Built for your multi-agent Scorify pipeline. Click topic cards to expand and view details.")

st.write("---")

# ------------------------ Input area ------------------------

if "user_text" not in st.session_state:
    st.session_state.user_text = ""

st.subheader("Input")
cols = st.columns([3, 2])
with cols[0]:
    st.session_state.user_text = st.text_input("Type your topic or question", value=st.session_state.user_text, key="user_text_input")

with cols[1]:
    st.write("Or record voice:")
    if st.button("🎤 Click to record (microphone)"):
        st.info("Recording from microphone... please speak clearly for ~8 seconds.")
        r = sr.Recognizer()
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source, timeout=8, phrase_time_limit=8)
            transcript = r.recognize_google(audio)
            st.success("Transcription complete")

            # ✅ Store transcript into text input
            st.session_state.user_text = transcript
            st.rerun()

        except Exception as e:
            st.error(f"Microphone recording failed: {e}")


# ------------------------ Controls ------------------------
st.write("---")
controls_col1, controls_col2, controls_col3 = st.columns([1, 1, 2])
with controls_col1:
    run_btn = st.button("Run Pipeline", key="run")
with controls_col2:
    show_raw = st.checkbox("Show raw KnowledgeBundle", value=False)
with controls_col3:
    show_steps = st.checkbox("Show each agent's prompt & raw output", value=True)

# ------------------------ Output area ------------------------
if run_btn and (st.session_state.user_text and st.session_state.user_text.strip()):
    query = st.session_state.user_text.strip()
    st.session_state.last_query = query

    status = st.empty()
    status.info("Running agents...")

    start = time.time()
    try:
        kb = run_pipeline(query, show_steps=show_steps)
        elapsed = time.time() - start
        status.success(f"Done — {elapsed:.1f}s")

        left, right = st.columns([2, 1])

        with left:
            st.markdown(f"### Topic: **{kb.topic}**")

            with st.expander("Theory (expand)", expanded=True):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"**Overview**\n\n{kb.theory.overview}")
                if hasattr(kb.theory, 'key_concepts') and kb.theory.key_concepts:
                    st.markdown("**Key Concepts**")
                    for kc in kb.theory.key_concepts:
                        st.write(f"• {kc}")
                if hasattr(kb.theory, 'mechanism') and kb.theory.mechanism:
                    st.markdown("**Mechanism**")
                    st.write(kb.theory.mechanism)
                if hasattr(kb.theory, 'cautions') and kb.theory.cautions:
                    st.markdown("**Cautions**")
                    for c in kb.theory.cautions:
                        st.write(f"- {c}")
                st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("Code (expand)"):
                if kb.code.supported:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    primary = kb.code.primary
                    st.markdown(f"**{primary.title}** — *{primary.language}*")
                    st.code(primary.code, language=primary.language)

                    if hasattr(kb.code, 'alternates') and kb.code.alternates:
                        st.markdown("**Alternates**")
                        for a in kb.code.alternates:
                            st.markdown(f"*{a.get('title','Alternate')}* — {a.get('language','')}")
                            st.code(a.get('code',''))
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.info("The agent indicated no code is applicable for this topic.")

            with st.expander("Examples & IO (expand)"):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if getattr(kb.examples, 'simple_analogy', None):
                    st.markdown("**Analogy**")
                    st.write(kb.examples.simple_analogy)
                if getattr(kb.examples, 'io_example', None):
                    st.markdown("**I/O Example**")
                    st.json(kb.examples.io_example)
                if getattr(kb.examples, 'explanation', None):
                    st.markdown("**Explanation**")
                    st.write(kb.examples.explanation)
                st.markdown("</div>", unsafe_allow_html=True)

            with st.expander("Use Cases & Applications (expand)"):
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if getattr(kb.use_cases, 'applications', None):
                    st.markdown("**Applications**")
                    for a in kb.use_cases.applications:
                        st.write(f"- {a}")
                if getattr(kb.use_cases, 'industries', None):
                    st.markdown("**Industries**")
                    st.write(', '.join(kb.use_cases.industries))
                if getattr(kb.use_cases, 'maturity_notes', None):
                    st.markdown("**Maturity Notes**")
                    st.write(kb.use_cases.maturity_notes)
                st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown("### Quick Controls & Suggestions")
            size = st.slider("Theory text size", min_value=12, max_value=28, value=16)
            st.markdown(f"<style>.theory-size{{font-size:{size}px}}</style>", unsafe_allow_html=True)

            if getattr(kb, 'suggested_subtopics', None):
                st.markdown("**Suggested subtopics**")
                for stopic in kb.suggested_subtopics[:8]:
                    if st.button(f"Dive: {stopic}"):
                        st.session_state.user_text = stopic
                        st.experimental_rerun()

            st.write("---")
            st.markdown("**Saved to local memory DB**")
            st.write(f"Key: knowledge::{kb.topic}")

        if show_raw:
            st.write("---")
            st.markdown("### Raw KnowledgeBundle (debug)")
            st.json(kb.model_dump())

        st.balloons()

    except Exception as e:
        status.error(f"Pipeline failed: {e}")

elif 'last_query' in st.session_state:
    st.info(f"Last query: {st.session_state.last_query}")
else:
    st.info("Type a topic or record your voice, then click 'Run Pipeline'.")
