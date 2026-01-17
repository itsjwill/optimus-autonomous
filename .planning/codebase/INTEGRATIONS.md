# External Integrations

**Analysis Date:** 2026-01-16

## APIs & External Services

**LLM Providers:**
- Anthropic Claude - Primary LLM provider
  - SDK/Client: `anthropic>=0.30.0` (`optimus/agents/base.py`)
  - Auth: API key in `ANTHROPIC_API_KEY` env var
  - Models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-haiku-20240307

- OpenAI GPT - Alternative LLM provider
  - SDK/Client: `openai>=1.30.0` (`optimus/agents/base.py`)
  - Auth: API key in `OPENAI_API_KEY` env var
  - Models: gpt-4-turbo, gpt-4o, gpt-3.5-turbo

**Code Execution:**
- E2B - Cloud sandbox execution (optional)
  - SDK/Client: E2B SDK (`optimus/security/sandbox.py`)
  - Auth: API key in `E2B_API_KEY` env var
  - Fallback: Local execution without sandbox

**MCP Protocol:**
- Model Context Protocol - 200+ tools via MCP servers (`optimus/tools/mcp_client.py`)
  - Pre-configured servers: filesystem, GitHub, PostgreSQL, SQLite, Puppeteer, Brave Search, Fetch, Memory, Slack, Google Drive
  - Custom server support via stdio-based communication

## Data Storage

**Databases:**
- SQLite (BrainDB) - Primary data store (`optimus/memory/brain_db.py`)
  - Connection: Local file `brain.db` in project directory
  - Client: `aiosqlite>=0.19.0` (async)
  - Tables: memories, patterns, decisions, tasks, iterations

**Optional Memory Backends:**
- Mem0 - Universal semantic memory (install separately)
  - Auto-init when available
  - Cross-session persistence

- ChromaDB - Vector embeddings (install separately)
  - Auto-init when available
  - Embedding search capabilities

**File Storage:**
- Local filesystem only
- No cloud storage integration

**Caching:**
- In-memory caching only
- No Redis or external cache

## Authentication & Identity

**Auth Provider:**
- None - No user authentication system
- API keys stored in environment variables

**OAuth Integrations:**
- None

## Monitoring & Observability

**Error Tracking:**
- Custom event observer (`optimus/observability/observer.py`)
  - Event logging to `optimus_events.jsonl`
  - Session-based tracking

**Analytics:**
- AgentOps - Agent monitoring (optional)
  - SDK: AgentOps client (`optimus/core/orchestrator.py`)
  - Auth: `AGENTOPS_API_KEY` env var
  - Features: Cost tracking, session monitoring

**Logs:**
- JSONL event log (`optimus_events.jsonl` in project directory)
- Console output via Rich library

## CI/CD & Deployment

**Hosting:**
- Self-hosted only (no cloud deployment configured)
- Runs locally via Python CLI

**CI Pipeline:**
- None configured
- No GitHub Actions or similar

## Environment Configuration

**Development:**
- Required env vars: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (at least one)
- Optional: `E2B_API_KEY`, `AGENTOPS_API_KEY`
- Secrets location: `.env` file (gitignored)
- Mock services: None (uses real APIs)

**Staging:**
- Not applicable (no staging environment)

**Production:**
- Same as development
- Secrets: Environment variables

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Integration Matrix

| Service | Type | Required? | File | Config |
|---------|------|-----------|------|--------|
| Anthropic Claude | LLM | Optional* | `optimus/agents/base.py` | `ANTHROPIC_API_KEY` |
| OpenAI GPT | LLM | Optional* | `optimus/agents/base.py` | `OPENAI_API_KEY` |
| E2B | Sandbox | Optional | `optimus/security/sandbox.py` | `E2B_API_KEY` |
| AgentOps | Monitoring | Optional | `optimus/observability/observer.py` | `AGENTOPS_API_KEY` |
| Mem0 | Memory | Optional | `optimus/memory/manager.py` | Auto-init |
| ChromaDB | Vector DB | Optional | `optimus/memory/` | Auto-init |
| LLM Guard | Security | Optional | `optimus/security/guardrails.py` | Auto-init |
| Playwright | Browser | Optional | `optimus/tools/browser.py` | Auto-download |
| MCP Servers | Tools | Optional | `optimus/tools/mcp_client.py` | Custom config |

*At least one LLM provider required

---

*Integration audit: 2026-01-16*
*Update when adding/removing external services*
