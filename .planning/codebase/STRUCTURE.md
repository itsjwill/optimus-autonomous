# Codebase Structure

**Analysis Date:** 2026-01-16

## Directory Layout

```
optimus-autonomous/
├── optimus.py                  # CLI entry point (MAIN)
├── banner.py                   # ASCII art and styling
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
│
├── optimus/                    # Main package (28 Python files)
│   ├── __init__.py             # Package init, version
│   ├── constants.py            # Constants and defaults
│   │
│   ├── core/                   # Orchestration layer
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Main Orchestrator (BRAIN)
│   │   ├── config.py           # Configuration classes
│   │   └── router.py           # Model routing
│   │
│   ├── agents/                 # Agent implementations
│   │   ├── __init__.py
│   │   ├── base.py             # BaseAgent, LLMAgent
│   │   ├── team.py             # Team, TeamFactory
│   │   ├── code_team.py        # CodeTeam
│   │   ├── web_team.py         # WebTeam
│   │   └── strategy_team.py    # StrategyTeam
│   │
│   ├── memory/                 # Persistence layer
│   │   ├── __init__.py
│   │   ├── manager.py          # MemoryManager
│   │   ├── brain_db.py         # BrainDB (SQLite)
│   │   └── knowledge_graph.py  # KnowledgeGraph
│   │
│   ├── security/               # Safety layer
│   │   ├── __init__.py
│   │   ├── guardrails.py       # GuardrailsManager
│   │   └── sandbox.py          # SandboxManager
│   │
│   ├── tools/                  # Tool integrations
│   │   ├── __init__.py
│   │   ├── registry.py         # ToolRegistry
│   │   ├── mcp_client.py       # MCPClient
│   │   ├── browser.py          # Browser tools
│   │   ├── file_tools.py       # File tools
│   │   └── web_tools.py        # Web tools
│   │
│   └── observability/          # Monitoring layer
│       ├── __init__.py
│       ├── observer.py         # Observer
│       └── metrics.py          # Metrics
│
├── .planning/                  # GSD planning files
│   └── codebase/               # Codebase documentation
│
└── venv/                       # Python virtual environment
```

## Directory Purposes

**optimus/**
- Purpose: Main application package
- Contains: All core Python modules (28 files)
- Key files: `__init__.py` (version), `constants.py` (defaults)
- Subdirectories: core, agents, memory, security, tools, observability

**optimus/core/**
- Purpose: Central orchestration and configuration
- Contains: Orchestrator, Config, Router classes
- Key files: `orchestrator.py` (main brain), `config.py` (settings)
- Subdirectories: None

**optimus/agents/**
- Purpose: Agent implementations and team coordination
- Contains: Base classes, team logic, specialized teams
- Key files: `base.py` (LLMAgent), `team.py` (Team coordination)
- Subdirectories: None

**optimus/memory/**
- Purpose: Persistent storage and context management
- Contains: Memory manager, SQLite backend, knowledge graph
- Key files: `brain_db.py` (BrainDB), `manager.py` (unified interface)
- Subdirectories: None

**optimus/security/**
- Purpose: Input/output validation and code sandboxing
- Contains: Guardrails manager, sandbox manager
- Key files: `guardrails.py` (validation), `sandbox.py` (E2B)
- Subdirectories: None

**optimus/tools/**
- Purpose: Tool registry and external integrations
- Contains: Registry, MCP client, specific tool modules
- Key files: `registry.py` (central registry), `mcp_client.py` (MCP)
- Subdirectories: None

**optimus/observability/**
- Purpose: Event tracking and metrics collection
- Contains: Observer, metrics collector
- Key files: `observer.py` (event tracking), `metrics.py` (stats)
- Subdirectories: None

## Key File Locations

**Entry Points:**
- `optimus.py` - CLI entry point, main commands
- `optimus/core/orchestrator.py` → `Orchestrator.run()` - Loop runner
- `optimus/core/orchestrator.py` → `Orchestrator.execute_task()` - Task execution

**Configuration:**
- `optimus/core/config.py` - OptimusConfig, TeamConfig, AgentConfig
- `optimus/constants.py` - DEFAULT_MODEL, COST_RATES, VERSION
- `.env` - Environment variables (gitignored)
- `optimus.yaml` - Project config (generated on init)

**Core Logic:**
- `optimus/core/orchestrator.py` - Main orchestration (Task, Iteration, Orchestrator)
- `optimus/agents/base.py` - BaseAgent, LLMAgent, AgentResponse
- `optimus/agents/team.py` - Team, TeamFactory
- `optimus/memory/brain_db.py` - BrainDB, MemoryEntry

**Testing:**
- No `tests/` directory exists currently
- pytest configured in requirements.txt

**Documentation:**
- `README.md` - User-facing documentation
- `.planning/` - GSD planning files

## Naming Conventions

**Files:**
- `snake_case.py` for all modules
- Examples: `brain_db.py`, `web_tools.py`, `mcp_client.py`
- `__init__.py` for package directories

**Directories:**
- `snake_case` for all directories
- Singular for focused domains: `memory`, `security`
- Plural for collections: `agents`, `tools`

**Special Patterns:**
- `_team.py` suffix for team implementations
- `_tools.py` suffix for tool modules
- No `test_` prefix files found (tests not implemented)

## Where to Add New Code

**New Agent Team:**
- Implementation: `optimus/agents/{team_name}_team.py`
- Register: Add to `TeamFactory` in `optimus/agents/team.py`
- Tests: `tests/unit/test_{team_name}_team.py` (when implemented)

**New Tool:**
- Implementation: `optimus/tools/{tool_name}.py`
- Register: Add to `ToolRegistry` in `optimus/tools/registry.py`
- Tests: `tests/unit/test_{tool_name}.py` (when implemented)

**New Memory Backend:**
- Implementation: `optimus/memory/{backend_name}.py`
- Interface: Follow `MemoryManager` patterns in `optimus/memory/manager.py`
- Tests: `tests/unit/test_{backend_name}.py` (when implemented)

**New Security Feature:**
- Implementation: Extend `optimus/security/guardrails.py`
- Or: New file `optimus/security/{feature_name}.py`
- Tests: `tests/unit/test_{feature_name}.py` (when implemented)

**Utilities:**
- Shared helpers: Create `optimus/utils/` directory
- Constants: Add to `optimus/constants.py`

## Special Directories

**optimus/**
- Purpose: Main application package
- Source: Core codebase
- Committed: Yes

**venv/**
- Purpose: Python virtual environment
- Source: Created by `python -m venv venv`
- Committed: No (gitignored)

**.planning/**
- Purpose: GSD planning and codebase documentation
- Source: Generated by GSD commands
- Committed: Yes

**Data files (generated at runtime):**
- `brain.db` - SQLite database (project directory)
- `optimus_events.jsonl` - Event log (project directory)
- `optimus.yaml` - Project config (project directory)

---

*Structure analysis: 2026-01-16*
*Update when directory structure changes*
