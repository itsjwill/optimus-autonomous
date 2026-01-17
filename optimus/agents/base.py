"""
Base Agent - Foundation for all Optimus agents
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AgentResponse:
    """Response from an agent execution."""
    success: bool
    output: str
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0
    tokens_used: int = 0
    cost: float = 0.0


class BaseAgent(ABC):
    """
    Base class for all Optimus agents.

    Provides:
    - Common interface for execution
    - Memory integration
    - Observability hooks
    - Error handling
    """

    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str = "",
        model: str = "claude-3-5-sonnet-20241022",
        verbose: bool = True
    ):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.model = model
        self.verbose = verbose
        self.memory = None
        self.tools: List[Any] = []
        self._execution_count = 0
        self._total_tokens = 0
        self._total_cost = 0.0

    @abstractmethod
    async def execute(self, task: str, context: Optional[str] = None) -> AgentResponse:
        """
        Execute a task.

        Args:
            task: The task description
            context: Optional context from memory or previous steps

        Returns:
            AgentResponse with results
        """
        pass

    def set_memory(self, memory) -> None:
        """Set the memory manager for context retrieval."""
        self.memory = memory

    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        self.tools.append(tool)

    async def get_context(self, task: str) -> str:
        """Get relevant context for a task from memory."""
        if not self.memory:
            return ""

        return await self.memory.get_context(task)

    def _log(self, message: str) -> None:
        """Log a message if verbose."""
        if self.verbose:
            print(f"[{self.name}] {message}")

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "name": self.name,
            "role": self.role,
            "executions": self._execution_count,
            "total_tokens": self._total_tokens,
            "total_cost": self._total_cost,
            "tools": len(self.tools),
        }


class LLMAgent(BaseAgent):
    """
    Agent that uses an LLM for task execution.
    Integrates with Anthropic Claude or OpenAI.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = None
        self._init_client()

    def _map_to_openrouter_model(self, model: str) -> str:
        """Map model names to OpenRouter format."""
        # Already in OpenRouter format
        if "/" in model:
            return model

        # Common model mappings
        model_map = {
            # Claude Sonnet 4
            "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4",
            "claude-sonnet-4": "anthropic/claude-sonnet-4",
            # Claude Sonnet 4.5
            "claude-4.5-sonnet": "anthropic/claude-sonnet-4.5",
            "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
            # Claude 3.5 Sonnet
            "claude-3-5-sonnet-20241022": "anthropic/claude-3.5-sonnet",
            "claude-3.5-sonnet": "anthropic/claude-3.5-sonnet",
            # Claude 3 Haiku (fast, cheap)
            "claude-3-haiku": "anthropic/claude-3-haiku",
            # GPT-4o
            "gpt-4o": "openai/gpt-4o",
            "gpt-4o-mini": "openai/gpt-4o-mini",
            "gpt-4-turbo": "openai/gpt-4-turbo",
        }

        if model.lower() in model_map:
            return model_map[model.lower()]

        # Default: prepend anthropic/ for claude models
        if "claude" in model.lower():
            return f"anthropic/{model}"
        elif "gpt" in model.lower():
            return f"openai/{model}"

        return model

    def _init_client(self) -> None:
        """Initialize the LLM client."""
        import os

        # Check for OpenRouter first (preferred for flexibility)
        openrouter_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=openrouter_key,
                    base_url="https://openrouter.ai/api/v1"
                )
                self.provider = "openrouter"
                # Map model names to OpenRouter format
                self.model = self._map_to_openrouter_model(self.model)
                print(f"[{self.name}] Using OpenRouter with {self.model}")
                return
            except ImportError:
                print(f"[{self.name}] OpenAI package not installed (needed for OpenRouter).")

        # Fall back to direct Anthropic
        if "claude" in self.model.lower():
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = Anthropic(api_key=api_key)
                    self.provider = "anthropic"
                    return
            except ImportError:
                print(f"[{self.name}] Anthropic not installed.")

        # Fall back to OpenAI
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                self.provider = "openai"
        except ImportError:
            print(f"[{self.name}] OpenAI not installed.")

    async def execute(self, task: str, context: Optional[str] = None) -> AgentResponse:
        """Execute a task using the LLM."""
        start_time = datetime.now()

        if not self.client:
            return AgentResponse(
                success=False,
                output="LLM client not initialized. Check API keys.",
            )

        # Build the prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(task, context)

        try:
            if self.provider == "anthropic":
                response = await self._call_anthropic(system_prompt, user_prompt)
            elif self.provider == "openrouter":
                response = await self._call_openrouter(system_prompt, user_prompt)
            else:
                response = await self._call_openai(system_prompt, user_prompt)

            duration = (datetime.now() - start_time).total_seconds() * 1000
            self._execution_count += 1

            return AgentResponse(
                success=True,
                output=response["content"],
                tokens_used=response.get("tokens", 0),
                cost=response.get("cost", 0),
                duration_ms=duration,
                metadata={
                    "model": self.model,
                    "provider": self.provider,
                }
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                output=f"Execution error: {str(e)}",
            )

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        return f"""You are {self.name}, a specialized AI agent.

Role: {self.role}
Goal: {self.goal}

{self.backstory}

You are part of Optimus Autonomous, a multi-agent system. Execute tasks efficiently and return clear, actionable results.
"""

    def _build_user_prompt(self, task: str, context: Optional[str]) -> str:
        """Build the user prompt with task and context."""
        prompt = f"Task: {task}"

        if context:
            prompt = f"Context:\n{context}\n\n{prompt}"

        return prompt

    async def _call_anthropic(self, system: str, user: str) -> Dict[str, Any]:
        """Call Anthropic Claude API."""
        import asyncio

        loop = asyncio.get_event_loop()

        def call():
            """Sync wrapper for Anthropic API call."""
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": user}]
            )
            return {
                "content": response.content[0].text,
                "tokens": response.usage.input_tokens + response.usage.output_tokens,
                "cost": self._calculate_cost(response.usage, "anthropic"),
            }

        return await loop.run_in_executor(None, call)

    async def _call_openai(self, system: str, user: str) -> Dict[str, Any]:
        """Call OpenAI API."""
        import asyncio

        loop = asyncio.get_event_loop()

        def call():
            """Sync wrapper for OpenAI API call."""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ]
            )
            return {
                "content": response.choices[0].message.content,
                "tokens": response.usage.total_tokens,
                "cost": self._calculate_cost(response.usage, "openai"),
            }

        return await loop.run_in_executor(None, call)

    async def _call_openrouter(self, system: str, user: str) -> Dict[str, Any]:
        """Call OpenRouter API (OpenAI-compatible)."""
        import asyncio
        import os

        loop = asyncio.get_event_loop()

        def call():
            """Sync wrapper for OpenRouter API call."""
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                extra_headers={
                    "HTTP-Referer": "https://github.com/itsjwill/optimus-autonomous",
                    "X-Title": "Optimus Trading Brain"
                }
            )

            # Calculate cost based on model
            tokens = response.usage.total_tokens if response.usage else 0
            cost = self._calculate_cost_openrouter(
                response.usage.prompt_tokens if response.usage else 0,
                response.usage.completion_tokens if response.usage else 0
            )

            return {
                "content": response.choices[0].message.content,
                "tokens": tokens,
                "cost": cost,
            }

        return await loop.run_in_executor(None, call)

    def _calculate_cost_openrouter(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for OpenRouter based on model."""
        # OpenRouter pricing per 1M tokens (as of Jan 2026)
        costs = {
            # Claude Sonnet 4.x
            "anthropic/claude-sonnet-4": {"input": 3.0, "output": 15.0},
            "anthropic/claude-sonnet-4.5": {"input": 3.0, "output": 15.0},
            # Claude 3.x
            "anthropic/claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
            "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
            # OpenAI
            "openai/gpt-4-turbo": {"input": 10.0, "output": 30.0},
            "openai/gpt-4o": {"input": 2.5, "output": 10.0},
            "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
        }

        rates = costs.get(self.model, {"input": 3.0, "output": 15.0})
        input_cost = (input_tokens / 1_000_000) * rates["input"]
        output_cost = (output_tokens / 1_000_000) * rates["output"]

        total = input_cost + output_cost
        self._total_cost += total
        self._total_tokens += input_tokens + output_tokens

        return total

    def _calculate_cost(self, usage, provider: str) -> float:
        """Calculate cost based on token usage."""
        # Approximate costs per 1M tokens
        costs = {
            "anthropic": {"input": 3.0, "output": 15.0},  # Claude 3.5 Sonnet
            "openai": {"input": 2.5, "output": 10.0},  # GPT-4 Turbo
        }

        rates = costs.get(provider, costs["anthropic"])

        if provider == "anthropic":
            input_cost = (usage.input_tokens / 1_000_000) * rates["input"]
            output_cost = (usage.output_tokens / 1_000_000) * rates["output"]
        else:
            # OpenAI doesn't split input/output in usage
            input_cost = (usage.prompt_tokens / 1_000_000) * rates["input"]
            output_cost = (usage.completion_tokens / 1_000_000) * rates["output"]

        total = input_cost + output_cost
        self._total_cost += total
        self._total_tokens += usage.input_tokens + usage.output_tokens if provider == "anthropic" else usage.total_tokens

        return total
