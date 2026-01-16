"""
BrainDB - SQLite-based persistent storage for Optimus
Stores patterns, decisions, tasks, and learnings.
"""

import sqlite3
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: Optional[int] = None
    category: str = ""
    content: str = ""
    metadata: Dict[str, Any] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


class BrainDB:
    """
    SQLite-based brain database for Optimus.

    Tables:
    - memories: General memory storage
    - patterns: Learned patterns from executions
    - decisions: Decision history for audit
    - tasks: Task execution history
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path("brain.db")
        self.conn: Optional[sqlite3.Connection] = None

    async def initialize(self) -> None:
        """Initialize the database and create tables."""
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._init_sync)

    def _init_sync(self) -> None:
        """Synchronous initialization."""
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        """Create database tables."""
        cursor = self.conn.cursor()

        # Memories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT DEFAULT '{}',
                embedding BLOB,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                description TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.0,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Decisions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                decision_type TEXT NOT NULL,
                input_context TEXT NOT NULL,
                output_action TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                outcome TEXT,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            )
        """)

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                team TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                duration_seconds REAL,
                metadata TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        # Iterations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS iterations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                iteration_num INTEGER NOT NULL,
                tasks_completed INTEGER DEFAULT 0,
                tasks_failed INTEGER DEFAULT 0,
                patterns_learned INTEGER DEFAULT 0,
                started_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")

        self.conn.commit()

    async def store_memory(self, category: str, content: str, metadata: Dict = None) -> int:
        """Store a memory entry."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._store_memory_sync, category, content, metadata or {}
        )

    def _store_memory_sync(self, category: str, content: str, metadata: Dict) -> int:
        """Synchronous memory storage."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO memories (category, content, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (category, content, json.dumps(metadata), now, now))

        self.conn.commit()
        return cursor.lastrowid

    async def search_memories(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryEntry]:
        """Search memories by category and/or content."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._search_memories_sync, category, query, limit
        )

    def _search_memories_sync(
        self,
        category: Optional[str],
        query: Optional[str],
        limit: int
    ) -> List[MemoryEntry]:
        """Synchronous memory search."""
        cursor = self.conn.cursor()

        sql = "SELECT * FROM memories WHERE 1=1"
        params = []

        if category:
            sql += " AND category = ?"
            params.append(category)

        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")

        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        return [
            MemoryEntry(
                id=row["id"],
                category=row["category"],
                content=row["content"],
                metadata=json.loads(row["metadata"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            for row in rows
        ]

    async def store_pattern(self, pattern_type: str, description: str, metadata: Dict = None) -> int:
        """Store a learned pattern."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._store_pattern_sync, pattern_type, description, metadata or {}
        )

    def _store_pattern_sync(self, pattern_type: str, description: str, metadata: Dict) -> int:
        """Synchronous pattern storage."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()

        # Check if pattern exists
        cursor.execute("""
            SELECT id, frequency FROM patterns
            WHERE pattern_type = ? AND description = ?
        """, (pattern_type, description))

        row = cursor.fetchone()

        if row:
            # Update frequency
            cursor.execute("""
                UPDATE patterns SET frequency = ?, updated_at = ?
                WHERE id = ?
            """, (row["frequency"] + 1, now, row["id"]))
            self.conn.commit()
            return row["id"]
        else:
            # Insert new pattern
            cursor.execute("""
                INSERT INTO patterns (pattern_type, description, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (pattern_type, description, json.dumps(metadata), now, now))
            self.conn.commit()
            return cursor.lastrowid

    async def store_task(self, task_data: Dict) -> int:
        """Store task execution record."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._store_task_sync, task_data)

    def _store_task_sync(self, task_data: Dict) -> int:
        """Synchronous task storage."""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO tasks
            (task_id, description, team, status, result, duration_seconds, metadata, created_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_data.get("task_id"),
            task_data.get("description"),
            task_data.get("team"),
            task_data.get("status"),
            task_data.get("result"),
            task_data.get("duration_seconds"),
            json.dumps(task_data.get("metadata", {})),
            task_data.get("created_at", datetime.now().isoformat()),
            task_data.get("completed_at")
        ))

        self.conn.commit()
        return cursor.lastrowid

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_stats_sync)

    def _get_stats_sync(self) -> Dict[str, Any]:
        """Synchronous stats retrieval."""
        cursor = self.conn.cursor()

        stats = {}

        # Memory count
        cursor.execute("SELECT COUNT(*) as count FROM memories")
        stats["memories"] = cursor.fetchone()["count"]

        # Pattern count
        cursor.execute("SELECT COUNT(*) as count FROM patterns")
        stats["patterns"] = cursor.fetchone()["count"]

        # Task counts
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM tasks GROUP BY status
        """)
        stats["tasks"] = {row["status"]: row["count"] for row in cursor.fetchall()}

        # Iteration count
        cursor.execute("SELECT COUNT(*) as count FROM iterations")
        stats["iterations"] = cursor.fetchone()["count"]

        return stats

    async def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
