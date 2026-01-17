"""
Optimus Agents - Specialized Agent Teams
Code, Web, Strategy, Trading, and custom teams.
"""

from .base import BaseAgent, AgentResponse
from .team import Team, TeamFactory
from .code_team import CodeTeam
from .web_team import WebTeam
from .strategy_team import StrategyTeam
from .trading_team import TradingTeam

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "Team",
    "TeamFactory",
    "CodeTeam",
    "WebTeam",
    "StrategyTeam",
    "TradingTeam",
]
