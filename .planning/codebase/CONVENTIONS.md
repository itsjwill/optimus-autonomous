# Coding Conventions

**Analysis Date:** 2026-01-16

## Naming Patterns

**Files:**
- `snake_case.py` for all Python files
- Examples: `brain_db.py`, `web_tools.py`, `mcp_client.py`, `knowledge_graph.py`
- `__init__.py` for package directories
- No test files present (v0.1.0 early stage)

**Functions:**
- `snake_case` for all functions and methods
- Private methods: single underscore prefix (`_init_sync()`, `_create_tables()`, `_validate_path()`)
- Action verbs: `execute()`, `initialize()`, `register()`, `validate()`, `store_memory()`
- Getters: `get_` prefix (`get_context()`, `get_registry()`, `get_stats()`)

**Variables:**
- `snake_case` for variables and parameters
- Descriptive names: `base_path`, `max_file_size`, `db_path`, `task_queue`
- Collections: plural form (`tools`, `agents`, `memories`, `patterns`)
- Booleans: `is_/has_` implied (`_initialized`, `_running`, `enabled`)

**Types:**
- `PascalCase` for classes: `BaseAgent`, `ToolRegistry`, `GuardrailsManager`
- Manager classes: `*Manager` suffix (`MemoryManager`, `GuardrailsManager`, `SandboxManager`)
- Result classes: `*Result` suffix (`ToolResult`, `GuardrailResult`, `AgentResponse`)
- No `I` prefix for interfaces

**Constants:**
- `UPPER_SNAKE_CASE` for constants
- Examples: `DEFAULT_MODEL`, `DEFAULT_TEMPERATURE`, `COST_RATES`, `VERSION`
- Location: `optimus/constants.py`

**Enums:**
- `PascalCase` for enum classes: `ToolCategory`, `TaskComplexity`, `TaskType`
- `UPPER_SNAKE_CASE` for enum values: `FILE`, `WEB`, `SIMPLE`, `EXPERT`
- Example: `optimus/tools/registry.py`, `optimus/core/router.py`

## Code Style

**Formatting:**
- 4-space indentation (Python standard)
- Double quotes (`"`) for strings consistently
- No semicolons (Python convention)
- Line length: Generally under 100 characters
- Single blank line between methods
- Double blank line between class definitions

**Linting:**
- No linting config found (.flake8, pylintrc, pyproject.toml)
- Code follows PEP 8 conventions implicitly
- Would benefit from: Black, Flake8, mypy

## Import Organization

**Order:**
1. Standard library imports (`asyncio`, `json`, `re`, `datetime`)
2. Third-party imports (`anthropic`, `openai`, `httpx`, `pydantic`)
3. Local imports (relative: `from .registry import Tool`)

**Grouping:**
- Blank line between import groups
- Multiple imports from same module on one line when short
- Type imports mixed with regular imports

**Path Aliases:**
- Relative imports within package: `from .registry import Tool`
- Absolute imports from package root: `from optimus.core.config import OptimusConfig`

## Error Handling

**Patterns:**
- Try-except at function/method boundaries
- Custom result objects for error propagation (`ToolResult`, `GuardrailResult`)
- Exception details captured in result objects

**Error Types:**
- Throw on: Import errors, validation failures, API errors
- Return result on: Expected operation failures
- Log with context: `print(f"[COMPONENT] Error message: {e}")`

## Logging

**Framework:**
- `print()` statements with component prefix
- Rich library for formatted console output
- JSONL for persistent event logging

**Patterns:**
- Format: `[COMPONENT] Message` (e.g., `[OBSERVER] Session started`)
- Levels implied by message content (no formal log levels)
- Debug info to console, structured data to JSONL

## Comments

**When to Comment:**
- Explain "why" not "what"
- Document complex regex patterns
- Note configuration options and defaults

**Docstrings:**
- Triple-quote docstrings on all classes and public methods
- Format: Summary line, blank line, description
- Args/Returns sections for complex functions
- Example from `optimus/tools/file_tools.py`:
```python
def read_file(self, path: str, max_lines: int = 1000) -> ToolResult:
    """
    Read a file from the filesystem.

    Args:
        path: Path to the file
        max_lines: Maximum lines to read

    Returns:
        ToolResult with file content
    """
```

**TODO Comments:**
- Format: `# TODO: description`
- No username tracking (use git blame)

## Function Design

**Size:**
- Keep under 50 lines when possible
- Extract helpers for complex logic
- One level of abstraction per function

**Parameters:**
- Max 3-4 parameters typical
- Use dataclasses for complex parameter groups
- Optional parameters have defaults: `max_lines: int = 1000`

**Return Values:**
- Explicit returns
- Return early for guard clauses
- Use result objects for success/failure states

## Module Design

**Exports:**
- `__init__.py` files define public API
- Named exports preferred
- Version exported from package root

**Dataclasses:**
- Extensive use of `@dataclass` decorator
- Default factories for mutable defaults: `field(default_factory=dict)`
- Examples: `Task`, `Iteration`, `Tool`, `ToolResult`, `AgentResponse`

**Async Patterns:**
- `async def` for I/O operations
- `await` for async calls
- `asyncio.iscoroutinefunction()` for runtime detection
- `run_in_executor()` for sync-to-async conversion

## Type Hints

**Usage:**
- Comprehensive type hints throughout codebase
- `Optional` for nullable types
- `Dict`, `List`, `Tuple`, `Any` from `typing`
- Generic types specified: `Dict[str, Any]`, `List[Dict[str, Any]]`

**Example:**
```python
async def execute(self, tool_name: str, **kwargs) -> ToolResult:
    """Execute a tool by name."""
    tool = self.get(tool_name)
    if not tool:
        return ToolResult(success=False, output=None, error=f"Tool not found: {tool_name}")
```

---

*Convention analysis: 2026-01-16*
*Update when patterns change*
