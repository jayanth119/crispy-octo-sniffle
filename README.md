# 🧠 LLM Multi-Agent System

This project is an **LLM-powered multi-agent framework** built with modular schemas and intelligent agents for generating, analyzing, and managing structured knowledge, code, and use cases.

---

## 📁 Project Structure

```
.
├── Schemas/
│   ├── codeSchema.py
│   ├── knowledgeSchema.py
│   ├── theorySchema.py
│   ├── topicSchema.py
│   ├── exampleSchema.py
│   └── useCaseSchema.py
│
├── agents/
│   ├── codeAgent.py
│   ├── knowledgeAgent.py
│   ├── theoryAgent.py
│   ├── topicAgent.py
│   ├── exampleAgent.py
│   └── usecaseAgent.py
│
└── models/
```

Each **Schema** defines the structured input/output format for a specific task type, while each **Agent** uses that schema to interact with an LLM to perform specialized operations.

---

## 🧩 System Architecture

```mermaid
graph TD
    A[User Input] --> B[Router / Main Controller]
    B --> C[Schema Layer]
    C -->|Defines structure| D[Agent Layer]
    D -->|Calls| E[LLM Engine]
    E --> F[Response Formatter]
    F --> G[Output Generation]
```

---

## 🤖 Agent Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant M as Main Controller
    participant A as Agent (e.g., CodeAgent)
    participant L as LLM
    U->>M: Sends query
    M->>A: Delegates task
    A->>L: Sends structured prompt (via schema)
    L-->>A: Returns response
    A-->>M: Processes and validates response
    M-->>U: Sends final output
```

---

## 🧱 Schema Design

```mermaid
classDiagram
    class BaseSchema {
        +id: str
        +prompt_template: str
        +validate_input()
        +parse_output()
    }

    class CodeSchema {
        +language: str
        +problem_statement: str
        +solution: str
    }

    class TheorySchema {
        +topic: str
        +definition: str
        +examples: list
    }

    BaseSchema <|-- CodeSchema
    BaseSchema <|-- TheorySchema
```

---

## ⚙️ Tech Stack

* **Python 3.10+**
* **LangChain / CrewAI**
* **OpenAI / Gemini API**
* **Pydantic** for schema validation
* **Mermaid.js** for diagrams

---

## 🚀 Setup

```bash
git clone https://github.com/jayanth119/crispy-octo-sniffle.git
cd crispy-octo-sniffle 
pip install -r requirements.txt
```

Run agents:

```bash
python agents/codeAgent.py
```

---

## 🧠 Prompt Engineering Highlights

* Modular prompts for each domain
* Context chaining between agents
* Role-based structured output
* Auto schema validation

---

## ⚠️ Challenges

* Maintaining consistent context across agents
* Balancing creativity vs factual accuracy
* Managing token limits and response length

---

## 📊 Future Work

* Implement feedback-based reinforcement
* Add memory store for long-term context
* Integrate dashboard for agent monitoring

---

**Author:** [Jayanth chukka]
**Project:** `crispy-octo-sniffle`
**License:** MIT
