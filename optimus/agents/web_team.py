"""
Web Team - Research and web automation agents
"""

from typing import Optional, List, Dict, Any
from .base import LLMAgent, AgentResponse
from .team import Team


class WebTeam(Team):
    """
    Specialized team for web research and automation.

    Agents:
    - Researcher: Finds information
    - Analyzer: Synthesizes findings
    - Reporter: Creates reports
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", verbose: bool = True):
        agents = [
            LLMAgent(
                name="Researcher",
                role="Web Researcher",
                goal="Find accurate, relevant information efficiently",
                backstory="""You are an expert researcher who excels at finding information.
You know how to search effectively and verify sources.
You extract key facts and organize them clearly.
You always cite your sources and note confidence levels.""",
                model=model,
                verbose=verbose
            ),
            LLMAgent(
                name="Analyzer",
                role="Data Analyzer",
                goal="Analyze data and extract insights",
                backstory="""You are a skilled analyst who finds patterns and insights.
You can synthesize information from multiple sources.
You identify trends, anomalies, and key takeaways.
You present findings in a clear, actionable format.""",
                model=model,
                verbose=verbose
            ),
            LLMAgent(
                name="Reporter",
                role="Report Writer",
                goal="Create clear, comprehensive reports",
                backstory="""You are a professional report writer.
You create well-structured, easy-to-read reports.
You highlight key findings and recommendations.
Your reports are concise yet thorough.""",
                model=model,
                verbose=verbose
            ),
        ]

        super().__init__(name="web", agents=agents, process="sequential")

    async def research(self, topic: str, depth: str = "standard") -> str:
        """
        Research a topic.

        Args:
            topic: Topic to research
            depth: Research depth (quick, standard, deep)

        Returns:
            Research findings
        """
        depth_instructions = {
            "quick": "Provide a brief overview with key facts.",
            "standard": "Provide comprehensive coverage of main aspects.",
            "deep": "Provide exhaustive research covering all angles."
        }

        task = f"""Research the following topic:

Topic: {topic}

Depth: {depth_instructions.get(depth, depth_instructions['standard'])}

For each finding:
- State the fact/insight
- Note the likely source type
- Rate confidence (high/medium/low)
"""
        return await self.execute(task)

    async def analyze_competitor(self, company: str, aspects: Optional[List[str]] = None) -> str:
        """
        Analyze a competitor.

        Args:
            company: Company to analyze
            aspects: Specific aspects to cover

        Returns:
            Competitive analysis
        """
        aspects = aspects or ["products", "pricing", "market position", "strengths", "weaknesses"]

        task = f"""Perform competitive analysis on: {company}

Cover these aspects:
{chr(10).join(f'- {a}' for a in aspects)}

Provide:
1. Key findings for each aspect
2. Comparison points
3. Strategic recommendations
"""
        return await self.execute(task)

    async def create_report(self, data: str, report_type: str = "summary") -> str:
        """
        Create a report from data.

        Args:
            data: Raw data/findings to report on
            report_type: Type of report (summary, detailed, executive)

        Returns:
            Formatted report
        """
        reporter = self.agents[-1]

        type_instructions = {
            "summary": "Create a concise 1-page summary.",
            "detailed": "Create a comprehensive detailed report.",
            "executive": "Create an executive summary with key points and recommendations."
        }

        prompt = f"""Create a {report_type} report from this data:

{data}

{type_instructions.get(report_type, type_instructions['summary'])}

Include:
- Executive summary
- Key findings
- Recommendations
- Next steps
"""
        response = await reporter.execute(prompt)
        return response.output if response.success else f"Report generation failed: {response.output}"


class ResearchAgent(LLMAgent):
    """
    Single-agent researcher for quick lookups.
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", verbose: bool = True):
        super().__init__(
            name="Researcher",
            role="Research Specialist",
            goal="Find accurate information quickly",
            backstory="""You are a research specialist.
You find information efficiently and verify accuracy.
You organize findings clearly and cite confidence levels.
You know when you don't have enough information.""",
            model=model,
            verbose=verbose
        )

    async def lookup(self, query: str) -> AgentResponse:
        """
        Quick information lookup.

        Args:
            query: What to look up

        Returns:
            Research findings
        """
        prompt = f"""Research query: {query}

Provide:
1. Direct answer (if possible)
2. Key facts
3. Confidence level
4. What additional research might help
"""
        return await self.execute(prompt)

    async def summarize_topic(self, topic: str, max_points: int = 5) -> AgentResponse:
        """
        Summarize a topic in key points.

        Args:
            topic: Topic to summarize
            max_points: Maximum number of points

        Returns:
            Summary with key points
        """
        prompt = f"""Summarize this topic in {max_points} key points:

Topic: {topic}

For each point:
- Clear, concise statement
- Why it matters
"""
        return await self.execute(prompt)
