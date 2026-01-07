"""PostgreSQL storage for memory nodes."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MemoryNodeModel, MemoryRelationshipModel
from app.models.memory import (
    MemoryLayer,
    MemoryNode,
    MemoryResolution,
    Relationship,
    RelationType,
)


class MemoryStorage:
    """Async PostgreSQL storage for memory nodes."""

    def __init__(self, session: AsyncSession, tenant_id: UUID):
        self.session = session
        self.tenant_id = tenant_id

    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------

    async def create(self, node: MemoryNode) -> MemoryNode:
        """Create a new memory node."""
        db_node = MemoryNodeModel(
            id=node.id,
            tenant_id=self.tenant_id,
            team_id=node.team_id,
            symbol=node.symbol,
            layer=node.layer.value,
            node_type=node.node_type,
            micro=node.micro,
            summary=node.summary,
            full_content={"full": node.full},
            tags=node.tags,
            salience=node.salience,
            confidence=node.confidence,
            created_at=node.timestamp,
            updated_at=node.updated_at,
        )
        self.session.add(db_node)
        await self.session.flush()

        # Create relationships if any
        for rel in node.relationships:
            await self._create_relationship(node.id, rel)

        return node

    async def get_by_symbol(self, symbol: str, team_id: str | None = None) -> MemoryNode | None:
        """Get a memory node by its symbol."""
        stmt = select(MemoryNodeModel).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.symbol == symbol,
            )
        )
        if team_id:
            stmt = stmt.where(MemoryNodeModel.team_id == team_id)

        result = await self.session.execute(stmt)
        db_node = result.scalar_one_or_none()
        return self._to_pydantic(db_node) if db_node else None

    async def get_by_id(self, node_id: UUID) -> MemoryNode | None:
        """Get a memory node by its UUID."""
        stmt = select(MemoryNodeModel).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.id == node_id,
            )
        )
        result = await self.session.execute(stmt)
        db_node = result.scalar_one_or_none()
        return self._to_pydantic(db_node) if db_node else None

    async def update(self, node: MemoryNode) -> MemoryNode:
        """Update an existing memory node."""
        stmt = (
            update(MemoryNodeModel)
            .where(
                and_(
                    MemoryNodeModel.tenant_id == self.tenant_id,
                    MemoryNodeModel.id == node.id,
                )
            )
            .values(
                micro=node.micro,
                summary=node.summary,
                full_content={"full": node.full},
                tags=node.tags,
                salience=node.salience,
                confidence=node.confidence,
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.execute(stmt)
        return node

    async def delete(self, symbol: str) -> bool:
        """Delete a memory node by symbol."""
        # First get the node ID
        node = await self.get_by_symbol(symbol)
        if not node:
            return False

        # Delete relationships
        await self.session.execute(
            delete(MemoryRelationshipModel).where(
                or_(
                    MemoryRelationshipModel.source_id == node.id,
                    MemoryRelationshipModel.target_id == node.id,
                )
            )
        )

        # Delete node
        stmt = delete(MemoryNodeModel).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.symbol == symbol,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0

    # -------------------------------------------------------------------------
    # Bulk Operations
    # -------------------------------------------------------------------------

    async def create_many(self, nodes: list[MemoryNode]) -> list[MemoryNode]:
        """Create multiple memory nodes in a batch."""
        db_nodes = [
            MemoryNodeModel(
                id=node.id,
                tenant_id=self.tenant_id,
                team_id=node.team_id,
                symbol=node.symbol,
                layer=node.layer.value,
                node_type=node.node_type,
                micro=node.micro,
                summary=node.summary,
                full_content={"full": node.full},
                tags=node.tags,
                salience=node.salience,
                confidence=node.confidence,
                created_at=node.timestamp,
                updated_at=node.updated_at,
            )
            for node in nodes
        ]
        self.session.add_all(db_nodes)
        await self.session.flush()

        # Create relationships
        for node in nodes:
            for rel in node.relationships:
                await self._create_relationship(node.id, rel)

        return nodes

    async def get_many_by_symbols(
        self,
        symbols: list[str],
        resolution: MemoryResolution = MemoryResolution.SUMMARY,
    ) -> list[MemoryNode]:
        """Get multiple nodes by symbols."""
        stmt = select(MemoryNodeModel).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.symbol.in_(symbols),
            )
        )
        result = await self.session.execute(stmt)
        db_nodes = result.scalars().all()
        return [self._to_pydantic(n, resolution) for n in db_nodes]

    # -------------------------------------------------------------------------
    # Query Methods
    # -------------------------------------------------------------------------

    async def find_by_tags(
        self,
        tags: list[str],
        team_id: str | None = None,
        layer: MemoryLayer | None = None,
        limit: int = 20,
        resolution: MemoryResolution = MemoryResolution.SUMMARY,
    ) -> list[MemoryNode]:
        """Find nodes matching all specified tags."""
        stmt = select(MemoryNodeModel).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.tags.contains(tags),
            )
        )

        if team_id:
            stmt = stmt.where(MemoryNodeModel.team_id == team_id)
        if layer:
            stmt = stmt.where(MemoryNodeModel.layer == layer.value)

        stmt = stmt.order_by(MemoryNodeModel.salience.desc()).limit(limit)

        result = await self.session.execute(stmt)
        db_nodes = result.scalars().all()
        return [self._to_pydantic(n, resolution) for n in db_nodes]

    async def find_by_layer(
        self,
        layer: MemoryLayer,
        team_id: str | None = None,
        node_type: str | None = None,
        limit: int = 50,
        resolution: MemoryResolution = MemoryResolution.MICRO,
    ) -> list[MemoryNode]:
        """Find all nodes in a layer."""
        stmt = select(MemoryNodeModel).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.layer == layer.value,
            )
        )

        if team_id:
            stmt = stmt.where(MemoryNodeModel.team_id == team_id)
        if node_type:
            stmt = stmt.where(MemoryNodeModel.node_type == node_type)

        stmt = stmt.order_by(MemoryNodeModel.salience.desc()).limit(limit)

        result = await self.session.execute(stmt)
        db_nodes = result.scalars().all()
        return [self._to_pydantic(n, resolution) for n in db_nodes]

    async def find_by_pattern(
        self,
        pattern: str,
        team_id: str | None = None,
        limit: int = 20,
        resolution: MemoryResolution = MemoryResolution.SUMMARY,
    ) -> list[MemoryNode]:
        """Find nodes matching a symbol pattern (glob-style: event.finding.*)."""
        # Convert glob to SQL LIKE pattern
        sql_pattern = pattern.replace("*", "%").replace("?", "_")

        stmt = select(MemoryNodeModel).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.symbol.like(sql_pattern),
            )
        )

        if team_id:
            stmt = stmt.where(MemoryNodeModel.team_id == team_id)

        stmt = stmt.order_by(MemoryNodeModel.salience.desc()).limit(limit)

        result = await self.session.execute(stmt)
        db_nodes = result.scalars().all()
        return [self._to_pydantic(n, resolution) for n in db_nodes]

    async def count_by_layer(self, team_id: str | None = None) -> dict[str, int]:
        """Count nodes per layer."""
        stmt = (
            select(MemoryNodeModel.layer, func.count(MemoryNodeModel.id))
            .where(MemoryNodeModel.tenant_id == self.tenant_id)
            .group_by(MemoryNodeModel.layer)
        )

        if team_id:
            stmt = stmt.where(MemoryNodeModel.team_id == team_id)

        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result.all()}

    # -------------------------------------------------------------------------
    # Relationship Methods
    # -------------------------------------------------------------------------

    async def _create_relationship(self, source_id: UUID, rel: Relationship) -> None:
        """Create a relationship from a source node."""
        # Get target node ID by symbol
        target_stmt = select(MemoryNodeModel.id).where(
            and_(
                MemoryNodeModel.tenant_id == self.tenant_id,
                MemoryNodeModel.symbol == rel.target_symbol,
            )
        )
        target_result = await self.session.execute(target_stmt)
        target_id = target_result.scalar_one_or_none()

        if not target_id:
            return  # Target doesn't exist yet, skip

        db_rel = MemoryRelationshipModel(
            tenant_id=self.tenant_id,
            source_id=source_id,
            target_id=target_id,
            relation_type=rel.relation_type.value,
            weight=rel.weight,
            metadata=rel.metadata,
            created_at=rel.created_at,
        )
        self.session.add(db_rel)

    async def add_relationship(
        self,
        source_symbol: str,
        target_symbol: str,
        relation_type: RelationType,
        weight: float = 1.0,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Add a relationship between two existing nodes."""
        # Get source and target IDs
        source = await self.get_by_symbol(source_symbol)
        target = await self.get_by_symbol(target_symbol)

        if not source or not target:
            return False

        db_rel = MemoryRelationshipModel(
            tenant_id=self.tenant_id,
            source_id=source.id,
            target_id=target.id,
            relation_type=relation_type.value,
            weight=weight,
            metadata=metadata or {},
        )
        self.session.add(db_rel)
        await self.session.flush()
        return True

    async def get_related(
        self,
        symbol: str,
        relation_types: list[RelationType] | None = None,
        direction: str = "outgoing",
        limit: int = 20,
        resolution: MemoryResolution = MemoryResolution.SUMMARY,
    ) -> list[MemoryNode]:
        """Get nodes related to a given symbol."""
        # Get the source node ID
        source = await self.get_by_symbol(symbol)
        if not source:
            return []

        # Build query based on direction
        if direction == "outgoing":
            rel_stmt = select(MemoryRelationshipModel.target_id).where(
                MemoryRelationshipModel.source_id == source.id
            )
        elif direction == "incoming":
            rel_stmt = select(MemoryRelationshipModel.source_id).where(
                MemoryRelationshipModel.target_id == source.id
            )
        else:  # both
            rel_stmt = select(MemoryRelationshipModel.target_id).where(
                MemoryRelationshipModel.source_id == source.id
            ).union(
                select(MemoryRelationshipModel.source_id).where(
                    MemoryRelationshipModel.target_id == source.id
                )
            )

        if relation_types:
            type_values = [rt.value for rt in relation_types]
            rel_stmt = rel_stmt.where(
                MemoryRelationshipModel.relation_type.in_(type_values)
            )

        # Get related node IDs
        rel_result = await self.session.execute(rel_stmt)
        related_ids = [row[0] for row in rel_result.all()]

        if not related_ids:
            return []

        # Get the actual nodes
        node_stmt = (
            select(MemoryNodeModel)
            .where(MemoryNodeModel.id.in_(related_ids))
            .limit(limit)
        )
        node_result = await self.session.execute(node_stmt)
        db_nodes = node_result.scalars().all()

        return [self._to_pydantic(n, resolution) for n in db_nodes]

    async def traverse(
        self,
        start_symbol: str,
        relation_types: list[RelationType],
        max_depth: int = 2,
        resolution: MemoryResolution = MemoryResolution.MICRO,
    ) -> list[MemoryNode]:
        """Traverse the graph from a starting node."""
        visited: set[str] = set()
        result: list[MemoryNode] = []

        async def _traverse(symbol: str, depth: int) -> None:
            if depth > max_depth or symbol in visited:
                return

            visited.add(symbol)
            node = await self.get_by_symbol(symbol)
            if node:
                result.append(node)

                # Get related nodes
                related = await self.get_related(
                    symbol, relation_types, "outgoing", limit=50, resolution=resolution
                )
                for rel_node in related:
                    await _traverse(rel_node.symbol, depth + 1)

        await _traverse(start_symbol, 0)
        return result

    # -------------------------------------------------------------------------
    # Salience Management
    # -------------------------------------------------------------------------

    async def boost_salience(self, symbol: str, boost: float = 0.05) -> None:
        """Boost salience when a node is accessed."""
        stmt = (
            update(MemoryNodeModel)
            .where(
                and_(
                    MemoryNodeModel.tenant_id == self.tenant_id,
                    MemoryNodeModel.symbol == symbol,
                )
            )
            .values(
                salience=func.least(1.0, MemoryNodeModel.salience + boost),
                updated_at=datetime.utcnow(),
            )
        )
        await self.session.execute(stmt)

    async def decay_salience(
        self,
        team_id: str,
        decay_rate: float = 0.01,
        min_salience: float = 0.01,
    ) -> int:
        """Apply time decay to all nodes in a team."""
        stmt = (
            update(MemoryNodeModel)
            .where(
                and_(
                    MemoryNodeModel.tenant_id == self.tenant_id,
                    MemoryNodeModel.team_id == team_id,
                    MemoryNodeModel.salience > min_salience,
                )
            )
            .values(
                salience=func.greatest(min_salience, MemoryNodeModel.salience - decay_rate),
                updated_at=datetime.utcnow(),
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    # -------------------------------------------------------------------------
    # Conversion Helpers
    # -------------------------------------------------------------------------

    def _to_pydantic(
        self,
        db_node: MemoryNodeModel,
        resolution: MemoryResolution = MemoryResolution.FULL,
    ) -> MemoryNode:
        """Convert SQLAlchemy model to Pydantic model."""
        full_content = db_node.full_content.get("full", "") if db_node.full_content else ""

        # For lower resolutions, we might not load full content
        if resolution == MemoryResolution.MICRO:
            full_content = ""
        elif resolution == MemoryResolution.SUMMARY:
            full_content = ""

        return MemoryNode(
            id=db_node.id,
            symbol=db_node.symbol,
            tenant_id=str(db_node.tenant_id),
            team_id=db_node.team_id,
            micro=db_node.micro,
            summary=db_node.summary,
            full=full_content,
            tags=db_node.tags or [],
            salience=db_node.salience,
            confidence=db_node.confidence,
            timestamp=db_node.created_at,
            updated_at=db_node.updated_at,
            relationships=[],  # Loaded separately if needed
        )
