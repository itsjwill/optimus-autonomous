"""
Model Router - Smart model selection for tasks
Routes tasks to optimal models based on complexity, cost, and requirements.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class TaskComplexity(Enum):
    """Task complexity levels."""
    SIMPLE = "simple"      # Quick, straightforward tasks
    MODERATE = "moderate"  # Standard tasks requiring reasoning
    COMPLEX = "complex"    # Complex analysis or generation
    EXPERT = "expert"      # Tasks requiring deep expertise


class TaskType(Enum):
    """Types of tasks."""
    CODE = "code"
    ANALYSIS = "analysis"
    WRITING = "writing"
    RESEARCH = "research"
    MATH = "math"
    CONVERSATION = "conversation"
    CREATIVE = "creative"
    DATA = "data"


@dataclass
class ModelSpec:
    """Specification for a model."""
    name: str
    provider: str
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    speed_rating: float  # 1-10, higher is faster
    quality_rating: float  # 1-10, higher is better
    capabilities: List[str] = field(default_factory=list)
    max_output_tokens: int = 4096


@dataclass
class RoutingDecision:
    """A routing decision."""
    model: str
    reason: str
    confidence: float
    estimated_cost: float
    estimated_tokens: int


# Available models with their specifications
MODELS: Dict[str, ModelSpec] = {
    # Anthropic Models
    "claude-3-5-sonnet-20241022": ModelSpec(
        name="claude-3-5-sonnet-20241022",
        provider="anthropic",
        context_window=200000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        speed_rating=8,
        quality_rating=9,
        capabilities=["code", "analysis", "writing", "research", "math", "creative"],
        max_output_tokens=8192
    ),
    "claude-3-opus-20240229": ModelSpec(
        name="claude-3-opus-20240229",
        provider="anthropic",
        context_window=200000,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        speed_rating=5,
        quality_rating=10,
        capabilities=["code", "analysis", "writing", "research", "math", "creative", "expert"],
        max_output_tokens=4096
    ),
    "claude-3-haiku-20240307": ModelSpec(
        name="claude-3-haiku-20240307",
        provider="anthropic",
        context_window=200000,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.00125,
        speed_rating=10,
        quality_rating=7,
        capabilities=["code", "analysis", "writing", "conversation"],
        max_output_tokens=4096
    ),

    # OpenAI Models
    "gpt-4-turbo": ModelSpec(
        name="gpt-4-turbo",
        provider="openai",
        context_window=128000,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        speed_rating=7,
        quality_rating=9,
        capabilities=["code", "analysis", "writing", "research", "math", "creative"],
        max_output_tokens=4096
    ),
    "gpt-4o": ModelSpec(
        name="gpt-4o",
        provider="openai",
        context_window=128000,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        speed_rating=8,
        quality_rating=9,
        capabilities=["code", "analysis", "writing", "research", "math", "creative", "vision"],
        max_output_tokens=4096
    ),
    "gpt-4o-mini": ModelSpec(
        name="gpt-4o-mini",
        provider="openai",
        context_window=128000,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        speed_rating=10,
        quality_rating=7,
        capabilities=["code", "analysis", "writing", "conversation"],
        max_output_tokens=16384
    ),
    "gpt-3.5-turbo": ModelSpec(
        name="gpt-3.5-turbo",
        provider="openai",
        context_window=16385,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0015,
        speed_rating=10,
        quality_rating=6,
        capabilities=["code", "writing", "conversation"],
        max_output_tokens=4096
    ),
}


class ModelRouter:
    """
    Smart model router for Optimus.

    Routes tasks to optimal models based on:
    - Task complexity and type
    - Required capabilities
    - Cost constraints
    - Speed requirements
    - Context length needs
    """

    def __init__(
        self,
        default_model: str = "claude-3-5-sonnet-20241022",
        available_providers: Optional[List[str]] = None,
        max_cost_per_request: Optional[float] = None,
        prefer_speed: bool = False
    ):
        """
        Initialize the router.

        Args:
            default_model: Default model to use
            available_providers: List of available providers (filters models)
            max_cost_per_request: Maximum cost constraint
            prefer_speed: Prefer faster models over quality
        """
        self.default_model = default_model
        self.available_providers = available_providers or ["anthropic", "openai"]
        self.max_cost_per_request = max_cost_per_request
        self.prefer_speed = prefer_speed
        self._usage_history: List[Dict] = []

    def route(
        self,
        task: str,
        task_type: Optional[TaskType] = None,
        complexity: Optional[TaskComplexity] = None,
        estimated_tokens: int = 2000,
        required_capabilities: Optional[List[str]] = None
    ) -> RoutingDecision:
        """
        Route a task to the optimal model.

        Args:
            task: The task description
            task_type: Type of task (auto-detected if not provided)
            complexity: Task complexity (auto-detected if not provided)
            estimated_tokens: Estimated output tokens needed
            required_capabilities: Required model capabilities

        Returns:
            RoutingDecision with chosen model and reasoning
        """
        # Auto-detect task type and complexity
        if not task_type:
            task_type = self._detect_task_type(task)
        if not complexity:
            complexity = self._detect_complexity(task)

        # Get candidate models
        candidates = self._get_candidates(task_type, required_capabilities)

        if not candidates:
            # Fallback to default
            return RoutingDecision(
                model=self.default_model,
                reason="No matching models found, using default",
                confidence=0.5,
                estimated_cost=self._estimate_cost(self.default_model, estimated_tokens),
                estimated_tokens=estimated_tokens
            )

        # Score and rank candidates
        scored = []
        for model_name in candidates:
            model = MODELS[model_name]
            score = self._score_model(model, complexity, estimated_tokens)
            scored.append((model_name, score))

        # Sort by score (higher is better)
        scored.sort(key=lambda x: x[1], reverse=True)

        best_model = scored[0][0]
        best_score = scored[0][1]

        # Build reasoning
        reason = self._build_reason(best_model, task_type, complexity)
        estimated_cost = self._estimate_cost(best_model, estimated_tokens)

        # Log decision
        self._log_decision(task, best_model, task_type, complexity, estimated_cost)

        return RoutingDecision(
            model=best_model,
            reason=reason,
            confidence=min(best_score / 10, 1.0),
            estimated_cost=estimated_cost,
            estimated_tokens=estimated_tokens
        )

    def _detect_task_type(self, task: str) -> TaskType:
        """Detect the type of task from its description."""
        task_lower = task.lower()

        # Code indicators
        code_keywords = ["code", "function", "implement", "bug", "debug", "refactor", "api", "program", "script"]
        if any(kw in task_lower for kw in code_keywords):
            return TaskType.CODE

        # Analysis indicators
        analysis_keywords = ["analyze", "examine", "evaluate", "assess", "compare", "review"]
        if any(kw in task_lower for kw in analysis_keywords):
            return TaskType.ANALYSIS

        # Research indicators
        research_keywords = ["research", "find", "search", "investigate", "explore", "discover"]
        if any(kw in task_lower for kw in research_keywords):
            return TaskType.RESEARCH

        # Writing indicators
        writing_keywords = ["write", "draft", "compose", "create", "document", "email", "blog", "article"]
        if any(kw in task_lower for kw in writing_keywords):
            return TaskType.WRITING

        # Math indicators
        math_keywords = ["calculate", "compute", "math", "equation", "formula", "statistics"]
        if any(kw in task_lower for kw in math_keywords):
            return TaskType.MATH

        # Creative indicators
        creative_keywords = ["creative", "story", "poem", "brainstorm", "imagine", "design"]
        if any(kw in task_lower for kw in creative_keywords):
            return TaskType.CREATIVE

        # Data indicators
        data_keywords = ["data", "csv", "json", "parse", "transform", "process"]
        if any(kw in task_lower for kw in data_keywords):
            return TaskType.DATA

        return TaskType.CONVERSATION

    def _detect_complexity(self, task: str) -> TaskComplexity:
        """Detect the complexity of a task."""
        task_lower = task.lower()

        # Expert indicators
        expert_keywords = ["complex", "advanced", "expert", "sophisticated", "comprehensive", "in-depth"]
        if any(kw in task_lower for kw in expert_keywords):
            return TaskComplexity.EXPERT

        # Complex indicators
        complex_keywords = ["multiple", "detailed", "thorough", "complete", "full", "all aspects"]
        if any(kw in task_lower for kw in complex_keywords):
            return TaskComplexity.COMPLEX

        # Simple indicators
        simple_keywords = ["simple", "quick", "brief", "short", "basic", "easy"]
        if any(kw in task_lower for kw in simple_keywords):
            return TaskComplexity.SIMPLE

        # Length-based heuristic
        if len(task) > 500:
            return TaskComplexity.COMPLEX
        elif len(task) < 100:
            return TaskComplexity.SIMPLE

        return TaskComplexity.MODERATE

    def _get_candidates(self, task_type: TaskType, required_capabilities: Optional[List[str]]) -> List[str]:
        """Get candidate models for a task."""
        candidates = []

        for name, model in MODELS.items():
            # Filter by provider
            if model.provider not in self.available_providers:
                continue

            # Check required capabilities
            if required_capabilities:
                if not all(cap in model.capabilities for cap in required_capabilities):
                    continue

            # Check task type capability
            if task_type.value not in model.capabilities:
                # Allow models without specific capability for general tasks
                if task_type not in [TaskType.CONVERSATION]:
                    continue

            candidates.append(name)

        return candidates

    def _score_model(self, model: ModelSpec, complexity: TaskComplexity, estimated_tokens: int) -> float:
        """Score a model for a task."""
        score = 0.0

        # Quality score (weighted by complexity)
        complexity_weights = {
            TaskComplexity.SIMPLE: 0.3,
            TaskComplexity.MODERATE: 0.5,
            TaskComplexity.COMPLEX: 0.7,
            TaskComplexity.EXPERT: 0.9,
        }
        quality_weight = complexity_weights.get(complexity, 0.5)
        score += model.quality_rating * quality_weight

        # Speed score (inversely weighted by complexity)
        speed_weight = 1 - quality_weight
        if self.prefer_speed:
            speed_weight *= 1.5
        score += model.speed_rating * speed_weight

        # Cost penalty
        estimated_cost = self._estimate_cost(model.name, estimated_tokens)
        if self.max_cost_per_request and estimated_cost > self.max_cost_per_request:
            score *= 0.5  # Penalize expensive models

        # Normalize cost penalty (cheaper is better)
        max_cost = 0.10  # Reference max cost
        cost_factor = 1 - min(estimated_cost / max_cost, 1)
        score += cost_factor * 2  # Cost bonus

        return score

    def _estimate_cost(self, model_name: str, tokens: int) -> float:
        """Estimate cost for a model and token count."""
        if model_name not in MODELS:
            return 0.0

        model = MODELS[model_name]
        # Assume 50/50 input/output split for estimation
        input_tokens = tokens * 0.5
        output_tokens = tokens * 0.5

        input_cost = (input_tokens / 1000) * model.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model.cost_per_1k_output

        return input_cost + output_cost

    def _build_reason(self, model: str, task_type: TaskType, complexity: TaskComplexity) -> str:
        """Build reasoning for model selection."""
        model_spec = MODELS.get(model)
        if not model_spec:
            return f"Selected {model}"

        reasons = []

        if complexity == TaskComplexity.EXPERT:
            reasons.append(f"expert-level task requires high-quality model")
        elif complexity == TaskComplexity.SIMPLE:
            reasons.append(f"simple task allows faster model")

        reasons.append(f"task type: {task_type.value}")
        reasons.append(f"quality: {model_spec.quality_rating}/10")
        reasons.append(f"speed: {model_spec.speed_rating}/10")

        return f"Selected {model}: " + ", ".join(reasons)

    def _log_decision(self, task: str, model: str, task_type: TaskType, complexity: TaskComplexity, cost: float) -> None:
        """Log a routing decision."""
        self._usage_history.append({
            "timestamp": datetime.now().isoformat(),
            "task_preview": task[:100],
            "model": model,
            "task_type": task_type.value,
            "complexity": complexity.value,
            "estimated_cost": cost
        })

        # Keep only last 1000 decisions
        if len(self._usage_history) > 1000:
            self._usage_history = self._usage_history[-1000:]

    def get_model_for_task(self, task: str, **kwargs) -> str:
        """Convenience method to just get the model name."""
        decision = self.route(task, **kwargs)
        return decision.model

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        if not self._usage_history:
            return {"decisions": 0}

        model_counts = {}
        total_cost = 0

        for decision in self._usage_history:
            model = decision["model"]
            model_counts[model] = model_counts.get(model, 0) + 1
            total_cost += decision.get("estimated_cost", 0)

        return {
            "decisions": len(self._usage_history),
            "model_distribution": model_counts,
            "total_estimated_cost": total_cost,
            "available_models": len([m for m in MODELS if MODELS[m].provider in self.available_providers])
        }

    def list_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available models."""
        models = []

        for name, spec in MODELS.items():
            if provider and spec.provider != provider:
                continue
            if spec.provider not in self.available_providers:
                continue

            models.append({
                "name": name,
                "provider": spec.provider,
                "quality": spec.quality_rating,
                "speed": spec.speed_rating,
                "context_window": spec.context_window,
                "capabilities": spec.capabilities
            })

        return models
