"""
Code Team - Software development agents
"""

from typing import Optional, Dict, Any
from .base import LLMAgent, AgentResponse
from .team import Team


class CodeTeam(Team):
    """
    Specialized team for software development tasks.

    Agents:
    - Architect: Designs solutions
    - Developer: Implements code
    - Tester: Writes and runs tests
    - Reviewer: Reviews code quality
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", verbose: bool = True):
        agents = [
            LLMAgent(
                name="Architect",
                role="Software Architect",
                goal="Design clean, scalable, maintainable solutions",
                backstory="""You are a senior software architect with 15+ years of experience.
You excel at breaking down complex problems into manageable components.
You always consider scalability, maintainability, and best practices.
You provide clear technical designs with rationale for your decisions.""",
                model=model,
                verbose=verbose
            ),
            LLMAgent(
                name="Developer",
                role="Senior Developer",
                goal="Write high-quality, well-tested, production-ready code",
                backstory="""You are an expert developer who writes clean, efficient code.
You follow best practices, write comprehensive tests, and document your work.
You consider edge cases and handle errors gracefully.
Your code is always production-ready.""",
                model=model,
                verbose=verbose
            ),
            LLMAgent(
                name="Reviewer",
                role="Code Reviewer",
                goal="Ensure code quality, catch bugs, and improve solutions",
                backstory="""You are a meticulous code reviewer with an eye for detail.
You catch bugs, security issues, and performance problems.
You provide constructive feedback to improve code quality.
You ensure code follows best practices and project standards.""",
                model=model,
                verbose=verbose
            ),
        ]

        super().__init__(name="code", agents=agents, process="sequential")

    async def develop(self, task: str, requirements: Optional[str] = None) -> str:
        """
        Full development cycle for a task.

        1. Architect designs the solution
        2. Developer implements it
        3. Reviewer checks quality

        Args:
            task: Development task description
            requirements: Optional additional requirements

        Returns:
            Complete development output
        """
        full_task = task
        if requirements:
            full_task = f"{task}\n\nRequirements:\n{requirements}"

        return await self.execute(full_task)

    async def review_code(self, code: str, context: Optional[str] = None) -> AgentResponse:
        """
        Review existing code.

        Args:
            code: Code to review
            context: Optional context about the code

        Returns:
            Review feedback
        """
        reviewer = self.agents[-1]  # Last agent is the reviewer

        prompt = f"""Review this code and provide feedback:

```
{code}
```

{f'Context: {context}' if context else ''}

Provide:
1. Issues found (bugs, security, performance)
2. Suggestions for improvement
3. Overall assessment
"""

        return await reviewer.execute(prompt)


class QuickDeveloper(LLMAgent):
    """
    Single-agent developer for quick tasks.
    Use when you don't need a full team.
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", verbose: bool = True):
        super().__init__(
            name="QuickDev",
            role="Full-Stack Developer",
            goal="Quickly implement features and fix bugs",
            backstory="""You are a versatile full-stack developer.
You can handle any programming task efficiently.
You write clean, working code on the first try.
You include error handling and edge cases.""",
            model=model,
            verbose=verbose
        )

    async def implement(self, task: str, language: str = "python") -> AgentResponse:
        """
        Quickly implement a feature.

        Args:
            task: What to implement
            language: Programming language to use

        Returns:
            Implementation with code
        """
        prompt = f"""Implement the following in {language}:

{task}

Provide:
1. Working code
2. Brief explanation
3. Usage example
"""
        return await self.execute(prompt)

    async def fix_bug(self, code: str, bug_description: str) -> AgentResponse:
        """
        Fix a bug in code.

        Args:
            code: Code with the bug
            bug_description: Description of the bug

        Returns:
            Fixed code with explanation
        """
        prompt = f"""Fix this bug:

Code:
```
{code}
```

Bug: {bug_description}

Provide:
1. Fixed code
2. Explanation of what was wrong
3. How you fixed it
"""
        return await self.execute(prompt)
