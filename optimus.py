#!/usr/bin/env python3
"""
Optimus Autonomous - Main CLI
by itsJWill (BillyCoder)

The best self-governing intelligence.
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add optimus package to path
sys.path.insert(0, str(Path(__file__).parent))

from banner import print_banner, BOLD_RED, RED, DIM, RESET


def init_project(name: str, path: str = "."):
    """Initialize a new Optimus project."""
    print_banner()
    print(f"{RED}[OPTIMUS]{RESET} Initializing project: {BOLD_RED}{name}{RESET}")

    project_dir = Path(path) / name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create project structure
    (project_dir / "tasks").mkdir(exist_ok=True)
    (project_dir / "outputs").mkdir(exist_ok=True)

    # Create config file
    config_content = f"""# Optimus Autonomous Configuration
# Project: {name}

project_name: {name}
default_model: claude-3-5-sonnet-20241022

# Memory settings
memory_enabled: true
memory_backend: sqlite  # sqlite, mem0

# Security settings
guardrails_enabled: true
sandbox_enabled: false  # Enable if E2B API key is set

# Observability
agentops_enabled: false

# Execution
max_iterations: 100
learning_enabled: true
verbose: true
"""
    (project_dir / "optimus.yaml").write_text(config_content)

    # Create .env template
    env_content = """# Optimus Autonomous Environment Variables

# Required: At least one LLM API key
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Optional: E2B for sandboxed execution
E2B_API_KEY=

# Optional: AgentOps for monitoring
AGENTOPS_API_KEY=
"""
    (project_dir / ".env.example").write_text(env_content)

    print(f"{DIM}  → Created project directory: {project_dir}{RESET}")
    print(f"{DIM}  → Created optimus.yaml config{RESET}")
    print(f"{DIM}  → Created .env.example template{RESET}")
    print()
    print(f"{RED}[OPTIMUS]{RESET} Project initialized!")
    print()
    print(f"{DIM}Next steps:{RESET}")
    print(f"  1. cd {name}")
    print(f"  2. cp .env.example .env")
    print(f"  3. Add your API keys to .env")
    print(f"  4. optimus status")
    print(f"  5. optimus run --task 'Your first task'")


async def deploy_teams(teams: str):
    """Deploy agent teams."""
    from optimus.core import Orchestrator, OptimusConfig
    from optimus.agents import TeamFactory

    print(f"{RED}[OPTIMUS]{RESET} Deploying teams: {BOLD_RED}{teams}{RESET}")

    config = OptimusConfig.from_env()
    orchestrator = Orchestrator(config)

    team_list = teams.split(",")
    default_teams = TeamFactory.create_default_teams()

    for team_name in team_list:
        team_name = team_name.strip()
        if team_name in default_teams:
            print(f"{DIM}  → Deploying {team_name} team...{RESET}")
            await orchestrator.deploy_team(default_teams[team_name])
        else:
            print(f"{DIM}  → Unknown team: {team_name} (available: code, web, strategy){RESET}")

    print(f"{RED}[OPTIMUS]{RESET} Teams deployed and ready.")
    return orchestrator


async def run_task(task: str, team: str = "code", iterations: int = 1, learn: bool = True):
    """Run a single task."""
    from optimus.core import Orchestrator, OptimusConfig
    from optimus.agents import TeamFactory

    print_banner()
    print(f"{RED}[OPTIMUS]{RESET} Running task with {BOLD_RED}{team}{RESET} team")
    print(f"{DIM}Task: {task[:100]}{'...' if len(task) > 100 else ''}{RESET}")
    print()

    config = OptimusConfig.from_env()
    orchestrator = Orchestrator(config)

    # Initialize
    await orchestrator.initialize()

    # Deploy the requested team
    default_teams = TeamFactory.create_default_teams()
    if team in default_teams:
        await orchestrator.deploy_team(default_teams[team])
    else:
        print(f"{RED}[ERROR]{RESET} Unknown team: {team}")
        return

    # Add and execute the task
    task_obj = await orchestrator.add_task(task, team)

    # Run the loop
    await orchestrator.run(max_iterations=iterations, learning=learn)

    # Print results
    print()
    print(f"{RED}[OPTIMUS]{RESET} Task completed!")

    if task_obj.result:
        print(f"\n{BOLD_RED}Result:{RESET}")
        print(task_obj.result)


async def run_loop(iterations: int, learn: bool):
    """Run the autonomous loop."""
    from optimus.core import Orchestrator, OptimusConfig
    from optimus.agents import TeamFactory

    print_banner()
    print(f"{RED}[OPTIMUS]{RESET} Starting autonomous loop")
    print(f"{DIM}  → Iterations: {iterations}{RESET}")
    print(f"{DIM}  → Learning: {'enabled' if learn else 'disabled'}{RESET}")
    print()

    config = OptimusConfig.from_env()
    orchestrator = Orchestrator(config)

    # Initialize
    await orchestrator.initialize()

    # Deploy default teams
    default_teams = TeamFactory.create_default_teams()
    for team_config in default_teams.values():
        await orchestrator.deploy_team(team_config)

    # Run the loop
    await orchestrator.run(max_iterations=iterations, learning=learn)


def status():
    """Show system status."""
    print_banner()

    # Check environment
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_e2b = bool(os.getenv("E2B_API_KEY"))
    has_agentops = bool(os.getenv("AGENTOPS_API_KEY"))

    # Check if in project directory
    has_config = Path("optimus.yaml").exists()
    has_brain = Path("brain.db").exists()

    def status_bar(enabled: bool, label: str) -> str:
        if enabled:
            return f"{BOLD_RED}██████████{RED} {label}"
        return f"{DIM}░░░░░░░░░░{RED} {label}"

    print(f"""
{RED}┌─────────────────────────────────────────────┐
│  OPTIMUS AUTONOMOUS v0.1.0                  │
├─────────────────────────────────────────────┤
│  {status_bar(has_anthropic or has_openai, 'LLM API        ')} │
│  {status_bar(has_brain, 'Memory (brain.db)')} │
│  {status_bar(has_e2b, 'Sandbox (E2B)   ')} │
│  {status_bar(True, 'Guardrails      ')} │
│  {status_bar(has_agentops, 'AgentOps        ')} │
├─────────────────────────────────────────────┤
│  Project: {'Found' if has_config else 'Not initialized':<24} │
│  Brain DB: {'Found' if has_brain else 'Not created':<23} │
└─────────────────────────────────────────────┘{RESET}
""")

    if not has_anthropic and not has_openai:
        print(f"{DIM}[!] No LLM API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY{RESET}")

    if not has_config:
        print(f"{DIM}[!] Not in an Optimus project. Run 'optimus init <name>' first{RESET}")


async def interactive_mode():
    """Interactive REPL mode."""
    from optimus.core import Orchestrator, OptimusConfig
    from optimus.agents import TeamFactory

    print_banner()
    print(f"{RED}[OPTIMUS]{RESET} Interactive mode")
    print(f"{DIM}Type tasks to execute. Commands: /teams, /status, /quit{RESET}")
    print()

    config = OptimusConfig.from_env()
    orchestrator = Orchestrator(config)
    await orchestrator.initialize()

    # Deploy all teams
    default_teams = TeamFactory.create_default_teams()
    for team_config in default_teams.values():
        await orchestrator.deploy_team(team_config)

    current_team = "code"

    while True:
        try:
            user_input = input(f"{RED}[{current_team}]>{RESET} ").strip()

            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd = user_input[1:].lower()

                if cmd == "quit" or cmd == "exit":
                    print(f"{DIM}Goodbye!{RESET}")
                    break
                elif cmd == "status":
                    print(orchestrator.get_status())
                elif cmd == "teams":
                    print(f"Available teams: {', '.join(orchestrator.teams.keys())}")
                elif cmd.startswith("use "):
                    team = cmd[4:].strip()
                    if team in orchestrator.teams:
                        current_team = team
                        print(f"{DIM}Switched to {team} team{RESET}")
                    else:
                        print(f"{DIM}Unknown team: {team}{RESET}")
                else:
                    print(f"{DIM}Unknown command: {cmd}{RESET}")
            else:
                # Execute as task
                task = await orchestrator.add_task(user_input, current_team)
                result = await orchestrator.execute_task(task)

                if result.status == "completed":
                    print(f"\n{result.result}\n")
                else:
                    print(f"\n{RED}[FAILED]{RESET} {result.result}\n")

        except KeyboardInterrupt:
            print(f"\n{DIM}Use /quit to exit{RESET}")
        except EOFError:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Optimus Autonomous - The best self-governing intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", help="Project name")
    init_parser.add_argument("--path", default=".", help="Parent directory")

    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy agent teams")
    deploy_parser.add_argument("--teams", required=True, help="Comma-separated team names (code,web,strategy)")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run tasks or autonomous loop")
    run_parser.add_argument("--task", help="Single task to run")
    run_parser.add_argument("--team", default="code", help="Team to use (default: code)")
    run_parser.add_argument("--iterations", type=int, default=10, help="Max iterations")
    run_parser.add_argument("--learn", action="store_true", help="Enable learning mode")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Interactive command
    subparsers.add_parser("interactive", help="Interactive REPL mode")
    subparsers.add_parser("i", help="Interactive REPL mode (shorthand)")

    # Banner command
    subparsers.add_parser("banner", help="Show the banner")

    args = parser.parse_args()

    if args.command == "init":
        init_project(args.name, args.path)
    elif args.command == "deploy":
        asyncio.run(deploy_teams(args.teams))
    elif args.command == "run":
        if args.task:
            asyncio.run(run_task(args.task, args.team, args.iterations, args.learn))
        else:
            asyncio.run(run_loop(args.iterations, args.learn))
    elif args.command == "status":
        status()
    elif args.command in ("interactive", "i"):
        asyncio.run(interactive_mode())
    elif args.command == "banner":
        print_banner()
    else:
        print_banner()
        parser.print_help()


if __name__ == "__main__":
    main()
