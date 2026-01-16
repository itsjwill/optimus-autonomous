"""
Observer - Unified observability for Optimus
Integrates with AgentOps for monitoring and cost tracking.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json

from ..core.config import OptimusConfig


@dataclass
class Event:
    """An observable event."""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: Optional[str] = None


@dataclass
class Session:
    """An observability session."""
    id: str
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    events: List[Event] = field(default_factory=list)
    total_tokens: int = 0
    total_cost: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0


class Observer:
    """
    Observability system for Optimus.

    Provides:
    - Event tracking
    - Cost monitoring
    - Performance metrics
    - Session management
    - AgentOps integration (optional)
    """

    def __init__(self, config: OptimusConfig):
        self.config = config
        self.agentops = None
        self.current_session: Optional[Session] = None
        self.sessions: List[Session] = []
        self.log_file = config.project_dir / "optimus_events.jsonl"

        self._init_agentops()

    def _init_agentops(self) -> None:
        """Initialize AgentOps if available."""
        if not self.config.agentops_enabled:
            return

        if not self.config.agentops_api_key:
            print("[OBSERVER] AgentOps API key not found. Running without AgentOps.")
            return

        try:
            import agentops
            agentops.init(api_key=self.config.agentops_api_key)
            self.agentops = agentops
            print("[OBSERVER] AgentOps initialized.")
        except ImportError:
            print("[OBSERVER] AgentOps not installed. Running without it.")
        except Exception as e:
            print(f"[OBSERVER] AgentOps init failed: {e}")

    def start_session(self, session_id: Optional[str] = None) -> Session:
        """Start a new observability session."""
        session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session = Session(id=session_id)
        self.sessions.append(self.current_session)

        if self.agentops:
            self.agentops.start_session()

        self._log_event(Event(
            type="session_start",
            data={"session_id": session_id},
            session_id=session_id
        ))

        print(f"[OBSERVER] Session started: {session_id}")
        return self.current_session

    def end_session(self) -> Optional[Session]:
        """End the current session."""
        if not self.current_session:
            return None

        self.current_session.ended_at = datetime.now()

        if self.agentops:
            self.agentops.end_session()

        self._log_event(Event(
            type="session_end",
            data={
                "session_id": self.current_session.id,
                "duration_seconds": (self.current_session.ended_at - self.current_session.started_at).total_seconds(),
                "total_tokens": self.current_session.total_tokens,
                "total_cost": self.current_session.total_cost,
                "tasks_completed": self.current_session.tasks_completed,
                "tasks_failed": self.current_session.tasks_failed,
            },
            session_id=self.current_session.id
        ))

        print(f"[OBSERVER] Session ended: {self.current_session.id}")
        print(f"  Tokens: {self.current_session.total_tokens}")
        print(f"  Cost: ${self.current_session.total_cost:.4f}")
        print(f"  Tasks: {self.current_session.tasks_completed} completed, {self.current_session.tasks_failed} failed")

        session = self.current_session
        self.current_session = None
        return session

    def track_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        duration_ms: float,
        agent_name: Optional[str] = None
    ) -> None:
        """Track an LLM API call."""
        event = Event(
            type="llm_call",
            data={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost": cost,
                "duration_ms": duration_ms,
                "agent": agent_name,
            },
            session_id=self.current_session.id if self.current_session else None
        )

        self._log_event(event)

        if self.current_session:
            self.current_session.total_tokens += input_tokens + output_tokens
            self.current_session.total_cost += cost
            self.current_session.events.append(event)

        if self.agentops:
            try:
                self.agentops.record(self.agentops.LLMEvent(
                    model=model,
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens,
                    cost=cost
                ))
            except Exception as e:
                print(f"[OBSERVER] AgentOps record failed: {e}")

    def track_task(
        self,
        task_id: str,
        status: str,
        team: str,
        duration_ms: float,
        result: Optional[str] = None
    ) -> None:
        """Track a task execution."""
        event = Event(
            type="task",
            data={
                "task_id": task_id,
                "status": status,
                "team": team,
                "duration_ms": duration_ms,
                "result_preview": result[:100] if result else None,
            },
            session_id=self.current_session.id if self.current_session else None
        )

        self._log_event(event)

        if self.current_session:
            if status == "completed":
                self.current_session.tasks_completed += 1
            elif status == "failed":
                self.current_session.tasks_failed += 1
            self.current_session.events.append(event)

        if self.agentops:
            try:
                self.agentops.record(self.agentops.ActionEvent(
                    action_type="task",
                    params={"task_id": task_id, "team": team},
                    returns=status
                ))
            except Exception as e:
                print(f"[OBSERVER] AgentOps record failed: {e}")

    def track_error(self, error: str, context: Optional[Dict] = None) -> None:
        """Track an error."""
        event = Event(
            type="error",
            data={
                "error": error,
                "context": context or {},
            },
            session_id=self.current_session.id if self.current_session else None
        )

        self._log_event(event)

        if self.current_session:
            self.current_session.events.append(event)

        if self.agentops:
            try:
                self.agentops.record(self.agentops.ErrorEvent(
                    error_type=type(error).__name__ if isinstance(error, Exception) else "Error",
                    details=str(error)
                ))
            except Exception as e:
                print(f"[OBSERVER] AgentOps record failed: {e}")

    def _log_event(self, event: Event) -> None:
        """Log event to file."""
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps({
                    "type": event.type,
                    "data": event.data,
                    "timestamp": event.timestamp.isoformat(),
                    "session_id": event.session_id,
                }) + "\n")
        except Exception as e:
            print(f"[OBSERVER] Failed to write event log: {e}")

    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        if not self.current_session:
            return {"status": "no active session"}

        duration = (datetime.now() - self.current_session.started_at).total_seconds()

        return {
            "session_id": self.current_session.id,
            "duration_seconds": duration,
            "total_tokens": self.current_session.total_tokens,
            "total_cost": self.current_session.total_cost,
            "tasks_completed": self.current_session.tasks_completed,
            "tasks_failed": self.current_session.tasks_failed,
            "events": len(self.current_session.events),
            "tokens_per_minute": (self.current_session.total_tokens / duration * 60) if duration > 0 else 0,
            "cost_per_hour": (self.current_session.total_cost / duration * 3600) if duration > 0 else 0,
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics across all sessions."""
        total_tokens = sum(s.total_tokens for s in self.sessions)
        total_cost = sum(s.total_cost for s in self.sessions)
        total_tasks = sum(s.tasks_completed + s.tasks_failed for s in self.sessions)
        total_completed = sum(s.tasks_completed for s in self.sessions)

        return {
            "sessions": len(self.sessions),
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "total_tasks": total_tasks,
            "success_rate": (total_completed / total_tasks * 100) if total_tasks > 0 else 0,
            "agentops_enabled": self.agentops is not None,
        }
