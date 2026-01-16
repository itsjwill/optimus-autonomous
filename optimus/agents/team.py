"""
Team - Agent team coordination
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ..core.config import OptimusConfig, TeamConfig, AgentConfig
from .base import BaseAgent, LLMAgent, AgentResponse


class Team:
    """
    A team of agents that work together.

    Supports:
    - Sequential execution (agents run one after another)
    - Parallel execution (agents run simultaneously)
    - Hierarchical execution (manager delegates to workers)
    """

    def __init__(
        self,
        name: str,
        agents: List[BaseAgent],
        process: str = "sequential"
    ):
        self.name = name
        self.agents = agents
        self.process = process
        self.memory = None

    def set_memory(self, memory) -> None:
        """Set memory for all agents in the team."""
        self.memory = memory
        for agent in self.agents:
            agent.set_memory(memory)

    async def execute(self, task: str) -> str:
        """
        Execute a task using the team.

        Args:
            task: The task description

        Returns:
            Combined result from the team
        """
        if self.process == "sequential":
            return await self._execute_sequential(task)
        elif self.process == "parallel":
            return await self._execute_parallel(task)
        elif self.process == "hierarchical":
            return await self._execute_hierarchical(task)
        else:
            return await self._execute_sequential(task)

    async def _execute_sequential(self, task: str) -> str:
        """Execute agents sequentially, passing context forward."""
        results = []
        context = ""

        for agent in self.agents:
            # Get context from memory
            if self.memory:
                memory_context = await self.memory.get_context(task)
                context = f"{memory_context}\n\nPrevious results:\n{context}" if context else memory_context

            response = await agent.execute(task, context)

            if response.success:
                results.append(f"[{agent.name}]: {response.output}")
                context = response.output
            else:
                results.append(f"[{agent.name}] FAILED: {response.output}")

        return "\n\n".join(results)

    async def _execute_parallel(self, task: str) -> str:
        """Execute all agents in parallel."""
        import asyncio

        # Get context once
        context = ""
        if self.memory:
            context = await self.memory.get_context(task)

        # Run all agents in parallel
        tasks = [agent.execute(task, context) for agent in self.agents]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for agent, response in zip(self.agents, responses):
            if isinstance(response, Exception):
                results.append(f"[{agent.name}] ERROR: {str(response)}")
            elif response.success:
                results.append(f"[{agent.name}]: {response.output}")
            else:
                results.append(f"[{agent.name}] FAILED: {response.output}")

        return "\n\n".join(results)

    async def _execute_hierarchical(self, task: str) -> str:
        """Execute with a manager agent delegating to workers."""
        if not self.agents:
            return "No agents in team"

        # First agent is the manager
        manager = self.agents[0]
        workers = self.agents[1:]

        # Manager analyzes the task
        manager_prompt = f"""Analyze this task and break it down for your team:
Task: {task}

You have {len(workers)} workers available:
{chr(10).join([f'- {w.name}: {w.role}' for w in workers])}

Provide a plan for how to execute this task."""

        manager_response = await manager.execute(manager_prompt)

        if not manager_response.success:
            return f"Manager failed: {manager_response.output}"

        # Workers execute based on manager's plan
        results = [f"[Manager - {manager.name}]: {manager_response.output}"]

        for worker in workers:
            worker_prompt = f"""Based on the manager's plan, complete your part:

Manager's Plan:
{manager_response.output}

Original Task: {task}

Complete your assigned work."""

            response = await worker.execute(worker_prompt)
            if response.success:
                results.append(f"[{worker.name}]: {response.output}")
            else:
                results.append(f"[{worker.name}] FAILED: {response.output}")

        return "\n\n".join(results)

    def get_stats(self) -> Dict[str, Any]:
        """Get team statistics."""
        return {
            "name": self.name,
            "process": self.process,
            "agent_count": len(self.agents),
            "agents": [a.get_stats() for a in self.agents],
        }


class TeamFactory:
    """Factory for creating agent teams."""

    @staticmethod
    async def create_team(team_config: TeamConfig, optimus_config: OptimusConfig) -> Team:
        """
        Create a team from configuration.

        Args:
            team_config: Team configuration
            optimus_config: Global Optimus configuration

        Returns:
            Configured Team instance
        """
        agents = []

        for agent_config in team_config.agents:
            agent = LLMAgent(
                name=agent_config.name,
                role=agent_config.role,
                goal=agent_config.goal,
                backstory=agent_config.backstory,
                model=agent_config.llm or optimus_config.default_model,
                verbose=optimus_config.verbose
            )
            agents.append(agent)

        return Team(
            name=team_config.name,
            agents=agents,
            process=team_config.process
        )

    @staticmethod
    def create_default_teams() -> Dict[str, TeamConfig]:
        """Create default team configurations."""
        return {
            "code": TeamConfig(
                name="code",
                process="sequential",
                agents=[
                    AgentConfig(
                        name="Architect",
                        role="Software Architect",
                        goal="Design clean, scalable solutions",
                        backstory="Expert in system design and best practices."
                    ),
                    AgentConfig(
                        name="Developer",
                        role="Senior Developer",
                        goal="Write high-quality, tested code",
                        backstory="Experienced developer who writes clean code."
                    ),
                    AgentConfig(
                        name="Reviewer",
                        role="Code Reviewer",
                        goal="Ensure code quality and catch bugs",
                        backstory="Meticulous reviewer focused on quality."
                    ),
                ]
            ),
            "web": TeamConfig(
                name="web",
                process="parallel",
                agents=[
                    AgentConfig(
                        name="Researcher",
                        role="Web Researcher",
                        goal="Find and extract relevant information",
                        backstory="Expert at finding information online."
                    ),
                    AgentConfig(
                        name="Analyzer",
                        role="Data Analyzer",
                        goal="Analyze and synthesize findings",
                        backstory="Skilled at making sense of complex data."
                    ),
                ]
            ),
            "strategy": TeamConfig(
                name="strategy",
                process="hierarchical",
                agents=[
                    AgentConfig(
                        name="Strategist",
                        role="Chief Strategist",
                        goal="Develop winning strategies",
                        backstory="Experienced strategist with track record of success."
                    ),
                    AgentConfig(
                        name="Analyst",
                        role="Market Analyst",
                        goal="Analyze market conditions and trends",
                        backstory="Data-driven analyst with deep market knowledge."
                    ),
                    AgentConfig(
                        name="Risk",
                        role="Risk Manager",
                        goal="Identify and mitigate risks",
                        backstory="Cautious professional focused on risk management."
                    ),
                ]
            ),
        }
