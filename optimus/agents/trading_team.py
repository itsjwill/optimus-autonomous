"""
Trading Team - Autonomous Trading Intelligence Agents

Specialized team for:
- Analyzing trading bot performance
- Pattern recognition in trade data
- Risk assessment and optimization
- Autonomous parameter tuning decisions
"""

from typing import Optional, List, Dict, Any
from .base import LLMAgent, AgentResponse
from .team import Team


class TradingTeam(Team):
    """
    Specialized team for autonomous trading intelligence.

    Agents:
    - Analyst: Analyzes trade data and patterns
    - Optimizer: Recommends parameter optimizations
    - Risk Manager: Assesses and mitigates trading risks
    - Executor: Decides which changes to apply

    Works with brain.db data and makes autonomous decisions.
    """

    # Model configurations for different agent types
    # - Analyst: Needs strong reasoning for data analysis -> Claude Sonnet 4
    # - Optimizer: Needs creativity for recommendations -> Claude Sonnet 4
    # - RiskGuard: Quick risk checks -> Claude 3 Haiku (fast, cheap)
    # - Executor: Critical decisions -> Claude Sonnet 4.5 (most capable)
    DEFAULT_MODELS = {
        "TradeAnalyst": "anthropic/claude-sonnet-4",
        "Optimizer": "anthropic/claude-sonnet-4",
        "RiskGuard": "anthropic/claude-3-haiku",  # Fast for risk checks
        "Executor": "anthropic/claude-sonnet-4",  # Most capable for decisions
    }

    def __init__(
        self,
        model: str = "claude-sonnet-4",
        models: dict = None,
        verbose: bool = True,
        use_multi_model: bool = True
    ):
        """
        Initialize TradingTeam with optional multi-model support.

        Args:
            model: Default model for all agents (used if use_multi_model=False)
            models: Override specific agent models (e.g., {"Executor": "gpt-4o"})
            verbose: Enable verbose logging
            use_multi_model: Use optimized models per agent type (default: True)
        """
        # Determine which model each agent uses
        agent_models = {}
        if use_multi_model:
            agent_models = self.DEFAULT_MODELS.copy()
        else:
            agent_models = {name: model for name in self.DEFAULT_MODELS}

        # Apply custom overrides if provided
        if models:
            agent_models.update(models)

        agents = [
            LLMAgent(
                name="TradeAnalyst",
                role="Trading Data Analyst",
                goal="Analyze trading performance and identify winning/losing patterns",
                backstory="""You are an expert quantitative analyst specializing in crypto trading.
You analyze trade data to find patterns: which conditions lead to wins vs losses.
You look at RSI levels, Z-scores, time of day, market regimes, and position sizing.
You quantify everything with statistics: win rate, profit factor, Sharpe ratio, max drawdown.
You separate signal from noise and identify statistically significant patterns.""",
                model=agent_models["TradeAnalyst"],
                verbose=verbose
            ),
            LLMAgent(
                name="Optimizer",
                role="Strategy Optimizer",
                goal="Recommend parameter changes to improve trading performance",
                backstory="""You are a trading strategy optimizer with deep expertise in algo trading.
You take analysis from the TradeAnalyst and translate it into actionable parameter changes.
You understand the specific bots: Billy (RSI mean reversion), Blood (liquidation cascades),
Reaper (aggressive 15x), and PHANTOM (confluence signals).
You recommend specific changes: RSI thresholds, Z-score levels, position sizing, scale levels.
You provide confidence scores and projected impact for each recommendation.""",
                model=agent_models["Optimizer"],
                verbose=verbose
            ),
            LLMAgent(
                name="RiskGuard",
                role="Trading Risk Manager",
                goal="Protect capital and prevent catastrophic losses",
                backstory="""You are a veteran risk manager who has seen every market condition.
You evaluate proposed changes for potential risks: over-leverage, correlated positions,
regime changes, black swan scenarios. You set hard limits: never exceed 5x on main wallet,
15x on reaper wallet. You recommend position sizing based on Kelly criterion.
You veto changes that could lead to ruin, even if they have positive expected value.
Capital preservation comes first.""",
                model=agent_models["RiskGuard"],
                verbose=verbose
            ),
            LLMAgent(
                name="Executor",
                role="Decision Executor",
                goal="Make final decisions on which changes to apply",
                backstory="""You are the final decision maker in the trading intelligence system.
You receive recommendations from the Optimizer, filtered by the RiskGuard.
You decide: APPLY (execute the change), DEFER (wait for more data), or REJECT (too risky).
You only apply changes with >70% confidence and positive risk-adjusted expected value.
You track the impact of previous decisions and learn from outcomes.
You never make more than 3 changes per day to avoid over-optimization.""",
                model=agent_models["Executor"],
                verbose=verbose
            ),
        ]

        super().__init__(name="trading", agents=agents, process="sequential")

    async def analyze_performance(self, trade_data: str, timeframe: str = "24h") -> str:
        """
        Analyze trading performance from brain.db data.

        Args:
            trade_data: JSON or formatted trade data from brain.db
            timeframe: Time period to analyze

        Returns:
            Complete performance analysis
        """
        task = f"""Analyze the following trading data from the last {timeframe}:

{trade_data}

Provide:
1. Overall P&L summary (by bot, by symbol, by direction)
2. Win rate analysis
3. Average trade metrics (hold time, peak ROE, actual exit)
4. Pattern identification (what's working, what's not)
5. Time-of-day analysis (if enough data)
6. Regime correlation (if available)
7. Specific recommendations for each bot
"""
        return await self.execute(task)

    async def generate_optimization(
        self,
        analysis: str,
        current_params: Dict[str, Any],
        constraints: Optional[List[str]] = None
    ) -> str:
        """
        Generate parameter optimization recommendations.

        Args:
            analysis: Output from analyze_performance
            current_params: Current bot parameters
            constraints: Hard limits to respect

        Returns:
            Specific parameter change recommendations
        """
        constraints = constraints or [
            "Max leverage: 5x (main wallet), 15x (reaper wallet)",
            "RSI range: 20-40 for buy, 60-80 for sell",
            "Z-score range: 2.0-5.0",
            "Scale levels: 1.5%-5% per level",
            "Max 3 changes per day",
            "Minimum 20 trades before changing a parameter"
        ]

        task = f"""Based on this performance analysis:

{analysis}

Current parameters:
{current_params}

Constraints:
{chr(10).join(f'- {c}' for c in constraints)}

Recommend specific parameter changes:
1. What parameter to change
2. Current value
3. Recommended new value
4. Confidence level (0-100%)
5. Projected impact (% improvement)
6. Risk assessment
7. Implementation priority

Only recommend changes with statistical significance (p < 0.05 or 20+ trades supporting the change).
"""
        return await self.execute(task)

    async def assess_risk(
        self,
        proposed_changes: str,
        current_positions: str,
        market_conditions: str
    ) -> str:
        """
        Assess risk of proposed changes.

        Args:
            proposed_changes: Optimizer's recommendations
            current_positions: Current open positions
            market_conditions: Current market state

        Returns:
            Risk assessment with approval/rejection
        """
        risk_agent = self.agents[2]  # RiskGuard

        task = f"""Assess the risk of these proposed changes:

Proposed Changes:
{proposed_changes}

Current Positions:
{current_positions}

Market Conditions:
{market_conditions}

Evaluate:
1. Position size risk (over-concentration?)
2. Leverage risk (can we survive a 10% adverse move?)
3. Correlation risk (are we doubling down on same direction?)
4. Regime risk (are these changes appropriate for current market?)
5. Tail risk (what's the worst case scenario?)

For each proposed change, provide:
- APPROVE: Safe to apply
- MODIFY: Safe with adjustments (specify what)
- REJECT: Too risky (explain why)
"""
        response = await risk_agent.execute(task)
        return response.output if response.success else f"Risk assessment failed: {response.output}"

    async def make_decision(
        self,
        analysis: str,
        optimizations: str,
        risk_assessment: str,
        previous_decisions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make final decision on what changes to apply.

        Args:
            analysis: Performance analysis
            optimizations: Optimizer recommendations
            risk_assessment: Risk evaluation
            previous_decisions: History of previous decisions

        Returns:
            Decision dict with actions to take
        """
        executor = self.agents[3]  # Executor

        task = f"""Make the final decision on parameter changes.

Performance Analysis:
{analysis}

Optimization Recommendations:
{optimizations}

Risk Assessment:
{risk_assessment}

{f'Previous Decisions:{chr(10)}{previous_decisions}' if previous_decisions else ''}

For each recommendation, decide:
1. APPLY - Execute immediately
2. DEFER - Wait for more data (specify how much)
3. REJECT - Do not apply (explain why)

Output your decision in this exact format:
DECISION: [APPLY|DEFER|REJECT]
PARAMETER: [parameter name]
BOT: [billy|blood|reaper|phantom]
OLD_VALUE: [current value]
NEW_VALUE: [new value]
CONFIDENCE: [0-100]
REASON: [one line explanation]

Provide one DECISION block per recommendation.
"""
        response = await executor.execute(task)

        if not response.success:
            return {"success": False, "error": response.output}

        # Parse the decisions
        decisions = []
        current_decision = {}

        for line in response.output.split("\n"):
            line = line.strip()
            if line.startswith("DECISION:"):
                if current_decision:
                    decisions.append(current_decision)
                current_decision = {"action": line.split(":", 1)[1].strip()}
            elif line.startswith("PARAMETER:"):
                current_decision["parameter"] = line.split(":", 1)[1].strip()
            elif line.startswith("BOT:"):
                current_decision["bot"] = line.split(":", 1)[1].strip()
            elif line.startswith("OLD_VALUE:"):
                current_decision["old_value"] = line.split(":", 1)[1].strip()
            elif line.startswith("NEW_VALUE:"):
                current_decision["new_value"] = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    current_decision["confidence"] = int(line.split(":", 1)[1].strip())
                except:
                    current_decision["confidence"] = 50
            elif line.startswith("REASON:"):
                current_decision["reason"] = line.split(":", 1)[1].strip()

        if current_decision:
            decisions.append(current_decision)

        return {
            "success": True,
            "decisions": decisions,
            "raw_output": response.output
        }

    async def run_autonomous_cycle(
        self,
        trade_data: str,
        current_params: Dict[str, Any],
        current_positions: str,
        market_conditions: str,
        previous_decisions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a complete autonomous learning cycle.

        This is the main entry point for the autonomous brain.
        Runs all agents in sequence and returns actionable decisions.

        Args:
            trade_data: Recent trade data from brain.db
            current_params: Current bot parameters
            current_positions: Current open positions
            market_conditions: Current market state
            previous_decisions: History of previous decisions

        Returns:
            Dict with analysis, recommendations, and decisions
        """
        self._log("Starting autonomous learning cycle...")

        # Step 1: Analyze
        self._log("Step 1: Analyzing performance...")
        analysis = await self.analyze_performance(trade_data)

        # Step 2: Optimize
        self._log("Step 2: Generating optimizations...")
        optimizations = await self.generate_optimization(analysis, current_params)

        # Step 3: Risk assessment
        self._log("Step 3: Assessing risks...")
        risk_assessment = await self.assess_risk(
            optimizations, current_positions, market_conditions
        )

        # Step 4: Decision
        self._log("Step 4: Making decisions...")
        decision = await self.make_decision(
            analysis, optimizations, risk_assessment, previous_decisions
        )

        return {
            "analysis": analysis,
            "optimizations": optimizations,
            "risk_assessment": risk_assessment,
            "decision": decision,
            "timestamp": self._get_timestamp()
        }

    def _log(self, message: str) -> None:
        """Log with team prefix."""
        print(f"[TradingTeam] {message}")

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
