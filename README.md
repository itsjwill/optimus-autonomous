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

Optimus Autonomous is a multi-agent AI operating system — a unified framework that combines **30+ open-source technologies** into one self-learning, self-optimizing intelligence mesh.

**One brain. Many agents. Infinite potential.**

---

## The Stack

Optimus synthesizes these technologies into a cohesive system:

### Core Orchestration
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **CrewAI** | ✅ Built-in | Role-based agent collaboration |
| **LangGraph** | ✅ Built-in | Cyclical workflows with state management |
| **Custom Orchestrator** | ✅ Built-in | Async task execution, parallel/sequential/hierarchical |

### Agent Teams
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **Code Team** | ✅ Implemented | Architect + Developer + Reviewer (sequential) |
| **Web Team** | ✅ Implemented | Researcher + Analyzer (parallel) |
| **Strategy Team** | ✅ Implemented | Strategist + Analyst + Risk Manager (hierarchical) |
| **Trading Team** | ✅ **NEW** | 5 AI agents for autonomous trading intelligence |

### Memory & Knowledge
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **BrainDB** | ✅ Implemented | SQLite storage for memories, patterns, decisions |
| **Mem0** | ✅ Optional | Universal cross-session memory |
| **Knowledge Graph** | ✅ Implemented | Entity-relationship storage with graph traversal |
| **ChromaDB** | ✅ Optional | Vector embeddings for semantic search |

### Tools & Automation
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **MCP Client** | ✅ Implemented | Model Context Protocol for 200+ tools |
| **Browser Tool** | ✅ Implemented | Playwright-based web automation |
| **File Tools** | ✅ Implemented | Safe file operations with sandbox |
| **Web Tools** | ✅ Implemented | HTTP requests, scraping, API calls |
| **Tool Registry** | ✅ Implemented | Centralized tool management and execution |

### Model Routing
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **Smart Router** | ✅ Implemented | Auto-selects optimal model per task |
| **Cost Optimization** | ✅ Implemented | Routes to cheaper models when appropriate |
| **Multi-Provider** | ✅ Implemented | Anthropic + OpenAI + OpenRouter support |
| **Multi-Model Agents** | ✅ **NEW** | Different agents use different models |

### Execution & Sandboxing
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **E2B** | ✅ Implemented | Cloud sandboxing (125ms boot) |
| **Local Fallback** | ✅ Implemented | Safe local execution with validation |
| **Code Validation** | ✅ Implemented | Dangerous pattern blocking |

### Security & Guardrails
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **Input Guardrails** | ✅ Implemented | 19 prompt injection patterns |
| **Output Validation** | ✅ Implemented | Content filtering, PII detection |
| **LLM Guard** | ✅ Optional | Advanced prompt injection protection |

### Observability
| Component | Integration | Purpose |
|-----------|-------------|---------|
| **AgentOps** | ✅ Optional | Cost tracking, session monitoring |
| **Metrics Collector** | ✅ Implemented | Token usage, duration, success rates |
| **Event Observer** | ✅ Implemented | Full audit trail with timestamps |

---

## Architecture

```
run_trading_brain.py        # Autonomous trading daemon (runs hourly)
deploy_to_droplet.sh        # One-command deployment to DigitalOcean
optimus/
├── core/                   # Orchestration engine
│   ├── config.py           # Configuration management
│   ├── orchestrator.py     # Task execution and agent coordination
│   └── router.py           # Smart model selection
├── agents/                 # Agent teams
│   ├── base.py             # BaseAgent and LLMAgent classes
│   ├── team.py             # Team coordination
│   ├── code_team.py        # Software development team
│   ├── web_team.py         # Web research team
│   ├── strategy_team.py    # Strategic planning team
│   └── trading_team.py     # 5-agent autonomous trading intelligence
├── memory/                 # Persistence layer
│   ├── brain_db.py         # SQLite storage
│   ├── manager.py          # Unified memory interface
│   └── knowledge_graph.py  # Entity-relationship graph
├── security/               # Safety and guardrails
│   ├── guardrails.py       # Input/output validation
│   └── sandbox.py          # Code execution sandbox
├── tools/                  # Tool integrations
│   ├── registry.py         # Central tool registry
│   ├── mcp_client.py       # MCP server connections
│   ├── browser.py          # Playwright automation
│   ├── file_tools.py       # File operations
│   └── web_tools.py        # HTTP and scraping
├── observability/          # Monitoring
│   ├── observer.py         # Event tracking
│   └── metrics.py          # Performance metrics
└── constants.py            # Centralized defaults
```

---

## Quick Start

```bash
# Clone the repo
git clone https://github.com/itsjwill/optimus-autonomous.git
cd optimus-autonomous

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for web automation)
playwright install chromium

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

## Features

### Smart Model Routing

Automatically selects the optimal model based on task complexity:

```python
from optimus.core import ModelRouter

router = ModelRouter(prefer_speed=False)
decision = router.route("Analyze this complex algorithm and suggest optimizations")

print(decision.model)      # claude-3-5-sonnet-20241022
print(decision.reason)     # Selected for expert-level analysis task
print(decision.confidence) # 0.92
```

### MCP Tool Integration

Connect to Model Context Protocol servers for 200+ tools:

```python
from optimus.tools import MCPClient, get_registry

client = MCPClient(registry=get_registry())

# Connect to filesystem and fetch servers
await client.connect("filesystem", "npx", ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"])
await client.connect("fetch", "npx", ["-y", "@modelcontextprotocol/server-fetch"])

# List available tools
print(client.list_tools())

# Call a tool
result = await client.call_tool("filesystem", "read_file", {"path": "/tmp/test.txt"})
```

### Browser Automation

Full web automation with Playwright:

```python
from optimus.tools import BrowserTool

browser = BrowserTool()
await browser.initialize()

# Navigate and interact
await browser.navigate("https://example.com")
await browser.click("button.submit")
await browser.fill("input[name=email]", "test@example.com")

# Extract content
text = await browser.get_text()
links = await browser.get_links()
screenshot = await browser.screenshot(full_page=True)
```

### Knowledge Graph

Store and query entity relationships:

```python
from optimus.memory import KnowledgeGraph

graph = KnowledgeGraph("knowledge.db")
await graph.initialize()

# Add entities
await graph.add_entity("user_1", "person", "John Doe", {"role": "developer"})
await graph.add_entity("project_1", "project", "Optimus", {"status": "active"})

# Add relationships
await graph.add_relationship("user_1", "project_1", "works_on", weight=1.0)

# Query the graph
neighbors = await graph.get_neighbors("user_1", depth=2)
path = await graph.find_path("user_1", "project_1")
```

### Trading Team (Autonomous Trading Brain)

The Trading Team is a 5-agent system for autonomous trading intelligence, designed to analyze performance, optimize strategies, and make decisions without human intervention.

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ALPHA ENGINE 2.0                                          │
│                           Real-Time Market Intelligence Layer                                │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
        ┌───────────────┬───────────────┬─────┴─────┬───────────────┬───────────────┐
        ▼               ▼               ▼           ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│    Oracle    │ │    Whale     │ │    Social    │ │   Funding    │ │   Advanced   │ │     Hive     │
│   Monitor    │ │   Tracker    │ │    Alpha     │ │   Monitor    │ │    Alpha     │ │     Mind     │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ Cross-       │ │ 134K+ Whale  │ │ Sentiment    │ │ Funding Rate │ │ Options IV   │ │ Signal       │
│ Exchange     │ │ Positions    │ │ Analysis     │ │ Arbitrage    │ │ MEV/Stale    │ │ Aggregation  │
│ Prices       │ │ (Moon Dev)   │ │              │ │ Detection    │ │ Detection    │ │ & Consensus  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │                │                │
       └────────────────┴────────────────┴────────────────┴────────────────┴────────────────┘
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       brain.db                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │   trades    │ │   shadow    │ │   alpha     │ │    whale    │ │  decisions  │            │
│  │   (60+)     │ │   trades    │ │   signals   │ │   signals   │ │   (MANTIS)  │            │
│  │             │ │   (243+)    │ │   (47K+)    │ │   (134K+)   │ │             │            │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
┌─────────────────────────────────────────┐       ┌─────────────────────────────────────────┐
│            MANTIS (Rule-Based)          │       │         OPTIMUS TRADING BRAIN           │
│         Parameter Auto-Learner          │       │           (5 AI Agents)                 │
├─────────────────────────────────────────┤       ├─────────────────────────────────────────┤
│ • Analyzes shadow trades vs real        │       │ • SystemArchitect orchestrates flow     │
│ • Adjusts: direction, stops, sizing     │       │ • TradeAnalyst finds patterns           │
│ • 70% confidence threshold              │       │ • Optimizer recommends changes          │
│ • Max 3 changes/day                     │       │ • RiskGuard vetoes risky changes        │
│ • 2-hour cooldown                       │       │ • Executor makes APPLY/DEFER/REJECT     │
└─────────────────────────────────────────┘       └─────────────────────────────────────────┘
                    │                                                   │
                    └─────────────────────────┬─────────────────────────┘
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    TRADING BOTS                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │   Billy V4  │ │  Blood V5.1 │ │  Reaper V2  │ │ PHANTOM V2  │ │   Arbiter   │            │
│  │  RSI Mean   │ │ Liquidation │ │   15x Aggr  │ │  Confluence │ │  dYdX Arb   │            │
│  │  Reversion  │ │   Cascade   │ │   Signals   │ │   Signals   │ │   Spreads   │            │
│  │  LONGS ONLY │ │ Asymm Z     │ │             │ │  90.5% Win  │ │             │            │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘            │
│         │              │              │              │              │                       │
│         └──────────────┴──────────────┴──────────────┴──────────────┘                       │
│                                         │                                                   │
└─────────────────────────────────────────┼───────────────────────────────────────────────────┘
                                          ▼
                              ┌─────────────────────────┐
                              │       Hyperliquid       │
                              │    (DEX - Live Trading) │
                              │    Main: $320 | Reaper: $40
                              └─────────────────────────┘
```

### Alpha Engine 2.0 Services (12 Running)

| Service | Type | Function |
|---------|------|----------|
| **oracle-monitor** | Alpha | Cross-exchange price comparison, stale detection |
| **whale-tracker** | Alpha | 134K+ whale positions from Moon Dev API |
| **social-alpha** | Alpha | Social sentiment analysis |
| **funding-monitor** | Alpha | Funding rate arbitrage opportunities |
| **hive-mind** | Alpha | Signal aggregation & consensus generation |
| **advanced-alpha** | Alpha | Options IV, MEV protection, stale detection |
| **billy-v4** | Trading | RSI mean reversion (LONGS ONLY) |
| **blood-v5** | Trading | Liquidation cascade (Asymmetric Z) |
| **reaper** | Trading | 15x aggressive signals |
| **phantom** | Trading | Multi-signal confluence (90.5% backtest) |
| **arbiter** | Arbitrage | dYdX spread arbitrage |
| **optimus-brain** | AI | 5 LLM agents for autonomous decisions |

---

## Optimus Trading Brain (5-Agent Flow)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OPTIMUS TRADING BRAIN                                 │
│                    Autonomous Decision Flow (Hourly)                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  📊 DATA SOURCES                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  brain.db    │  │  Positions   │  │ Alpha Signals│  │ Whale Data   │    │
│  │  (trades,    │  │  (live from  │  │  (hive mind  │  │  (Moon Dev   │    │
│  │  shadow,     │  │  Hyperliquid)│  │  consensus)  │  │  134K+ pos)  │    │
│  │  decisions)  │  │              │  │              │  │              │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         └──────────────────┴─────────────────┴─────────────────┘            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏛️ SYSTEM ARCHITECT (Claude Sonnet 4)                                      │
│  ├─ Orchestrates the entire flow                                            │
│  ├─ Analyzes incoming data, determines priorities                           │
│  ├─ Frames problems for downstream agents                                   │
│  └─ Ensures no gaps in analysis                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  📈 TRADE ANALYST (Claude Sonnet 4)                                         │
│  ├─ Analyzes trade patterns (win rate, P&L, hold time)                      │
│  ├─ Identifies what's working vs what's not                                 │
│  ├─ Correlates with market regimes and time-of-day                         │
│  └─ Provides statistical significance for findings                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ OPTIMIZER (Claude Sonnet 4)                                             │
│  ├─ Translates analysis into parameter recommendations                      │
│  ├─ Understands each bot: Billy, Blood, Reaper, PHANTOM                    │
│  ├─ Proposes: RSI thresholds, Z-scores, position sizing                    │
│  └─ Assigns confidence scores and projected impact                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  🛡️ RISK GUARD (Claude 3 Haiku - Fast & Cheap)                              │
│  ├─ Evaluates each recommendation for risk                                  │
│  ├─ Checks: leverage, correlation, regime, tail risk                       │
│  ├─ Hard limits: 5x main wallet, 15x reaper wallet                         │
│  └─ Verdict: APPROVE / MODIFY / REJECT                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚡ EXECUTOR (Claude Sonnet 4)                                               │
│  ├─ Makes final decision on each recommendation                             │
│  ├─ Decisions: APPLY / DEFER / REJECT                                       │
│  ├─ Requires >70% confidence for APPLY                                      │
│  ├─ Max 3 changes per day (prevents over-optimization)                      │
│  └─ Tracks impact of previous decisions                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  📤 OUTPUT                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│  │ Apply Config │  │ Save to      │  │ Slack Alert  │                      │
│  │ Changes      │  │ brain.db     │  │ (if applied) │                      │
│  │ (if APPLY)   │  │ decisions    │  │              │                      │
│  └──────────────┘  └──────────────┘  └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Multi-Model Configuration:**

| Agent | Model | Why |
|-------|-------|-----|
| **SystemArchitect** | Claude Sonnet 4 | System-level thinking, orchestration |
| **TradeAnalyst** | Claude Sonnet 4 | Strong reasoning for data analysis |
| **Optimizer** | Claude Sonnet 4 | Creative strategy recommendations |
| **RiskGuard** | Claude 3 Haiku | Fast + cheap for quick risk checks |
| **Executor** | Claude Sonnet 4 | Critical final decisions |

**Cost Optimization:** RiskGuard uses Haiku ($0.25/M tokens) instead of Sonnet 4 ($3/M), saving 92% on risk checks while maintaining quality for critical decisions.

```python
from optimus.agents import TradingTeam

# Default: multi-model mode (optimized per agent)
team = TradingTeam(use_multi_model=True)

# Override specific agents
team = TradingTeam(
    models={"Executor": "anthropic/claude-sonnet-4.5"},  # Upgrade Executor
    use_multi_model=True
)

# Single model for all agents
team = TradingTeam(
    model="gpt-4o",
    use_multi_model=False
)

# Run autonomous cycle
result = await team.run_autonomous_cycle(
    trade_data=trade_json,
    current_params=params,
    current_positions=positions,
    market_conditions=market_json,
    previous_decisions=history
)

# Result contains:
# - analysis: Full performance breakdown
# - optimizations: Parameter recommendations
# - risk_assessment: Risk evaluation
# - decision: {success: true, decisions: [{action: "APPLY", ...}]}
```

---

### Agent Teams

Three specialized teams with different execution patterns:

```python
from optimus.agents import CodeTeam, WebTeam, StrategyTeam

# Code Team (Sequential: Architect → Developer → Reviewer)
code = CodeTeam()
result = await code.implement_feature("Add JWT authentication")

# Web Team (Parallel: Researcher + Analyzer simultaneously)
web = WebTeam()
result = await web.research("AI agent frameworks 2024")

# Strategy Team (Hierarchical: Strategist delegates to Analyst + Risk)
strategy = StrategyTeam()
result = await strategy.develop_strategy("Enter European market")
```

### Memory System

Persistent memory across sessions:

```python
from optimus.memory import BrainDB, MemoryManager

# Direct SQLite access
brain = BrainDB("brain.db")
await brain.initialize()
await brain.store_memory("pattern", "Users prefer dark mode", {"source": "analytics"})
results = await brain.search_memories("pattern", "user preferences")

# Unified interface (with optional Mem0)
manager = MemoryManager(config)
await manager.initialize()
await manager.add("Important context for future tasks")
context = await manager.get_context("current task description")
```

### Security Guardrails

Built-in protection against malicious inputs:

```python
from optimus.security import GuardrailsManager

guardrails = GuardrailsManager(config)

# Check input
is_safe, reason = await guardrails.check_input(user_input)
if not is_safe:
    print(f"Blocked: {reason}")

# Check output
is_safe, reason = await guardrails.check_output(agent_output)
```

---

## Configuration

### Environment Variables

```bash
# Required: At least one LLM API key
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
OPENROUTER_API_KEY=sk-or-...   # Recommended: routes to 400+ models

# Optional: E2B for sandboxed execution
E2B_API_KEY=...

# Optional: AgentOps for monitoring
AGENTOPS_API_KEY=...

# For Trading Brain
HYPERLIQUID_WALLET_ADDRESS=0x...
HYPERLIQUID_PRIVATE_KEY=...
SLACK_WEBHOOK=https://hooks.slack.com/...
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

## CLI Commands

| Command | Description |
|---------|-------------|
| `optimus init <name>` | Initialize a new project |
| `optimus status` | Show system status and API keys |
| `optimus run --task "..." --team code` | Run a task with specified team |
| `optimus run --iterations 100` | Run autonomous loop |
| `optimus deploy --teams code,web,strategy` | Deploy agent teams |
| `optimus interactive` | Interactive REPL mode |
| `optimus banner` | Show the banner |

---

## Inspired By

Optimus Autonomous draws inspiration from 30+ excellent projects:

| Category | Projects |
|----------|----------|
| **Orchestration** | CrewAI, LangGraph, Ralphy, MEGAMIND, Eigent |
| **Memory** | Mem0, Graphiti, ChromaDB |
| **Tools** | MCP Servers, Playwright, Stagehand |
| **Execution** | E2B, Arrakis |
| **Security** | LLM Guard, NeMo Guardrails, Rebuff |
| **Observability** | AgentOps, OpenLit |
| **Research** | Nexus BT, AgentBench |

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
