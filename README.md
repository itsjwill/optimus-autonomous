# Optimus Autonomous

```
╔═══════════════════════════════════════════════════════════╗
║  ██████╗ ██████╗ ████████╗██╗███╗   ███╗██╗   ██╗███████╗ ║
║ ██╔═══██╗██╔══██╗╚══██╔══╝██║████╗ ████║██║   ██║██╔════╝ ║
║ ██║   ██║██████╔╝   ██║   ██║██╔████╔██║██║   ██║███████╗ ║
║ ██║   ██║██╔═══╝    ██║   ██║██║╚██╔╝██║██║   ██║╚════██║ ║
║ ╚██████╔╝██║        ██║   ██║██║ ╚═╝ ██║╚██████╔╝███████║ ║
║  ╚═════╝ ╚═╝        ╚═╝   ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝ ║
║                    A U T O N O M O U S                    ║
║                                                           ║
║                       by itsJWill                         ║
╚═══════════════════════════════════════════════════════════╝
```

> **"The best self-governing intelligence."**

---

## What is Optimus Autonomous?

Optimus Autonomous is a multi-agent AI operating system — a unified framework that combines powerful autonomous agent technologies into one self-learning, self-optimizing intelligence mesh.

**One brain. Many agents. Infinite potential.**

---

## Current Implementation

### Core Features (v0.1.0)

| Component | Status | Description |
|-----------|--------|-------------|
| **Multi-Agent Orchestration** | ✅ Implemented | Async task execution with sequential, parallel, and hierarchical modes |
| **Agent Teams** | ✅ Implemented | Specialized Code, Web, and Strategy teams with role-based collaboration |
| **Memory Layer** | ✅ Implemented | SQLite brain.db for persistent memory + optional Mem0 integration |
| **Security Guardrails** | ✅ Implemented | Input/output validation, prompt injection detection, dangerous pattern blocking |
| **Code Sandbox** | ✅ Implemented | E2B integration for safe code execution (with local fallback) |
| **Observability** | ✅ Implemented | AgentOps integration for cost tracking and session monitoring |
| **CLI Interface** | ✅ Implemented | Full CLI with init, run, deploy, status, and interactive modes |

### Architecture

```
optimus/
├── core/               # Orchestration engine
│   ├── config.py       # Configuration management
│   └── orchestrator.py # Task execution and agent coordination
├── agents/             # Agent teams
│   ├── base.py         # BaseAgent and LLMAgent classes
│   ├── team.py         # Team coordination (sequential/parallel/hierarchical)
│   ├── code_team.py    # Software development team
│   ├── web_team.py     # Web research team
│   └── strategy_team.py # Strategic planning team
├── memory/             # Persistence layer
│   ├── brain_db.py     # SQLite storage for memories, patterns, decisions
│   └── manager.py      # Unified memory interface (Mem0 optional)
├── security/           # Safety and guardrails
│   ├── guardrails.py   # Input/output validation (19 injection patterns)
│   └── sandbox.py      # E2B sandboxed code execution
├── observability/      # Monitoring
│   ├── observer.py     # Event tracking, session management
│   └── metrics.py      # Performance metrics collection
└── tools/              # Tool integrations (extensible)
```

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/itsjwill/optimus-autonomous.git
cd optimus-autonomous

# Install dependencies
pip install -r requirements.txt

# Show the banner
python optimus.py banner

# Initialize a project
python optimus.py init my-project
cd my-project

# Add your API keys
cp .env.example .env
# Edit .env with ANTHROPIC_API_KEY or OPENAI_API_KEY

# Check system status
python ../optimus.py status

# Run a task with the code team
python ../optimus.py run --task "Build a REST API endpoint" --team code

# Run in interactive mode
python ../optimus.py interactive
```

---

## Agent Teams

### Code Team (Sequential)
- **Architect** — Designs clean, scalable solutions
- **Developer** — Implements high-quality, tested code
- **Reviewer** — Ensures quality and catches bugs

```python
from optimus.agents import CodeTeam

team = CodeTeam()
result = await team.implement_feature(
    "Add user authentication with JWT tokens",
    requirements=["secure", "stateless", "refresh tokens"]
)
```

### Web Team (Parallel)
- **Researcher** — Finds and extracts relevant information
- **Analyzer** — Synthesizes findings into insights

```python
from optimus.agents import WebTeam

team = WebTeam()
result = await team.research(
    "AI agent frameworks comparison 2024",
    sources=["github", "papers", "blogs"]
)
```

### Strategy Team (Hierarchical)
- **Strategist** — Develops winning strategies (manager)
- **Analyst** — Analyzes data and markets
- **Risk Manager** — Assesses risks and mitigations

```python
from optimus.agents import StrategyTeam

team = StrategyTeam()
result = await team.develop_strategy(
    "Enter the European market",
    constraints=["limited budget", "6-month timeline"]
)
```

---

## Memory System

Optimus remembers everything across sessions:

```python
from optimus.memory import BrainDB

brain = BrainDB("brain.db")
await brain.initialize()

# Store memories
await brain.store_memory("pattern", "Users prefer dark mode", {"source": "analytics"})

# Search memories
results = await brain.search_memories("pattern", "user preferences")

# Store learned patterns
await brain.store_pattern("optimization", "Cache API responses for 5 minutes")
```

---

## Security

### Input Validation
- 19 prompt injection detection patterns
- 8 sensitive data (PII) detection patterns
- 4 harmful content filters
- Rate limiting and anomaly detection

### Code Sandboxing
- E2B cloud sandboxing (125ms boot)
- Local fallback with dangerous pattern blocking
- File system and network isolation

```python
from optimus.security import SandboxManager

sandbox = SandboxManager(config)
result = await sandbox.execute(
    code="print('Hello, World!')",
    language="python",
    timeout_ms=5000
)
```

---

## Configuration

### Environment Variables

```bash
# Required: At least one LLM API key
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional: E2B for sandboxed execution
E2B_API_KEY=...

# Optional: AgentOps for monitoring
AGENTOPS_API_KEY=...
```

### Project Config (optimus.yaml)

```yaml
project_name: my-project
default_model: claude-3-5-sonnet-20241022

memory_enabled: true
memory_backend: sqlite  # sqlite or mem0

guardrails_enabled: true
sandbox_enabled: false  # Enable if E2B API key is set

max_iterations: 100
learning_enabled: true
verbose: true
```

---

## Roadmap

### Completed (v0.1.0)
- [x] Core orchestration layer
- [x] Agent teams (Code, Web, Strategy)
- [x] Memory layer (SQLite + Mem0)
- [x] Security guardrails
- [x] E2B sandbox integration
- [x] AgentOps observability
- [x] CLI interface

### Coming Soon
- [ ] MCP tool server integration
- [ ] Knowledge graphs (Graphiti)
- [ ] Web automation (Agent-Browser, Stagehand)
- [ ] Model routing optimization
- [ ] Production hardening

---

## Inspired By

Optimus Autonomous draws inspiration from these excellent projects:

| Project | Inspiration |
|---------|-------------|
| [MEGAMIND](https://github.com/itsjwill/megamind) | Autonomous project execution with fresh context |
| [CrewAI](https://github.com/crewAIInc/crewAI) | Role-based agent collaboration |
| [LangGraph](https://github.com/langchain-ai/langgraph) | Cyclical workflows with state management |
| [Mem0](https://github.com/mem0ai/mem0) | Persistent cross-session memory |
| [E2B](https://github.com/e2b-dev/E2B) | Fast, secure code sandboxing |
| [AgentOps](https://github.com/AgentOps-AI/agentops) | Agent monitoring and cost tracking |
| [LLM Guard](https://github.com/protectai/llm-guard) | Prompt injection protection |

---

## Author

**itsJWill**, known as **BillyCoder** — Builder. Shipper. Relentless optimizer.

Creator of [MEGAMIND](https://github.com/itsjwill/megamind) for autonomous project execution. Architect of trading bots that compound profits 24/7 without human intervention. Builder of AI-powered business automation that turns workflows into self-improving machines.

*"Deploy once. Improve forever."*

---

## License

MIT License — Use it, fork it, make it yours.

---

<p align="center">
  <b>Optimus Autonomous</b><br>
  <i>The best self-governing intelligence.</i><br>
  <code>by itsJWill</code>
</p>
