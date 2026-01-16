"""
Strategy Team - Planning and decision-making agents
"""

from typing import Optional, List, Dict, Any
from .base import LLMAgent, AgentResponse
from .team import Team


class StrategyTeam(Team):
    """
    Specialized team for strategic planning and analysis.

    Agents:
    - Strategist: Develops strategies (manager)
    - Analyst: Analyzes data and markets
    - Risk: Assesses risks
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", verbose: bool = True):
        agents = [
            LLMAgent(
                name="Strategist",
                role="Chief Strategist",
                goal="Develop winning strategies based on data and analysis",
                backstory="""You are a seasoned strategist with a track record of success.
You see the big picture and identify opportunities others miss.
You make data-driven decisions while considering qualitative factors.
You create actionable plans with clear milestones.""",
                model=model,
                verbose=verbose
            ),
            LLMAgent(
                name="Analyst",
                role="Market Analyst",
                goal="Provide deep market insights and data analysis",
                backstory="""You are an expert analyst with deep domain knowledge.
You analyze trends, patterns, and anomalies in data.
You provide insights that inform strategic decisions.
You quantify opportunities and challenges.""",
                model=model,
                verbose=verbose
            ),
            LLMAgent(
                name="Risk",
                role="Risk Manager",
                goal="Identify, assess, and mitigate risks",
                backstory="""You are a cautious professional focused on risk management.
You identify potential risks before they become problems.
You quantify risk exposure and recommend mitigations.
You balance opportunity with prudent risk management.""",
                model=model,
                verbose=verbose
            ),
        ]

        super().__init__(name="strategy", agents=agents, process="hierarchical")

    async def develop_strategy(
        self,
        objective: str,
        constraints: Optional[List[str]] = None,
        timeline: Optional[str] = None
    ) -> str:
        """
        Develop a strategy for an objective.

        Args:
            objective: What to achieve
            constraints: Limitations to consider
            timeline: Time horizon

        Returns:
            Complete strategy
        """
        task = f"""Develop a strategy for:

Objective: {objective}
{f'Timeline: {timeline}' if timeline else ''}
{f'Constraints: {chr(10).join("- " + c for c in constraints)}' if constraints else ''}

Provide:
1. Strategic analysis
2. Recommended approach
3. Key milestones
4. Risk assessment
5. Success metrics
"""
        return await self.execute(task)

    async def analyze_decision(
        self,
        decision: str,
        options: List[str],
        criteria: Optional[List[str]] = None
    ) -> str:
        """
        Analyze a decision with multiple options.

        Args:
            decision: Decision to make
            options: Available options
            criteria: Evaluation criteria

        Returns:
            Decision analysis with recommendation
        """
        criteria = criteria or ["cost", "benefit", "risk", "feasibility", "timeline"]

        task = f"""Analyze this decision:

Decision: {decision}

Options:
{chr(10).join(f'{i+1}. {o}' for i, o in enumerate(options))}

Evaluate each option against:
{chr(10).join(f'- {c}' for c in criteria)}

Provide:
1. Analysis of each option
2. Comparison matrix
3. Recommended option with rationale
4. Implementation considerations
"""
        return await self.execute(task)

    async def assess_risk(self, scenario: str, context: Optional[str] = None) -> str:
        """
        Assess risks for a scenario.

        Args:
            scenario: Scenario to assess
            context: Additional context

        Returns:
            Risk assessment
        """
        risk_agent = self.agents[-1]

        prompt = f"""Assess risks for this scenario:

Scenario: {scenario}
{f'Context: {context}' if context else ''}

Provide:
1. Identified risks (categorized)
2. Likelihood and impact for each
3. Risk matrix
4. Mitigation strategies
5. Monitoring recommendations
"""
        response = await risk_agent.execute(prompt)
        return response.output if response.success else f"Risk assessment failed: {response.output}"


class DecisionAgent(LLMAgent):
    """
    Single-agent for quick decisions.
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", verbose: bool = True):
        super().__init__(
            name="Decider",
            role="Decision Maker",
            goal="Make clear, well-reasoned decisions",
            backstory="""You are a decisive professional.
You weigh options quickly and make clear recommendations.
You explain your reasoning concisely.
You consider both data and intuition.""",
            model=model,
            verbose=verbose
        )

    async def decide(self, question: str, options: Optional[List[str]] = None) -> AgentResponse:
        """
        Make a quick decision.

        Args:
            question: Decision question
            options: Optional list of options

        Returns:
            Decision with reasoning
        """
        prompt = f"""Make a decision:

Question: {question}
{f'Options: {", ".join(options)}' if options else ''}

Provide:
1. Your decision
2. Key reasoning (3 points max)
3. Confidence level
"""
        return await self.execute(prompt)

    async def prioritize(self, items: List[str], criteria: str = "importance") -> AgentResponse:
        """
        Prioritize a list of items.

        Args:
            items: Items to prioritize
            criteria: Prioritization criteria

        Returns:
            Prioritized list with reasoning
        """
        prompt = f"""Prioritize these items by {criteria}:

Items:
{chr(10).join(f'- {item}' for item in items)}

Provide:
1. Prioritized list (most important first)
2. Brief rationale for top 3
"""
        return await self.execute(prompt)
