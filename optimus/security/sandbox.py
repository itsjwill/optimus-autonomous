"""
Sandbox Manager - Secure code execution environment
Integrates with E2B for cloud sandboxing.
"""

import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from ..core.config import OptimusConfig


@dataclass
class ExecutionResult:
    """Result of sandboxed code execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_ms: float = 0
    error: Optional[str] = None


@dataclass
class SandboxSession:
    """A sandbox session."""
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, closed, error


class SandboxManager:
    """
    Secure execution sandbox for Optimus.

    Provides:
    - Isolated code execution via E2B
    - File system isolation
    - Network restrictions
    - Resource limits
    - Session management
    """

    def __init__(self, config: OptimusConfig):
        self.config = config
        self.e2b_client = None
        self.sessions: Dict[str, SandboxSession] = {}
        self._init_e2b()

    def _init_e2b(self) -> None:
        """Initialize E2B client if available."""
        if not self.config.e2b_api_key:
            print("[SANDBOX] E2B API key not found. Using local execution (unsafe).")
            return

        try:
            from e2b import Sandbox
            self.e2b_client = Sandbox
            print("[SANDBOX] E2B initialized.")
        except ImportError:
            print("[SANDBOX] E2B not installed. Using local execution (unsafe).")
        except Exception as e:
            print(f"[SANDBOX] E2B init failed: {e}. Using local execution (unsafe).")

    async def create_session(self, template: str = "base") -> SandboxSession:
        """Create a new sandbox session."""
        session_id = f"sandbox_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if self.e2b_client:
            try:
                # E2B sandbox creation is sync, run in executor
                loop = asyncio.get_event_loop()
                sandbox = await loop.run_in_executor(
                    None,
                    lambda: self.e2b_client(template=template)
                )
                session_id = sandbox.id
            except Exception as e:
                print(f"[SANDBOX] E2B session creation failed: {e}")

        session = SandboxSession(id=session_id)
        self.sessions[session_id] = session
        return session

    async def execute(
        self,
        code: str,
        language: str = "python",
        session_id: Optional[str] = None,
        timeout_ms: int = 30000
    ) -> ExecutionResult:
        """
        Execute code in the sandbox.

        Args:
            code: Code to execute
            language: Programming language (python, javascript, bash)
            session_id: Optional session to use
            timeout_ms: Execution timeout in milliseconds

        Returns:
            ExecutionResult with stdout, stderr, and status
        """
        start_time = datetime.now()

        # Validate code before execution
        validation = self._validate_code(code, language)
        if not validation["safe"]:
            return ExecutionResult(
                success=False,
                error=f"Code validation failed: {validation['reason']}",
                exit_code=-1
            )

        # Execute in E2B if available
        if self.e2b_client and self.config.e2b_api_key:
            return await self._execute_e2b(code, language, timeout_ms)

        # Fallback to local execution (with caution)
        return await self._execute_local(code, language, timeout_ms)

    async def _execute_e2b(self, code: str, language: str, timeout_ms: int) -> ExecutionResult:
        """Execute code in E2B sandbox."""
        try:
            from e2b import Sandbox

            loop = asyncio.get_event_loop()

            def run_in_sandbox():
                sandbox = Sandbox()
                try:
                    if language == "python":
                        result = sandbox.run_code(code)
                    elif language == "javascript":
                        result = sandbox.run_code(code, language="javascript")
                    elif language == "bash":
                        result = sandbox.process.start_and_wait(f"bash -c '{code}'")
                    else:
                        return ExecutionResult(
                            success=False,
                            error=f"Unsupported language: {language}"
                        )

                    return ExecutionResult(
                        success=True,
                        stdout=result.stdout if hasattr(result, 'stdout') else str(result),
                        stderr=result.stderr if hasattr(result, 'stderr') else "",
                        exit_code=result.exit_code if hasattr(result, 'exit_code') else 0
                    )
                finally:
                    sandbox.close()

            result = await asyncio.wait_for(
                loop.run_in_executor(None, run_in_sandbox),
                timeout=timeout_ms / 1000
            )
            return result

        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                error="Execution timed out",
                exit_code=-1
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                exit_code=-1
            )

    async def _execute_local(self, code: str, language: str, timeout_ms: int) -> ExecutionResult:
        """
        Execute code locally (fallback when E2B not available).
        WARNING: This is not sandboxed and should only be used for trusted code.
        """
        import subprocess
        import tempfile
        import os

        print("[SANDBOX] WARNING: Executing locally without sandbox!")

        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_extension(language), delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                cmd = self._get_command(language, temp_file)
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout_ms / 1000
                    )

                    return ExecutionResult(
                        success=process.returncode == 0,
                        stdout=stdout.decode() if stdout else "",
                        stderr=stderr.decode() if stderr else "",
                        exit_code=process.returncode
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    return ExecutionResult(
                        success=False,
                        error="Execution timed out",
                        exit_code=-1
                    )
            finally:
                os.unlink(temp_file)

        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                exit_code=-1
            )

    def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code for dangerous patterns."""
        dangerous_patterns = {
            "python": [
                r"import\s+os",
                r"import\s+subprocess",
                r"import\s+sys",
                r"__import__",
                r"eval\s*\(",
                r"exec\s*\(",
                r"open\s*\([^)]*['\"]w",
                r"os\.system",
                r"subprocess\.",
                r"shutil\.rmtree",
            ],
            "javascript": [
                r"require\s*\(['\"]child_process",
                r"require\s*\(['\"]fs['\"]",
                r"eval\s*\(",
                r"Function\s*\(",
                r"process\.exit",
            ],
            "bash": [
                r"rm\s+-rf\s+/",
                r"dd\s+if=",
                r"mkfs",
                r":\(\)\{",  # Fork bomb
                r"wget.*\|.*sh",
                r"curl.*\|.*sh",
            ]
        }

        patterns = dangerous_patterns.get(language, [])

        import re
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return {
                    "safe": False,
                    "reason": f"Dangerous pattern detected: {pattern[:30]}..."
                }

        return {"safe": True, "reason": ""}

    def _get_extension(self, language: str) -> str:
        """Get file extension for language."""
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "bash": ".sh",
        }
        return extensions.get(language, ".txt")

    def _get_command(self, language: str, file_path: str) -> str:
        """Get execution command for language."""
        commands = {
            "python": f"python3 {file_path}",
            "javascript": f"node {file_path}",
            "bash": f"bash {file_path}",
        }
        return commands.get(language, f"cat {file_path}")

    async def close_session(self, session_id: str) -> None:
        """Close a sandbox session."""
        if session_id in self.sessions:
            self.sessions[session_id].status = "closed"
            del self.sessions[session_id]

    def get_stats(self) -> Dict[str, Any]:
        """Get sandbox statistics."""
        return {
            "e2b_enabled": self.e2b_client is not None,
            "active_sessions": len([s for s in self.sessions.values() if s.status == "active"]),
            "total_sessions": len(self.sessions),
        }
