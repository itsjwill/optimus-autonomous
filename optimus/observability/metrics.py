"""
Metrics Collector - Performance and usage metrics
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json


@dataclass
class Metric:
    """A single metric measurement."""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collects and aggregates metrics for Optimus.

    Tracks:
    - Token usage by model/agent
    - Cost by model/agent
    - Task duration by team
    - Success/failure rates
    - Memory usage
    """

    def __init__(self):
        self.metrics: List[Metric] = []
        self._aggregates: Dict[str, List[float]] = defaultdict(list)

    def record(
        self,
        name: str,
        value: float,
        unit: str = "",
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric."""
        metric = Metric(
            name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        self.metrics.append(metric)
        self._aggregates[name].append(value)

    def record_tokens(self, tokens: int, model: str, agent: str = "unknown") -> None:
        """Record token usage."""
        self.record("tokens", tokens, "tokens", {"model": model, "agent": agent})

    def record_cost(self, cost: float, model: str, agent: str = "unknown") -> None:
        """Record cost."""
        self.record("cost", cost, "USD", {"model": model, "agent": agent})

    def record_duration(self, duration_ms: float, operation: str, team: str = "unknown") -> None:
        """Record operation duration."""
        self.record("duration", duration_ms, "ms", {"operation": operation, "team": team})

    def record_task_result(self, success: bool, team: str) -> None:
        """Record task result."""
        self.record("task_success", 1 if success else 0, "", {"team": team})

    def get_summary(self, since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get metrics summary."""
        metrics = self.metrics
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]

        if not metrics:
            return {"status": "no metrics"}

        # Aggregate by name
        by_name: Dict[str, List[float]] = defaultdict(list)
        for m in metrics:
            by_name[m.name].append(m.value)

        summary = {}
        for name, values in by_name.items():
            summary[name] = {
                "count": len(values),
                "sum": sum(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

        return summary

    def get_cost_breakdown(self) -> Dict[str, float]:
        """Get cost breakdown by model."""
        costs: Dict[str, float] = defaultdict(float)

        for m in self.metrics:
            if m.name == "cost":
                model = m.tags.get("model", "unknown")
                costs[model] += m.value

        return dict(costs)

    def get_token_breakdown(self) -> Dict[str, int]:
        """Get token usage breakdown by model."""
        tokens: Dict[str, int] = defaultdict(int)

        for m in self.metrics:
            if m.name == "tokens":
                model = m.tags.get("model", "unknown")
                tokens[model] += int(m.value)

        return dict(tokens)

    def get_team_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics by team."""
        teams: Dict[str, Dict[str, List]] = defaultdict(lambda: {"durations": [], "successes": []})

        for m in self.metrics:
            team = m.tags.get("team")
            if not team:
                continue

            if m.name == "duration":
                teams[team]["durations"].append(m.value)
            elif m.name == "task_success":
                teams[team]["successes"].append(m.value)

        result = {}
        for team, data in teams.items():
            durations = data["durations"]
            successes = data["successes"]

            result[team] = {
                "tasks": len(successes),
                "success_rate": (sum(successes) / len(successes) * 100) if successes else 0,
                "avg_duration_ms": (sum(durations) / len(durations)) if durations else 0,
                "total_duration_ms": sum(durations),
            }

        return result

    def get_recent(self, minutes: int = 60) -> List[Metric]:
        """Get recent metrics."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [m for m in self.metrics if m.timestamp >= cutoff]

    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()
        self._aggregates.clear()

    def export_json(self) -> str:
        """Export metrics as JSON."""
        return json.dumps([
            {
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "timestamp": m.timestamp.isoformat(),
                "tags": m.tags,
            }
            for m in self.metrics
        ], indent=2)
