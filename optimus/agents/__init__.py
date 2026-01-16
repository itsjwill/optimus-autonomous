"""
Optimus Agents - Specialized Agent Teams
Code, Web, Strategy, and custom teams.
"""

from .base import BaseAgent, AgentResponse
from .team import Team, TeamFactory
from .code_team import CodeTeam
from .web_team import WebTeam
from .strategy_team import StrategyTeam

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "Team",
    "TeamFactory",
    "CodeTeam",
    "WebTeam",
    "StrategyTeam",
]
