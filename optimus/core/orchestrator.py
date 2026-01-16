"""
Optimus Orchestrator - The Brain
Coordinates agents, manages state, runs the autonomous loop.
"""

import asyncio
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .config import OptimusConfig, TeamConfig


@dataclass
class Task:
    """A task to be executed by agents."""
    id: str
    description: str
    team: str
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Iteration:
    """A single iteration of the autonomous loop."""
    id: int
    tasks_completed: int = 0
    tasks_failed: int = 0
    patterns_learned: int = 0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class Orchestrator:
    """
    The central brain of Optimus Autonomous.

    Manages:
    - Agent teams and their coordination
    - Task queue and execution
    - Memory and learning
    - Security guardrails
    - Observability
    """

    def __init__(self, config: Optional[OptimusConfig] = None):
        self.config = config or OptimusConfig.from_env()
        self.teams: Dict[str, Any] = {}
        self.task_queue: List[Task] = []
        self.iterations: List[Iteration] = []
        self.current_iteration: Optional[Iteration] = None
        self.memory = None
        self.guardrails = None
        self.sandbox = None
        self.observer = None
        self._initialized = False
        self._running = False

        # Callbacks
        self._on_task_complete: List[Callable] = []
        self._on_iteration_complete: List[Callable] = []
        self._on_pattern_learned: List[Callable] = []

    async def initialize(self) -> None:
        """Initialize all components."""
        if self._initialized:
            return

        print(f"[OPTIMUS] Initializing Optimus Autonomous v{self._get_version()}...")

        # Initialize memory
        if self.config.memory_enabled:
            await self._init_memory()

        # Initialize security
        if self.config.guardrails_enabled:
            await self._init_guardrails()

        # Initialize sandbox
        if self.config.sandbox_enabled:
            await self._init_sandbox()

        # Initialize observability
        if self.config.agentops_enabled:
            await self._init_observer()

        self._initialized = True
        print("[OPTIMUS] Initialization complete.")

    async def _init_memory(self) -> None:
        """Initialize memory backend."""
        print("[OPTIMUS] Initializing memory layer...")
        from ..memory import MemoryManager
        self.memory = MemoryManager(self.config)
        await self.memory.initialize()

    async def _init_guardrails(self) -> None:
        """Initialize security guardrails."""
        print("[OPTIMUS] Initializing security guardrails...")
        from ..security import GuardrailsManager
        self.guardrails = GuardrailsManager(self.config)

    async def _init_sandbox(self) -> None:
        """Initialize execution sandbox."""
        print("[OPTIMUS] Initializing execution sandbox...")
        from ..security import SandboxManager
        self.sandbox = SandboxManager(self.config)

    async def _init_observer(self) -> None:
        """Initialize observability."""
        print("[OPTIMUS] Initializing observability...")
        from ..observability import Observer
        self.observer = Observer(self.config)

    def _get_version(self) -> str:
        """Get Optimus version."""
        from .. import __version__
        return __version__

    async def deploy_team(self, team_config: TeamConfig) -> None:
        """Deploy an agent team."""
        print(f"[OPTIMUS] Deploying team: {team_config.name}")

        from ..agents import TeamFactory
        team = await TeamFactory.create_team(team_config, self.config)
        self.teams[team_config.name] = team

        print(f"[OPTIMUS] Team '{team_config.name}' deployed with {len(team_config.agents)} agents.")

    async def add_task(self, description: str, team: str, **metadata) -> Task:
        """Add a task to the queue."""
        task = Task(
            id=f"task_{len(self.task_queue)}_{datetime.now().strftime('%H%M%S')}",
            description=description,
            team=team,
            metadata=metadata
        )
        self.task_queue.append(task)

        if self.memory:
            await self.memory.store("task_added", {
                "task_id": task.id,
                "description": description,
                "team": team
            })

        return task

    async def execute_task(self, task: Task) -> Task:
        """Execute a single task."""
        if task.team not in self.teams:
            task.status = "failed"
            task.result = f"Team '{task.team}' not deployed"
            return task

        task.status = "in_progress"

        # Apply input guardrails
        if self.guardrails:
            safe, reason = await self.guardrails.check_input(task.description)
            if not safe:
                task.status = "failed"
                task.result = f"Blocked by guardrails: {reason}"
                return task

        try:
            team = self.teams[task.team]
            result = await team.execute(task.description)

            # Apply output guardrails
            if self.guardrails:
                safe, reason = await self.guardrails.check_output(result)
                if not safe:
                    task.status = "failed"
                    task.result = f"Output blocked by guardrails: {reason}"
                    return task

            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now()

            # Store in memory
            if self.memory:
                await self.memory.store("task_completed", {
                    "task_id": task.id,
                    "result": result[:500] if result else None  # Truncate for storage
                })

            # Notify callbacks
            for callback in self._on_task_complete:
                await callback(task)

        except Exception as e:
            task.status = "failed"
            task.result = str(e)

        return task

    async def run(
        self,
        max_iterations: Optional[int] = None,
        learning: bool = True
    ) -> None:
        """Run the autonomous loop."""
        if not self._initialized:
            await self.initialize()

        max_iterations = max_iterations or self.config.max_iterations
        self._running = True

        print(f"[OPTIMUS] Starting autonomous loop (max {max_iterations} iterations)...")

        iteration_count = 0
        while self._running and iteration_count < max_iterations:
            iteration_count += 1
            self.current_iteration = Iteration(id=iteration_count)

            print(f"\n[OPTIMUS] === Iteration {iteration_count} ===")

            # Process pending tasks
            pending_tasks = [t for t in self.task_queue if t.status == "pending"]

            if not pending_tasks:
                print("[OPTIMUS] No pending tasks. Waiting...")
                await asyncio.sleep(1)
                continue

            for task in pending_tasks:
                if not self._running:
                    break

                print(f"[OPTIMUS] Executing: {task.description[:50]}...")
                await self.execute_task(task)

                if task.status == "completed":
                    self.current_iteration.tasks_completed += 1
                else:
                    self.current_iteration.tasks_failed += 1

            # Learning phase
            if learning and self.memory:
                patterns = await self._learn_from_iteration()
                self.current_iteration.patterns_learned = len(patterns)

            self.current_iteration.completed_at = datetime.now()
            self.iterations.append(self.current_iteration)

            # Notify callbacks
            for callback in self._on_iteration_complete:
                await callback(self.current_iteration)

            print(f"[OPTIMUS] Iteration {iteration_count} complete: "
                  f"{self.current_iteration.tasks_completed} completed, "
                  f"{self.current_iteration.tasks_failed} failed, "
                  f"{self.current_iteration.patterns_learned} patterns learned")

        self._running = False
        print(f"\n[OPTIMUS] Autonomous loop finished after {iteration_count} iterations.")

    async def _learn_from_iteration(self) -> List[Dict[str, Any]]:
        """Extract patterns from the current iteration."""
        if not self.memory:
            return []

        patterns = []
        completed_tasks = [t for t in self.task_queue
                         if t.status == "completed"
                         and t.completed_at
                         and t.completed_at >= self.current_iteration.started_at]

        for task in completed_tasks:
            # Simple pattern extraction - can be enhanced
            pattern = {
                "task_type": task.team,
                "description_keywords": task.description.split()[:5],
                "success": True,
                "duration": (task.completed_at - task.created_at).total_seconds()
            }
            patterns.append(pattern)

            await self.memory.store("pattern", pattern)

            for callback in self._on_pattern_learned:
                await callback(pattern)

        return patterns

    def stop(self) -> None:
        """Stop the autonomous loop."""
        print("[OPTIMUS] Stopping autonomous loop...")
        self._running = False

    def on_task_complete(self, callback: Callable) -> None:
        """Register a callback for task completion."""
        self._on_task_complete.append(callback)

    def on_iteration_complete(self, callback: Callable) -> None:
        """Register a callback for iteration completion."""
        self._on_iteration_complete.append(callback)

    def on_pattern_learned(self, callback: Callable) -> None:
        """Register a callback for pattern learning."""
        self._on_pattern_learned.append(callback)

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "version": self._get_version(),
            "initialized": self._initialized,
            "running": self._running,
            "teams": list(self.teams.keys()),
            "tasks": {
                "total": len(self.task_queue),
                "pending": len([t for t in self.task_queue if t.status == "pending"]),
                "completed": len([t for t in self.task_queue if t.status == "completed"]),
                "failed": len([t for t in self.task_queue if t.status == "failed"]),
            },
            "iterations": len(self.iterations),
            "memory_enabled": self.memory is not None,
            "guardrails_enabled": self.guardrails is not None,
            "sandbox_enabled": self.sandbox is not None,
        }
