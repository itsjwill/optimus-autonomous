# Codebase Concerns

**Analysis Date:** 2026-01-16

## Tech Debt

**Bare Exception Catching:**
- Issue: Bare `except:` clauses silently swallow all exceptions
- Files: `optimus/tools/file_tools.py` (lines ~201, ~385), `optimus/tools/web_tools.py` (lines ~71, ~115)
- Why: Quick implementation during prototyping
- Impact: Silent failures, hard to debug, lost stack traces
- Fix approach: Replace with specific exceptions (`except ValueError:`) or at minimum `except Exception as e:` with logging

**Unbounded Execution Log:**
- Issue: `_execution_log` list grows unbounded in memory
- File: `optimus/tools/registry.py` (line ~103)
- Why: No max size consideration during implementation
- Impact: Memory exhaustion in long-running applications
- Fix approach: Add max size limit with FIFO eviction, or periodic cleanup

**New HTTP Client Per Request:**
- Issue: Creates new `httpx.AsyncClient` for each request instead of reusing
- File: `optimus/tools/web_tools.py` (lines ~37-45)
- Why: Simplified implementation
- Impact: No connection pooling, performance degradation, wasted resources
- Fix approach: Create persistent client in `__init__`, use as instance variable

**Generic Exception Conversion:**
- Issue: Task failures only capture `str(e)` losing traceback
- File: `optimus/core/orchestrator.py` (line ~200)
- Why: Simple error handling
- Impact: Difficult to debug production failures
- Fix approach: Store full exception with traceback, or use structured error objects

## Known Bugs

**Race Condition in Global Registry:**
- Symptoms: Multiple registry instances could be created under concurrent access
- Trigger: Concurrent calls to `get_registry()` before initialization completes
- File: `optimus/tools/registry.py` (lines ~221-230)
- Workaround: Single-threaded usage only
- Root cause: `if _global_registry is None:` check not atomic
- Fix: Use threading.Lock or module-level initialization

**Execution Log Not Thread-Safe:**
- Symptoms: Corrupted log entries under concurrent tool execution
- Trigger: Multiple agents executing tools simultaneously
- File: `optimus/tools/registry.py` (lines ~167-173)
- Workaround: Sequential execution only
- Root cause: List append without locking

## Security Considerations

**Unsafe Local Code Execution:**
- Risk: Local fallback execution bypasses all sandboxing protections
- File: `optimus/security/sandbox.py` (lines ~174-225)
- Current mitigation: Prints warning "WARNING: Executing locally without sandbox!"
- Recommendations:
  - Add resource limits (memory, CPU, disk) for local execution
  - Require explicit user confirmation for local execution
  - Fail closed instead of falling back

**No URL Validation (SSRF Risk):**
- Risk: URLs passed to HTTP client without protocol validation
- File: `optimus/tools/web_tools.py` (line ~49)
- Current mitigation: None
- Recommendations:
  - Whitelist allowed protocols (https, http only)
  - Block file://, gopher://, and other dangerous schemes
  - Optionally block internal IP ranges

**Insufficient Code Validation:**
- Risk: Dangerous pattern detection uses simple regex that can be bypassed
- File: `optimus/security/sandbox.py` (lines ~227-269)
- Current mitigation: Basic pattern matching
- Recommendations:
  - Add detection for: `globals()`, `locals()`, `__dict__`, `vars()`, `compile()`
  - Consider AST-based analysis for Python code
  - Add more comprehensive bash pattern blocking

**API Key Exposure Risk:**
- Risk: Environment variables merged without sanitization to subprocess
- File: `optimus/tools/mcp_client.py` (line ~74)
- Current mitigation: None
- Recommendations:
  - Explicitly whitelist env vars passed to MCP servers
  - Never pass full environment
  - Audit MCP server configurations

## Performance Bottlenecks

**N+1 Query Pattern in Team Execution:**
- Problem: Each agent calls `memory.get_context()` separately
- File: `optimus/agents/team.py` (lines ~68-71)
- Measurement: 5 agents = 5 memory queries
- Cause: No batch context retrieval
- Improvement path: Add `memory.get_contexts(agent_names)` batch method

**Synchronous I/O in Async Context:**
- Problem: `run_in_executor(None, ...)` relies on default thread pool
- File: `optimus/memory/brain_db.py` (lines ~52-53)
- Measurement: Limited to ~5-10 threads per CPU
- Cause: Using sync SQLite API in async wrapper
- Improvement path: Already using aiosqlite, ensure all calls are truly async

## Fragile Areas

**MCP Server Connection State:**
- File: `optimus/tools/mcp_client.py`
- Why fragile: `servers` dict modified without locking during connect/disconnect
- Common failures: Connection state corruption under concurrent access
- Safe modification: Add asyncio.Lock around state mutations
- Test coverage: None

**Guardrails Pattern Matching:**
- File: `optimus/security/guardrails.py`
- Why fragile: Regex patterns can have edge cases, false positives/negatives
- Common failures: Legitimate content blocked, malicious content passes
- Safe modification: Test patterns against known attack corpus
- Test coverage: None

## Scaling Limits

**In-Memory Task Queue:**
- Current capacity: Limited by available RAM
- File: `optimus/core/orchestrator.py` (line ~54)
- Limit: Queue not persisted, lost on crash
- Symptoms at limit: Memory exhaustion, task loss
- Scaling path: Persist queue to SQLite or Redis

**SQLite Single-Writer:**
- Current capacity: One concurrent write operation
- File: `optimus/memory/brain_db.py`
- Limit: SQLite write lock blocks concurrent writes
- Symptoms at limit: Slow write operations under load
- Scaling path: Use PostgreSQL for high-write scenarios

## Dependencies at Risk

**Outdated Model Specs:**
- Risk: Model names hardcoded, may become deprecated
- File: `optimus/core/router.py` (lines ~59-68)
- Impact: API calls fail for deprecated models
- Migration plan: Move to config file, add model validation

**Playwright Browser Not Auto-Installed:**
- Risk: Browser tools fail at runtime if Playwright not properly installed
- File: `optimus/tools/browser.py`
- Impact: "Browser not installed" errors during execution
- Migration plan: Add install check and helpful error message

## Missing Critical Features

**No Test Suite:**
- Problem: Zero test coverage
- Current workaround: Manual testing only
- Blocks: CI/CD pipeline, confident refactoring
- Implementation complexity: Medium (need fixtures for mocking LLM APIs)

**No Request Retry Logic:**
- Problem: HTTP requests fail immediately on transient errors
- File: `optimus/tools/web_tools.py`
- Current workaround: Manual retry by user
- Blocks: Reliable API integration
- Implementation complexity: Low (add tenacity or backoff library)

**No Graceful Shutdown:**
- Problem: `stop()` sets flag but doesn't cancel in-progress tasks
- File: `optimus/core/orchestrator.py` (line ~295)
- Current workaround: Wait for current iteration to complete
- Blocks: Clean shutdown on SIGTERM
- Implementation complexity: Low (add task cancellation)

## Test Coverage Gaps

**No Tests Exist:**
- What's not tested: Everything
- Risk: Any change could break functionality silently
- Priority: Critical
- Difficulty to test: Medium (need mock LLM responses, async fixtures)

**Priority Areas for Testing:**
1. `optimus/security/guardrails.py` - Security critical
2. `optimus/tools/registry.py` - Core functionality
3. `optimus/memory/brain_db.py` - Data integrity
4. `optimus/core/orchestrator.py` - Main logic

## Summary Table

| Severity | File | Issue | Impact |
|----------|------|-------|--------|
| **CRITICAL** | `optimus/security/sandbox.py` | Unsafe local execution | Code execution risk |
| **CRITICAL** | `optimus/tools/web_tools.py` | No URL validation | SSRF vulnerability |
| **HIGH** | `optimus/tools/registry.py` | Unbounded log | Memory exhaustion |
| **HIGH** | `optimus/tools/web_tools.py` | No connection pooling | Performance |
| **HIGH** | All | No test suite | Quality/reliability |
| **MEDIUM** | `optimus/memory/brain_db.py` | No auto-close | Resource leaks |
| **MEDIUM** | `optimus/tools/registry.py` | Race in singleton | Concurrency bug |
| **MEDIUM** | `optimus/tools/file_tools.py` | Bare except | Silent failures |
| **LOW** | `optimus/core/router.py` | Hardcoded models | May fail at runtime |

---

*Concerns audit: 2026-01-16*
*Update as issues are fixed or new ones discovered*
