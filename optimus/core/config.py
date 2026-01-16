"""
Optimus Configuration
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    name: str
    role: str
    goal: str
    backstory: str = ""
    tools: List[str] = field(default_factory=list)
    llm: str = "claude-3-5-sonnet-20241022"
    max_iterations: int = 10
    verbose: bool = True


@dataclass
class TeamConfig:
    """Configuration for an agent team."""
    name: str
    agents: List[AgentConfig] = field(default_factory=list)
    process: str = "sequential"  # sequential, hierarchical, parallel


@dataclass
class OptimusConfig:
    """Main configuration for Optimus Autonomous."""

    # Project settings
    project_name: str = "optimus-project"
    project_dir: Path = field(default_factory=lambda: Path.cwd())

    # API Keys (from environment)
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    e2b_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("E2B_API_KEY")
    )

    # Model settings
    default_model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.7
    max_tokens: int = 4096

    # Memory settings
    memory_enabled: bool = True
    memory_backend: str = "mem0"  # mem0, chromadb, sqlite

    # Security settings
    guardrails_enabled: bool = True
    sandbox_enabled: bool = True
    audit_logging: bool = True

    # Observability
    agentops_enabled: bool = False
    agentops_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("AGENTOPS_API_KEY")
    )

    # Teams
    teams: Dict[str, TeamConfig] = field(default_factory=dict)

    # Execution settings
    max_iterations: int = 100
    learning_enabled: bool = True
    verbose: bool = True

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.anthropic_api_key and not self.openai_api_key:
            print("[WARN] No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")

        # Create project directory if needed
        self.project_dir = Path(self.project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_yaml(cls, path: str) -> "OptimusConfig":
        """Load configuration from YAML file."""
        import yaml
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_env(cls) -> "OptimusConfig":
        """Create configuration from environment variables."""
        return cls(
            project_name=os.getenv("OPTIMUS_PROJECT", "optimus-project"),
            default_model=os.getenv("OPTIMUS_MODEL", "claude-3-5-sonnet-20241022"),
            memory_enabled=os.getenv("OPTIMUS_MEMORY", "true").lower() == "true",
            guardrails_enabled=os.getenv("OPTIMUS_GUARDRAILS", "true").lower() == "true",
            sandbox_enabled=os.getenv("OPTIMUS_SANDBOX", "true").lower() == "true",
            verbose=os.getenv("OPTIMUS_VERBOSE", "true").lower() == "true",
        )
