"""
Memory Manager - Unified interface for Optimus memory
Combines Mem0 for semantic memory with BrainDB for structured storage.
"""

import json
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..core.config import OptimusConfig
from .brain_db import BrainDB


class MemoryManager:
    """
    Unified memory manager for Optimus.

    Provides:
    - Semantic memory via Mem0 (optional, requires API key)
    - Structured storage via BrainDB (SQLite)
    - Pattern learning and retrieval
    - Cross-session persistence
    """

    def __init__(self, config: OptimusConfig):
        self.config = config
        self.brain_db = BrainDB(config.project_dir / "brain.db")
        self.mem0_client = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize memory systems."""
        if self._initialized:
            return

        # Initialize BrainDB
        await self.brain_db.initialize()
        print("[MEMORY] BrainDB initialized.")

        # Initialize Mem0 if available
        if self.config.memory_backend == "mem0":
            try:
                from mem0 import Memory
                self.mem0_client = Memory()
                print("[MEMORY] Mem0 initialized.")
            except ImportError:
                print("[MEMORY] Mem0 not installed. Using BrainDB only.")
            except Exception as e:
                print(f"[MEMORY] Mem0 initialization failed: {e}. Using BrainDB only.")

        self._initialized = True

    async def store(self, category: str, data: Any, user_id: str = "optimus") -> str:
        """
        Store data in memory.

        Args:
            category: Type of memory (task, pattern, decision, etc.)
            data: Data to store (dict, str, or any JSON-serializable)
            user_id: User/session identifier for Mem0

        Returns:
            Memory ID or confirmation
        """
        # Convert data to string if needed
        if isinstance(data, dict):
            content = json.dumps(data)
            metadata = data
        else:
            content = str(data)
            metadata = {"raw": content}

        # Store in BrainDB
        memory_id = await self.brain_db.store_memory(category, content, metadata)

        # Store in Mem0 for semantic search (if available)
        if self.mem0_client:
            try:
                self.mem0_client.add(content, user_id=user_id, metadata={"category": category})
            except Exception as e:
                print(f"[MEMORY] Mem0 store failed: {e}")

        return f"mem_{memory_id}"

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        user_id: str = "optimus"
    ) -> List[Dict[str, Any]]:
        """
        Search memories.

        Args:
            query: Search query
            category: Filter by category
            limit: Maximum results
            user_id: User/session identifier for Mem0

        Returns:
            List of matching memories
        """
        results = []

        # Search BrainDB
        db_results = await self.brain_db.search_memories(category, query, limit)
        for entry in db_results:
            results.append({
                "source": "brain_db",
                "id": entry.id,
                "category": entry.category,
                "content": entry.content,
                "metadata": entry.metadata,
                "created_at": entry.created_at
            })

        # Search Mem0 (if available)
        if self.mem0_client:
            try:
                mem0_results = self.mem0_client.search(query, user_id=user_id, limit=limit)
                for item in mem0_results:
                    results.append({
                        "source": "mem0",
                        "content": item.get("memory", ""),
                        "metadata": item.get("metadata", {}),
                        "score": item.get("score", 0)
                    })
            except Exception as e:
                print(f"[MEMORY] Mem0 search failed: {e}")

        return results[:limit]

    async def get_patterns(self, pattern_type: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Get learned patterns."""
        # This would query the patterns table
        memories = await self.brain_db.search_memories("pattern", pattern_type, limit)
        return [
            {
                "id": m.id,
                "content": m.content,
                "metadata": m.metadata,
                "created_at": m.created_at
            }
            for m in memories
        ]

    async def store_pattern(self, pattern_type: str, description: str, metadata: Dict = None) -> int:
        """Store a learned pattern."""
        return await self.brain_db.store_pattern(pattern_type, description, metadata)

    async def get_context(self, task_description: str, limit: int = 5) -> str:
        """
        Get relevant context for a task.

        Searches memory for relevant patterns and past experiences.
        """
        results = await self.search(task_description, limit=limit)

        if not results:
            return ""

        context_parts = []
        for r in results:
            context_parts.append(f"- {r['content'][:200]}")

        return "Relevant context from memory:\n" + "\n".join(context_parts)

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        db_stats = await self.brain_db.get_stats()

        stats = {
            "brain_db": db_stats,
            "mem0_enabled": self.mem0_client is not None
        }

        return stats

    async def close(self) -> None:
        """Close memory connections."""
        await self.brain_db.close()
