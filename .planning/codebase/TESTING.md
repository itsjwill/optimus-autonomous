# Testing Patterns

**Analysis Date:** 2026-01-16

## Test Framework

**Runner:**
- pytest 7.4.0+ (specified in `requirements.txt`)
- pytest-asyncio 0.23.0+ for async test support
- No other testing frameworks detected

**Assertion Library:**
- pytest built-in assert
- No additional assertion libraries

**Run Commands:**
```bash
pytest                              # Run all tests (when implemented)
pytest --asyncio-mode=auto          # Auto-detect async tests
pytest path/to/test_file.py         # Single file
pytest -v                           # Verbose output
```

## Test File Organization

**Current State: NO TESTS FOUND**
- No `tests/` directory exists
- No `__tests__/` directory exists
- No files matching `*test*.py` or `test_*.py` patterns
- Project is v0.1.0 (early development stage)

**Recommended Location:**
- `tests/` directory at project root
- Co-located tests not currently used

**Recommended Naming:**
- `test_module_name.py` to match each module
- Test functions: `test_` prefix

**Recommended Structure:**
```
optimus-autonomous/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── unit/
│   │   ├── test_config.py       # optimus/core/config.py
│   │   ├── test_registry.py     # optimus/tools/registry.py
│   │   ├── test_brain_db.py     # optimus/memory/brain_db.py
│   │   ├── test_guardrails.py   # optimus/security/guardrails.py
│   │   └── test_metrics.py      # optimus/observability/metrics.py
│   ├── integration/
│   │   ├── test_orchestrator.py # Full orchestrator tests
│   │   ├── test_agent_team.py   # Team coordination
│   │   └── test_memory_system.py # Memory backends
│   └── e2e/
│       └── test_workflows.py    # End-to-end flows
```

## Test Structure

**Recommended Suite Organization:**
```python
import pytest
from optimus.tools.registry import ToolRegistry, Tool, ToolCategory

class TestToolRegistry:
    """Tests for ToolRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create fresh registry for each test."""
        return ToolRegistry()

    def test_register_tool(self, registry):
        """Should register a tool successfully."""
        # arrange
        tool = Tool(name="test", description="Test tool", func=lambda: None)

        # act
        registry.register(tool)

        # assert
        assert registry.get("test") == tool

    def test_get_nonexistent_tool(self, registry):
        """Should return None for unknown tool."""
        assert registry.get("unknown") is None
```

**Async Test Pattern:**
```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """Should handle async operations."""
    result = await some_async_function()
    assert result.success is True
```

**Patterns:**
- Use `@pytest.fixture` for setup
- AAA pattern: Arrange, Act, Assert
- One assertion focus per test (multiple asserts OK)
- Descriptive test names with "should" format

## Mocking

**Framework:**
- pytest-mock (recommended addition)
- unittest.mock built-in

**Recommended Patterns:**
```python
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_llm_agent_with_mock():
    """Should call LLM API correctly."""
    with patch('optimus.agents.base.anthropic') as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        agent = LLMAgent(name="test", model="claude-3-5-sonnet-20241022")
        result = await agent.execute("test prompt")

        mock_client.messages.create.assert_called_once()
```

**What to Mock:**
- External LLM APIs (Anthropic, OpenAI)
- File system operations
- HTTP requests (httpx client)
- SQLite database connections
- Time/dates for deterministic tests

**What NOT to Mock:**
- Pure functions and utilities
- Dataclasses and simple data structures
- Internal business logic

## Fixtures and Factories

**Recommended Test Data:**
```python
# tests/conftest.py
import pytest
from optimus.core.config import OptimusConfig
from optimus.tools.registry import ToolRegistry

@pytest.fixture
def config():
    """Create test configuration."""
    return OptimusConfig(
        project_name="test-project",
        anthropic_api_key="test-key",
        memory_enabled=False,
        guardrails_enabled=False,
    )

@pytest.fixture
def registry():
    """Create clean tool registry."""
    return ToolRegistry()

@pytest.fixture
def mock_llm_response():
    """Create mock LLM response."""
    return {
        "content": [{"text": "Test response"}],
        "usage": {"input_tokens": 10, "output_tokens": 20}
    }
```

**Location:**
- Shared fixtures: `tests/conftest.py`
- Test-specific fixtures: In test file

## Coverage

**Requirements:**
- No enforced coverage target currently
- Recommended: 80% for critical paths

**Configuration (Recommended):**
```ini
# pytest.ini or pyproject.toml
[tool:pytest]
asyncio_mode = auto

[tool:coverage.run]
source = optimus
omit = */tests/*
```

**View Coverage:**
```bash
pytest --cov=optimus --cov-report=html
open htmlcov/index.html
```

## Test Types

**Unit Tests:**
- Scope: Single function/class in isolation
- Mocking: All external dependencies
- Speed: Each test <100ms
- Priority: High (foundation of test suite)

**Integration Tests:**
- Scope: Multiple modules together
- Mocking: External APIs only
- Examples: Orchestrator + Team + Memory

**E2E Tests:**
- Scope: Full user workflows
- Mocking: Minimal (maybe LLM APIs)
- Examples: `optimus init` → `optimus run`

## Common Patterns

**Async Testing:**
```python
@pytest.mark.asyncio
async def test_brain_db_store():
    """Should store memory entry."""
    db = BrainDB(":memory:")
    await db.initialize()

    await db.store_memory("test", "content", {"key": "value"})
    result = await db.get_memory("test")

    assert result is not None
    assert result.content == "content"
```

**Error Testing:**
```python
def test_invalid_config_raises():
    """Should raise on invalid configuration."""
    with pytest.raises(ValueError, match="API key required"):
        OptimusConfig(anthropic_api_key=None, openai_api_key=None)
```

**Parametrized Tests:**
```python
@pytest.mark.parametrize("input,expected", [
    ("test", True),
    ("", False),
    (None, False),
])
def test_validation(input, expected):
    """Should validate input correctly."""
    assert validate(input) == expected
```

**Snapshot Testing:**
- Not currently used
- Could be useful for LLM prompt templates

---

*Testing analysis: 2026-01-16*
*Update when test patterns change*
