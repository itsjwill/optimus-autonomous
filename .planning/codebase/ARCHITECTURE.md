# Architecture

**Analysis Date:** 2026-01-16

## Pattern Overview

**Overall:** Multi-Agent Orchestration System with Layered Architecture

**Key Characteristics:**
- Multi-agent system with specialized teams (Code, Web, Strategy)
- Async-first design built on Python asyncio
- Pluggable components (memory, security, observability)
- Tool-based extensibility via central registry and MCP protocol
- Clear separation of concerns across 6 layers

## Layers

**Entry/CLI Layer:**
- Purpose: Command-line interface and user interaction
- Contains: CLI commands, interactive REPL, banner display
- Location: `optimus.py`, `banner.py`
- Depends on: Core layer
- Used by: End users via terminal

**Orchestration Layer:**
- Purpose: Central brain managing tasks, teams, and system coordination
- Contains: Task queue, execution lifecycle, memory init, security application
- Location: `optimus/core/orchestrator.py`, `optimus/core/config.py`, `optimus/core/router.py`
- Depends on: All other layers
- Used by: CLI layer

**Agent Layer:**
- Purpose: Task execution via LLM-powered agents
- Contains: BaseAgent, LLMAgent, Team coordination, specialized teams
- Location: `optimus/agents/base.py`, `optimus/agents/team.py`, `optimus/agents/code_team.py`, `optimus/agents/web_team.py`, `optimus/agents/strategy_team.py`
- Depends on: Tools, Memory, Security layers
- Used by: Orchestration layer

**Memory Layer:**
- Purpose: Persistence, pattern learning, context retrieval
- Contains: MemoryManager, BrainDB (SQLite), KnowledgeGraph
- Location: `optimus/memory/manager.py`, `optimus/memory/brain_db.py`, `optimus/memory/knowledge_graph.py`
- Depends on: SQLite, optional Mem0/ChromaDB
- Used by: Agent layer, Orchestration layer

**Security Layer:**
- Purpose: Input/output validation and sandboxed code execution
- Contains: GuardrailsManager, SandboxManager
- Location: `optimus/security/guardrails.py`, `optimus/security/sandbox.py`
- Depends on: Optional LLM Guard, E2B
- Used by: Orchestration layer

**Tools Layer:**
- Purpose: Capability registry and external tool integration
- Contains: ToolRegistry, MCP client, file/web/browser tools
- Location: `optimus/tools/registry.py`, `optimus/tools/mcp_client.py`, `optimus/tools/file_tools.py`, `optimus/tools/web_tools.py`, `optimus/tools/browser.py`
- Depends on: External MCP servers, httpx, Playwright
- Used by: Agent layer

**Observability Layer:**
- Purpose: Event tracking, cost monitoring, performance metrics
- Contains: Observer, Metrics collector
- Location: `optimus/observability/observer.py`, `optimus/observability/metrics.py`
- Depends on: Optional AgentOps
- Used by: Orchestration layer

## Data Flow

**Task Execution Flow:**

1. User runs CLI command (`optimus.py` → `main()`)
2. Orchestrator initializes memory, security, sandbox, observer
3. Task created and added to queue (`Orchestrator.add_task()`)
4. GuardrailsManager validates input for injection/harmful content
5. Team executes task (sequential/parallel/hierarchical)
   - Agent retrieves context from MemoryManager
   - Agent builds system/user prompts
   - LLM API call (Anthropic or OpenAI)
   - Observer tracks tokens, cost, duration
6. GuardrailsManager validates output for sensitive data
7. Result stored in MemoryManager/BrainDB
8. Task status updated, callbacks triggered
9. Optional: Pattern extraction and learning

**State Management:**
- File-based: BrainDB (SQLite) for persistent state
- In-memory: Task queue, execution logs, session data
- Event log: JSONL file for audit trail

## Key Abstractions

**Agent:**
- Purpose: LLM-powered task executor
- Examples: `LLMAgent`, code team agents, web team agents
- Pattern: Abstract base class with concrete implementations
- Location: `optimus/agents/base.py`

**Team:**
- Purpose: Coordinate multiple agents with execution strategy
- Examples: CodeTeam (Architect→Developer→Reviewer), WebTeam, StrategyTeam
- Pattern: Composition over inheritance
- Location: `optimus/agents/team.py`

**Tool:**
- Purpose: Capability that agents can invoke
- Examples: file operations, web requests, browser automation
- Pattern: Registry pattern with JSON schema generation
- Location: `optimus/tools/registry.py`

**Task:**
- Purpose: Unit of work to be executed
- Examples: Code generation, research, analysis
- Pattern: Dataclass with status tracking
- Location: `optimus/core/orchestrator.py`

**Memory:**
- Purpose: Persistent storage and context retrieval
- Examples: BrainDB, Mem0, ChromaDB
- Pattern: Strategy pattern with pluggable backends
- Location: `optimus/memory/manager.py`

## Entry Points

**CLI Entry:**
- Location: `optimus.py` → `main()`
- Triggers: User runs `python optimus.py <command>`
- Commands: init, deploy, run, status, interactive

**Task Execution:**
- Location: `optimus/core/orchestrator.py` → `Orchestrator.execute_task()`
- Triggers: Task dequeued from task queue
- Responsibilities: Validate, execute with team, store result

**Loop Runner:**
- Location: `optimus/core/orchestrator.py` → `Orchestrator.run()`
- Triggers: `optimus run --iterations N`
- Responsibilities: Execute tasks iteratively with learning

**Interactive Mode:**
- Location: `optimus.py` → `interactive_mode()`
- Triggers: `optimus interactive` or `optimus i`
- Responsibilities: REPL for direct agent interaction

## Error Handling

**Strategy:** Try-except at boundaries, custom result objects for propagation

**Patterns:**
- Tasks catch exceptions and store in `task.result`
- Tools return `ToolResult` with success flag and error message
- Guardrails return `GuardrailResult` with pass/fail and details
- Orchestrator logs errors via Observer

## Cross-Cutting Concerns

**Logging:**
- Rich console output for user feedback
- JSONL event log for audit (`optimus_events.jsonl`)
- Optional AgentOps for detailed monitoring

**Validation:**
- Guardrails for input/output security
- Pydantic for configuration validation
- Type hints throughout codebase

**Configuration:**
- Environment variables (highest priority)
- YAML config file (`optimus.yaml`)
- Dataclass defaults (lowest priority)

**Cost Tracking:**
- Token counting per LLM call
- Cost calculation based on model pricing
- Session-level aggregation

---

*Architecture analysis: 2026-01-16*
*Update when major patterns change*
