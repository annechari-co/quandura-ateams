"""Query patterns for memory retrieval combining PostgreSQL and ChromaDB."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.embeddings import EmbeddingStore
from app.memory.storage import MemoryStorage
from app.models.memory import (
    MemoryLayer,
    MemoryNode,
    MemoryQueryResult,
    MemoryResolution,
    RelationType,
)


@dataclass
class MemoryQueryBuilder:
    """Fluent query builder for memory retrieval."""

    session: AsyncSession
    tenant_id: UUID
    team_id: str | None = None

    # Query parameters
    _pattern: str | None = None
    _text_query: str | None = None
    _symbols: list[str] | None = None
    _layer: MemoryLayer | None = None
    _node_type: str | None = None
    _tags: list[str] = field(default_factory=list)
    _time_range: tuple[datetime, datetime] | None = None
    _min_salience: float | None = None
    _traverse_from: str | None = None
    _relation_types: list[RelationType] | None = None
    _max_depth: int = 1
    _resolution: MemoryResolution = MemoryResolution.SUMMARY
    _limit: int = 10
    _offset: int = 0

    # Internal
    _storage: MemoryStorage | None = None
    _embeddings: EmbeddingStore | None = None

    def __post_init__(self) -> None:
        self._storage = MemoryStorage(self.session, self.tenant_id)
        if self.team_id:
            self._embeddings = EmbeddingStore(self.tenant_id, self.team_id)

    # -------------------------------------------------------------------------
    # Fluent API
    # -------------------------------------------------------------------------

    def pattern(self, pattern: str) -> "MemoryQueryBuilder":
        """Set symbol pattern (glob-style: event.finding.*)."""
        self._pattern = pattern
        return self

    def semantic(self, query: str) -> "MemoryQueryBuilder":
        """Set semantic search query."""
        self._text_query = query
        return self

    def symbols(self, *symbols: str) -> "MemoryQueryBuilder":
        """Set exact symbols to retrieve."""
        self._symbols = list(symbols)
        return self

    def layer(self, layer: MemoryLayer) -> "MemoryQueryBuilder":
        """Filter by layer."""
        self._layer = layer
        return self

    def type(self, node_type: str) -> "MemoryQueryBuilder":
        """Filter by node type."""
        self._node_type = node_type
        return self

    def tag(self, key: str, value: str) -> "MemoryQueryBuilder":
        """Add a tag filter."""
        self._tags.append(f"{key}:{value}")
        return self

    def tags(self, *tags: str) -> "MemoryQueryBuilder":
        """Add multiple tag filters."""
        self._tags.extend(tags)
        return self

    def time_range(self, start: datetime, end: datetime) -> "MemoryQueryBuilder":
        """Filter by time range."""
        self._time_range = (start, end)
        return self

    def min_salience(self, salience: float) -> "MemoryQueryBuilder":
        """Filter by minimum salience."""
        self._min_salience = salience
        return self

    def traverse(
        self,
        from_symbol: str,
        relations: list[RelationType] | None = None,
        depth: int = 2,
    ) -> "MemoryQueryBuilder":
        """Set graph traversal starting point."""
        self._traverse_from = from_symbol
        self._relation_types = relations
        self._max_depth = depth
        return self

    def resolution(self, res: MemoryResolution) -> "MemoryQueryBuilder":
        """Set content resolution level."""
        self._resolution = res
        return self

    def limit(self, n: int) -> "MemoryQueryBuilder":
        """Set result limit."""
        self._limit = n
        return self

    def offset(self, n: int) -> "MemoryQueryBuilder":
        """Set result offset for pagination."""
        self._offset = n
        return self

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------

    async def execute(self) -> MemoryQueryResult:
        """Execute the query and return results."""
        start_time = time.time()
        nodes: list[MemoryNode] = []

        # Route to appropriate query method
        if self._symbols:
            nodes = await self._execute_symbol_lookup()
        elif self._traverse_from:
            nodes = await self._execute_traversal()
        elif self._text_query:
            nodes = await self._execute_semantic_search()
        elif self._pattern:
            nodes = await self._execute_pattern_search()
        elif self._tags:
            nodes = await self._execute_tag_search()
        elif self._layer:
            nodes = await self._execute_layer_search()

        elapsed_ms = int((time.time() - start_time) * 1000)

        return MemoryQueryResult(
            nodes=nodes,
            total_count=len(nodes),
            query_time_ms=elapsed_ms,
            resolution_used=self._resolution,
        )

    async def first(self) -> MemoryNode | None:
        """Execute and return the first result."""
        self._limit = 1
        result = await self.execute()
        return result.nodes[0] if result.nodes else None

    async def all(self) -> list[MemoryNode]:
        """Execute and return all results."""
        result = await self.execute()
        return result.nodes

    async def count(self) -> int:
        """Execute and return count only."""
        result = await self.execute()
        return result.total_count

    # -------------------------------------------------------------------------
    # Query Execution Methods
    # -------------------------------------------------------------------------

    async def _execute_symbol_lookup(self) -> list[MemoryNode]:
        """Look up nodes by exact symbols."""
        return await self._storage.get_many_by_symbols(
            self._symbols, resolution=self._resolution
        )

    async def _execute_traversal(self) -> list[MemoryNode]:
        """Execute graph traversal."""
        return await self._storage.traverse(
            self._traverse_from,
            self._relation_types or list(RelationType),
            max_depth=self._max_depth,
            resolution=self._resolution,
        )

    async def _execute_semantic_search(self) -> list[MemoryNode]:
        """Execute semantic similarity search."""
        if not self._embeddings:
            return []

        # Search ChromaDB for similar embeddings
        results = self._embeddings.find_similar(
            query=self._text_query,
            limit=self._limit,
            layer=self._layer,
            node_type=self._node_type,
        )

        if not results:
            return []

        # Get full nodes from PostgreSQL
        node_ids = [UUID(nid) for nid, _, _ in results]
        nodes = []
        for node_id in node_ids:
            node = await self._storage.get_by_id(node_id)
            if node:
                # Boost salience since node was accessed
                await self._storage.boost_salience(node.symbol)
                nodes.append(node)

        return nodes

    async def _execute_pattern_search(self) -> list[MemoryNode]:
        """Execute symbol pattern search."""
        return await self._storage.find_by_pattern(
            self._pattern,
            team_id=self.team_id,
            limit=self._limit,
            resolution=self._resolution,
        )

    async def _execute_tag_search(self) -> list[MemoryNode]:
        """Execute tag-based search."""
        return await self._storage.find_by_tags(
            self._tags,
            team_id=self.team_id,
            layer=self._layer,
            limit=self._limit,
            resolution=self._resolution,
        )

    async def _execute_layer_search(self) -> list[MemoryNode]:
        """Execute layer-based search."""
        return await self._storage.find_by_layer(
            self._layer,
            team_id=self.team_id,
            node_type=self._node_type,
            limit=self._limit,
            resolution=self._resolution,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


async def find_precedents(
    session: AsyncSession,
    tenant_id: UUID,
    team_id: str,
    finding_description: str,
    limit: int = 5,
) -> list[MemoryNode]:
    """Find similar past findings for precedent matching.

    Used by Inspector Assistant to suggest relevant past cases.
    """
    query = MemoryQueryBuilder(session, tenant_id, team_id)
    result = await (
        query
        .semantic(finding_description)
        .layer(MemoryLayer.EVENT)
        .type("finding")
        .resolution(MemoryResolution.SUMMARY)
        .limit(limit)
        .execute()
    )
    return result.nodes


async def get_facility_context(
    session: AsyncSession,
    tenant_id: UUID,
    team_id: str,
    facility_symbol: str,
) -> dict[str, list[MemoryNode]]:
    """Get full context for a facility: entity, past inspections, open findings.

    Used by Report Generator to assemble facility history.
    """
    query = MemoryQueryBuilder(session, tenant_id, team_id)

    # Get facility entity
    facility = await (
        query.symbols(facility_symbol).resolution(MemoryResolution.FULL).first()
    )

    if not facility:
        return {"facility": [], "inspections": [], "findings": []}

    # Get related inspections
    query2 = MemoryQueryBuilder(session, tenant_id, team_id)
    inspections = await (
        query2
        .tag("facility", facility.node_id)
        .layer(MemoryLayer.EVENT)
        .type("inspection")
        .resolution(MemoryResolution.SUMMARY)
        .limit(20)
        .all()
    )

    # Get open findings
    query3 = MemoryQueryBuilder(session, tenant_id, team_id)
    findings = await (
        query3
        .tag("facility", facility.node_id)
        .tag("status", "open")
        .layer(MemoryLayer.EVENT)
        .type("finding")
        .resolution(MemoryResolution.SUMMARY)
        .limit(50)
        .all()
    )

    return {
        "facility": [facility] if facility else [],
        "inspections": inspections,
        "findings": findings,
    }


async def get_applicable_standards(
    session: AsyncSession,
    tenant_id: UUID,
    team_id: str,
    equipment_type: str,
) -> list[MemoryNode]:
    """Get inspection standards for an equipment type.

    Used by Inspector Assistant to provide criteria during inspection.
    """
    query = MemoryQueryBuilder(session, tenant_id, team_id)
    result = await (
        query
        .tag("equipment_type", equipment_type)
        .layer(MemoryLayer.OPERATIONAL)
        .type("standard")
        .resolution(MemoryResolution.FULL)
        .limit(10)
        .execute()
    )
    return result.nodes
