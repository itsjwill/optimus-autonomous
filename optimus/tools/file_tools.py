"""
File Tools - File system operations for agents
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from .registry import Tool, ToolResult, ToolCategory


class FileTools:
    """
    File system tools for agents.

    Provides safe file operations with:
    - Path validation
    - Size limits
    - Extension filtering
    - Sandbox boundaries
    """

    def __init__(self, base_path: Optional[str] = None, max_file_size: int = 10 * 1024 * 1024):
        """
        Initialize file tools.

        Args:
            base_path: Base directory for file operations (sandbox)
            max_file_size: Maximum file size in bytes (default 10MB)
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.max_file_size = max_file_size
        self._blocked_extensions = {'.exe', '.dll', '.so', '.dylib', '.sh', '.bat', '.cmd', '.ps1'}

    def _validate_path(self, path: str) -> Path:
        """Validate and resolve a path within the sandbox."""
        resolved = (self.base_path / path).resolve()

        # Ensure path is within base_path (prevent directory traversal)
        if not str(resolved).startswith(str(self.base_path.resolve())):
            raise ValueError(f"Path escapes sandbox: {path}")

        return resolved

    async def read_file(self, path: str, encoding: str = "utf-8") -> ToolResult:
        """
        Read a file's contents.

        Args:
            path: Path to the file (relative to base_path)
            encoding: File encoding

        Returns:
            ToolResult with file contents
        """
        start_time = datetime.now()

        try:
            resolved = self._validate_path(path)

            if not resolved.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File not found: {path}"
                )

            if resolved.stat().st_size > self.max_file_size:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File too large: {resolved.stat().st_size} bytes"
                )

            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                lambda: resolved.read_text(encoding=encoding)
            )

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=content,
                duration_ms=duration,
                metadata={"path": str(resolved), "size": len(content)}
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def write_file(self, path: str, content: str, encoding: str = "utf-8") -> ToolResult:
        """
        Write content to a file.

        Args:
            path: Path to the file (relative to base_path)
            content: Content to write
            encoding: File encoding

        Returns:
            ToolResult with success status
        """
        start_time = datetime.now()

        try:
            resolved = self._validate_path(path)

            # Check extension
            if resolved.suffix.lower() in self._blocked_extensions:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Blocked file extension: {resolved.suffix}"
                )

            # Check content size
            if len(content.encode(encoding)) > self.max_file_size:
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Content too large: {len(content)} characters"
                )

            # Create parent directories if needed
            resolved.parent.mkdir(parents=True, exist_ok=True)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: resolved.write_text(content, encoding=encoding)
            )

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=f"Written: {path}",
                duration_ms=duration,
                metadata={"path": str(resolved), "size": len(content)}
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def list_directory(self, path: str = ".", pattern: str = "*") -> ToolResult:
        """
        List directory contents.

        Args:
            path: Directory path (relative to base_path)
            pattern: Glob pattern for filtering

        Returns:
            ToolResult with list of files/directories
        """
        start_time = datetime.now()

        try:
            resolved = self._validate_path(path)

            if not resolved.is_dir():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Not a directory: {path}"
                )

            loop = asyncio.get_event_loop()
            entries = await loop.run_in_executor(
                None,
                lambda: list(resolved.glob(pattern))
            )

            items = []
            for entry in entries[:1000]:  # Limit to 1000 entries
                try:
                    stat = entry.stat()
                    items.append({
                        "name": entry.name,
                        "path": str(entry.relative_to(self.base_path)),
                        "is_dir": entry.is_dir(),
                        "size": stat.st_size if not entry.is_dir() else 0,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except:
                    pass

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=items,
                duration_ms=duration,
                metadata={"count": len(items)}
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def create_directory(self, path: str) -> ToolResult:
        """
        Create a directory.

        Args:
            path: Directory path (relative to base_path)

        Returns:
            ToolResult with success status
        """
        start_time = datetime.now()

        try:
            resolved = self._validate_path(path)

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: resolved.mkdir(parents=True, exist_ok=True)
            )

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=f"Created: {path}",
                duration_ms=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def delete_file(self, path: str) -> ToolResult:
        """
        Delete a file.

        Args:
            path: File path (relative to base_path)

        Returns:
            ToolResult with success status
        """
        start_time = datetime.now()

        try:
            resolved = self._validate_path(path)

            if not resolved.exists():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"File not found: {path}"
                )

            if resolved.is_dir():
                return ToolResult(
                    success=False,
                    output=None,
                    error="Use delete_directory for directories"
                )

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, resolved.unlink)

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=f"Deleted: {path}",
                duration_ms=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def file_exists(self, path: str) -> ToolResult:
        """
        Check if a file exists.

        Args:
            path: File path (relative to base_path)

        Returns:
            ToolResult with existence status
        """
        start_time = datetime.now()

        try:
            resolved = self._validate_path(path)
            exists = resolved.exists()
            is_file = resolved.is_file() if exists else False
            is_dir = resolved.is_dir() if exists else False

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output={
                    "exists": exists,
                    "is_file": is_file,
                    "is_dir": is_dir
                },
                duration_ms=duration
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    async def search_files(self, pattern: str, path: str = ".") -> ToolResult:
        """
        Search for files matching a pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")
            path: Starting directory

        Returns:
            ToolResult with matching files
        """
        start_time = datetime.now()

        try:
            resolved = self._validate_path(path)

            if not resolved.is_dir():
                return ToolResult(
                    success=False,
                    output=None,
                    error=f"Not a directory: {path}"
                )

            loop = asyncio.get_event_loop()
            matches = await loop.run_in_executor(
                None,
                lambda: list(resolved.glob(pattern))
            )

            files = []
            for match in matches[:500]:  # Limit results
                try:
                    files.append({
                        "path": str(match.relative_to(self.base_path)),
                        "name": match.name,
                        "size": match.stat().st_size if match.is_file() else 0
                    })
                except:
                    pass

            duration = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                output=files,
                duration_ms=duration,
                metadata={"count": len(files), "pattern": pattern}
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                output=None,
                error=str(e),
                duration_ms=duration
            )

    def get_tools(self) -> List[Tool]:
        """Get file tools for registration."""
        return [
            Tool(
                name="file_read",
                description="Read the contents of a file",
                func=self.read_file,
                category=ToolCategory.FILE,
                parameters={
                    "path": {"type": "string", "description": "Path to the file", "required": True},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)"}
                }
            ),
            Tool(
                name="file_write",
                description="Write content to a file",
                func=self.write_file,
                category=ToolCategory.FILE,
                parameters={
                    "path": {"type": "string", "description": "Path to the file", "required": True},
                    "content": {"type": "string", "description": "Content to write", "required": True},
                    "encoding": {"type": "string", "description": "File encoding (default: utf-8)"}
                }
            ),
            Tool(
                name="file_list",
                description="List contents of a directory",
                func=self.list_directory,
                category=ToolCategory.FILE,
                parameters={
                    "path": {"type": "string", "description": "Directory path"},
                    "pattern": {"type": "string", "description": "Glob pattern for filtering"}
                }
            ),
            Tool(
                name="file_mkdir",
                description="Create a directory",
                func=self.create_directory,
                category=ToolCategory.FILE,
                parameters={
                    "path": {"type": "string", "description": "Directory path", "required": True}
                }
            ),
            Tool(
                name="file_delete",
                description="Delete a file",
                func=self.delete_file,
                category=ToolCategory.FILE,
                parameters={
                    "path": {"type": "string", "description": "Path to the file", "required": True}
                },
                requires_confirmation=True
            ),
            Tool(
                name="file_exists",
                description="Check if a file or directory exists",
                func=self.file_exists,
                category=ToolCategory.FILE,
                parameters={
                    "path": {"type": "string", "description": "Path to check", "required": True}
                }
            ),
            Tool(
                name="file_search",
                description="Search for files matching a pattern",
                func=self.search_files,
                category=ToolCategory.FILE,
                parameters={
                    "pattern": {"type": "string", "description": "Glob pattern (e.g., **/*.py)", "required": True},
                    "path": {"type": "string", "description": "Starting directory"}
                }
            ),
        ]
