"""
Knowledge Graph - Entity and relationship storage for agents
Provides graph-based memory for understanding connections.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import sqlite3


@dataclass
class Entity:
    """An entity in the knowledge graph."""
    id: str
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relationship:
    """A relationship between entities."""
    id: str
    source_id: str
    target_id: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GraphQuery:
    """A query result from the graph."""
    entities: List[Entity]
    relationships: List[Relationship]
    paths: List[List[str]] = field(default_factory=list)


class KnowledgeGraph:
    """
    Knowledge graph for storing entities and relationships.

    Provides:
    - Entity storage with types and properties
    - Relationship management
    - Graph queries and traversal
    - Path finding between entities
    - Similarity-based entity search

    Uses SQLite for persistence with graph operations.
    """

    def __init__(self, db_path: str = "knowledge_graph.db"):
        """
        Initialize the knowledge graph.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the database schema."""
        if self._initialized:
            return

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._create_schema)
        self._initialized = True
        print(f"[KNOWLEDGE GRAPH] Initialized: {self.db_path}")

    def _create_schema(self) -> None:
        """Create database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Relationships table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                type TEXT NOT NULL,
                properties TEXT DEFAULT '{}',
                weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES entities(id),
                FOREIGN KEY (target_id) REFERENCES entities(id)
            )
        """)

        # Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rel_type ON relationships(type)")

        conn.commit()
        conn.close()

    async def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Entity:
        """
        Add or update an entity.

        Args:
            entity_id: Unique entity ID
            entity_type: Type of entity (e.g., "person", "concept", "file")
            name: Display name
            properties: Additional properties

        Returns:
            The created/updated Entity
        """
        await self.initialize()

        entity = Entity(
            id=entity_id,
            type=entity_type,
            name=name,
            properties=properties or {}
        )

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._upsert_entity, entity)

        return entity

    def _upsert_entity(self, entity: Entity) -> None:
        """Insert or update an entity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO entities (id, type, name, properties, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                type = excluded.type,
                name = excluded.name,
                properties = excluded.properties,
                updated_at = excluded.updated_at
        """, (
            entity.id,
            entity.type,
            entity.name,
            json.dumps(entity.properties),
            entity.created_at.isoformat(),
            entity.updated_at.isoformat()
        ))

        conn.commit()
        conn.close()

    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_entity, entity_id)

    def _get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Entity(
                id=row[0],
                type=row[1],
                name=row[2],
                properties=json.loads(row[3]) if row[3] else {},
                created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                updated_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now()
            )
        return None

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None,
        weight: float = 1.0
    ) -> Relationship:
        """
        Add a relationship between entities.

        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            relationship_type: Type of relationship (e.g., "knows", "contains", "references")
            properties: Additional properties
            weight: Relationship weight (for ranking)

        Returns:
            The created Relationship
        """
        await self.initialize()

        rel_id = f"{source_id}_{relationship_type}_{target_id}"
        relationship = Relationship(
            id=rel_id,
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            properties=properties or {},
            weight=weight
        )

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._insert_relationship, relationship)

        return relationship

    def _insert_relationship(self, rel: Relationship) -> None:
        """Insert relationship into database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO relationships (id, source_id, target_id, type, properties, weight, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rel.id,
            rel.source_id,
            rel.target_id,
            rel.type,
            json.dumps(rel.properties),
            rel.weight,
            rel.created_at.isoformat()
        ))

        conn.commit()
        conn.close()

    async def get_relationships(
        self,
        entity_id: str,
        direction: str = "both",
        relationship_type: Optional[str] = None
    ) -> List[Relationship]:
        """
        Get relationships for an entity.

        Args:
            entity_id: Entity ID
            direction: "outgoing", "incoming", or "both"
            relationship_type: Filter by relationship type

        Returns:
            List of relationships
        """
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._get_relationships,
            entity_id,
            direction,
            relationship_type
        )

    def _get_relationships(self, entity_id: str, direction: str, rel_type: Optional[str]) -> List[Relationship]:
        """Get relationships from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        relationships = []

        if direction in ("outgoing", "both"):
            query = "SELECT * FROM relationships WHERE source_id = ?"
            params = [entity_id]
            if rel_type:
                query += " AND type = ?"
                params.append(rel_type)

            cursor.execute(query, params)
            for row in cursor.fetchall():
                relationships.append(self._row_to_relationship(row))

        if direction in ("incoming", "both"):
            query = "SELECT * FROM relationships WHERE target_id = ?"
            params = [entity_id]
            if rel_type:
                query += " AND type = ?"
                params.append(rel_type)

            cursor.execute(query, params)
            for row in cursor.fetchall():
                relationships.append(self._row_to_relationship(row))

        conn.close()
        return relationships

    def _row_to_relationship(self, row) -> Relationship:
        """Convert database row to Relationship."""
        return Relationship(
            id=row[0],
            source_id=row[1],
            target_id=row[2],
            type=row[3],
            properties=json.loads(row[4]) if row[4] else {},
            weight=row[5],
            created_at=datetime.fromisoformat(row[6]) if row[6] else datetime.now()
        )

    async def find_entities(
        self,
        entity_type: Optional[str] = None,
        name_contains: Optional[str] = None,
        limit: int = 100
    ) -> List[Entity]:
        """
        Find entities matching criteria.

        Args:
            entity_type: Filter by entity type
            name_contains: Filter by name (case-insensitive contains)
            limit: Maximum results

        Returns:
            List of matching entities
        """
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._find_entities,
            entity_type,
            name_contains,
            limit
        )

    def _find_entities(self, entity_type: Optional[str], name_contains: Optional[str], limit: int) -> List[Entity]:
        """Find entities in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM entities WHERE 1=1"
        params = []

        if entity_type:
            query += " AND type = ?"
            params.append(entity_type)

        if name_contains:
            query += " AND name LIKE ?"
            params.append(f"%{name_contains}%")

        query += f" ORDER BY updated_at DESC LIMIT {limit}"

        cursor.execute(query, params)
        entities = []

        for row in cursor.fetchall():
            entities.append(Entity(
                id=row[0],
                type=row[1],
                name=row[2],
                properties=json.loads(row[3]) if row[3] else {},
                created_at=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
                updated_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now()
            ))

        conn.close()
        return entities

    async def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """
        Find a path between two entities.

        Args:
            source_id: Starting entity ID
            target_id: Target entity ID
            max_depth: Maximum path length

        Returns:
            List of entity IDs forming the path, or None if no path found
        """
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._find_path,
            source_id,
            target_id,
            max_depth
        )

    def _find_path(self, source_id: str, target_id: str, max_depth: int) -> Optional[List[str]]:
        """BFS path finding."""
        if source_id == target_id:
            return [source_id]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        visited = set()
        queue = [(source_id, [source_id])]

        while queue:
            current_id, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            if current_id in visited:
                continue
            visited.add(current_id)

            # Get neighbors
            cursor.execute("""
                SELECT target_id FROM relationships WHERE source_id = ?
                UNION
                SELECT source_id FROM relationships WHERE target_id = ?
            """, (current_id, current_id))

            for row in cursor.fetchall():
                neighbor_id = row[0]
                if neighbor_id == target_id:
                    conn.close()
                    return path + [neighbor_id]

                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))

        conn.close()
        return None

    async def get_neighbors(self, entity_id: str, depth: int = 1) -> GraphQuery:
        """
        Get neighboring entities up to a certain depth.

        Args:
            entity_id: Starting entity ID
            depth: How many hops to explore

        Returns:
            GraphQuery with entities and relationships
        """
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_neighbors, entity_id, depth)

    def _get_neighbors(self, entity_id: str, depth: int) -> GraphQuery:
        """Get neighbors from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        entities = {}
        relationships = []
        to_visit = [entity_id]
        visited = set()

        for _ in range(depth):
            next_visit = []

            for current_id in to_visit:
                if current_id in visited:
                    continue
                visited.add(current_id)

                # Get entity
                cursor.execute("SELECT * FROM entities WHERE id = ?", (current_id,))
                row = cursor.fetchone()
                if row:
                    entities[current_id] = Entity(
                        id=row[0],
                        type=row[1],
                        name=row[2],
                        properties=json.loads(row[3]) if row[3] else {}
                    )

                # Get relationships
                cursor.execute("""
                    SELECT * FROM relationships
                    WHERE source_id = ? OR target_id = ?
                """, (current_id, current_id))

                for rel_row in cursor.fetchall():
                    rel = self._row_to_relationship(rel_row)
                    relationships.append(rel)

                    # Add neighbors to visit
                    next_visit.append(rel.source_id)
                    next_visit.append(rel.target_id)

            to_visit = [n for n in next_visit if n not in visited]

        conn.close()

        return GraphQuery(
            entities=list(entities.values()),
            relationships=relationships
        )

    async def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity and its relationships.

        Args:
            entity_id: Entity ID to delete

        Returns:
            True if deleted
        """
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._delete_entity, entity_id)

    def _delete_entity(self, entity_id: str) -> bool:
        """Delete entity from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete relationships first
        cursor.execute("DELETE FROM relationships WHERE source_id = ? OR target_id = ?", (entity_id, entity_id))

        # Delete entity
        cursor.execute("DELETE FROM entities WHERE id = ?", (entity_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    async def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._get_stats)

    def _get_stats(self) -> Dict[str, Any]:
        """Get stats from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM entities")
        entity_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM relationships")
        rel_count = cursor.fetchone()[0]

        cursor.execute("SELECT type, COUNT(*) FROM entities GROUP BY type")
        entity_types = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT type, COUNT(*) FROM relationships GROUP BY type")
        rel_types = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            "entities": entity_count,
            "relationships": rel_count,
            "entity_types": entity_types,
            "relationship_types": rel_types
        }

    async def export_to_json(self) -> Dict[str, Any]:
        """Export the entire graph to JSON."""
        await self.initialize()

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._export_to_json)

    def _export_to_json(self) -> Dict[str, Any]:
        """Export graph to JSON."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM entities")
        entities = []
        for row in cursor.fetchall():
            entities.append({
                "id": row[0],
                "type": row[1],
                "name": row[2],
                "properties": json.loads(row[3]) if row[3] else {}
            })

        cursor.execute("SELECT * FROM relationships")
        relationships = []
        for row in cursor.fetchall():
            relationships.append({
                "id": row[0],
                "source": row[1],
                "target": row[2],
                "type": row[3],
                "properties": json.loads(row[4]) if row[4] else {},
                "weight": row[5]
            })

        conn.close()

        return {
            "entities": entities,
            "relationships": relationships,
            "exported_at": datetime.now().isoformat()
        }
