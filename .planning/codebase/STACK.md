# Technology Stack

**Analysis Date:** 2026-01-16

## Languages

**Primary:**
- Python 3.12 - All application code (28 Python files)

**Secondary:**
- None detected

## Runtime

**Environment:**
- Python 3.12+
- Async-first architecture using `asyncio`
- No Node.js, Go, Rust, or other runtimes

**Package Manager:**
- pip
- Lockfile: `requirements.txt` present (no poetry.lock or Pipfile)

## Frameworks

**Core:**
- None (vanilla Python with custom orchestration framework)

**Agent Orchestration (Optional - install separately):**
- CrewAI - Role-based agent collaboration
- LangGraph - Cyclical workflows with state management

**Testing:**
- pytest 7.4.0+ - Test framework
- pytest-asyncio 0.23.0+ - Async test support

**Build/Dev:**
- No build tools required (pure Python)
- No TypeScript compiler

## Key Dependencies

**Critical (LLM Providers):**
- `anthropic>=0.30.0` - Claude LLM provider (`optimus/agents/base.py`)
- `openai>=1.30.0` - GPT LLM provider (`optimus/agents/base.py`)

**Configuration & Data:**
- `PyYAML>=6.0` - YAML config parsing (`optimus/core/config.py`)
- `pydantic>=2.5.0` - Data validation
- `python-dotenv>=1.0.0` - Environment variable loading

**HTTP & Web:**
- `httpx>=0.26.0` - Async HTTP client (`optimus/tools/web_tools.py`)
- `aiohttp>=3.9.0` - Async web requests
- `playwright>=1.40.0` - Headless browser automation (`optimus/tools/browser.py`)
- `beautifulsoup4>=4.12.0` - HTML parsing

**Database:**
- `aiosqlite>=0.19.0` - Async SQLite (`optimus/memory/brain_db.py`)

**CLI & Utilities:**
- `click>=8.1.0` - CLI framework (`optimus.py`)
- `rich>=13.7.0` - Terminal formatting (`banner.py`)

## Configuration

**Environment:**
- `.env` files for secrets
- Required: `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` (at least one)
- Optional: `E2B_API_KEY`, `AGENTOPS_API_KEY`

**Project Config:**
- `optimus.yaml` - Project configuration (generated on init)
- Dataclass-based config with environment variable override support

**Build:**
- No build configuration (interpreted Python)
- No `pyproject.toml` or `setup.py` currently

## Platform Requirements

**Development:**
- macOS/Linux/Windows (any platform with Python 3.12+)
- Optional: Playwright browsers (`playwright install chromium`)
- Optional: Docker for sandboxed execution

**Production:**
- Python 3.12+ runtime
- SQLite for BrainDB storage
- Optional: E2B cloud sandbox API access

---

*Stack analysis: 2026-01-16*
*Update after major dependency changes*
