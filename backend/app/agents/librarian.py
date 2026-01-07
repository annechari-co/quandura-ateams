"""Librarian agent for knowledge retrieval from organizational memory."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import Agent, AgentConfig, AgentResult
from app.memory.embeddings import EmbeddingStore
from app.memory.queries import MemoryQueryBuilder
from app.memory.storage import MemoryStorage
from app.models.memory import (
    MemoryLayer,
    MemoryNode,
    MemoryResolution,
    RelationType,
)
from app.models.passport import Passport


class AgentContext(BaseModel):
    """Context assembled for an agent from memory."""

    nodes: list[MemoryNode] = []
    total_tokens_estimate: int = 0
    layers_represented: list[str] = []
    retrieval_summary: str = ""


@dataclass
class LibrarianConfig:
    """Configuration for the Librarian agent."""

    tenant_id: UUID
    team_id: str
    default_resolution: MemoryResolution = MemoryResolution.SUMMARY
    max_context_tokens: int = 4000
    salience_boost_on_retrieve: float = 0.05


class Librarian(Agent):
    """Knowledge retrieval agent that serves context to other agents.

    The Librarian is responsible for:
    - Retrieving relevant context from organizational memory
    - Assembling context packages for specialist agents
    - Finding similar past cases (precedent matching)
    - Traversing the knowledge graph for related information
    """

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: UUID,
        team_id: str,
        config: LibrarianConfig | None = None,
    ):
        agent_config = AgentConfig(
            agent_id=f"librarian_{team_id}",
            agent_type="librarian",
            system_prompt=self._system_prompt(),
            autonomy_level=3,  # Collaborative - medium autonomy for retrieval
        )
        super().__init__(agent_config)

        self.session = session
        self.tenant_id = tenant_id
        self.team_id = team_id
        self.lib_config = config or LibrarianConfig(tenant_id=tenant_id, team_id=team_id)

        self._storage = MemoryStorage(session, tenant_id)
        self._embeddings = EmbeddingStore(tenant_id, team_id)

    def _system_prompt(self) -> str:
        return """You are a Librarian agent responsible for knowledge retrieval.
Your role is to find and assemble relevant context from organizational memory.
You do not generate new content - you retrieve existing knowledge.
When asked to find information, use the available retrieval methods to locate relevant nodes.
Always prioritize high-salience, recent information unless specifically asked otherwise."""

    async def process(self, passport: Passport) -> AgentResult:
        """Process a retrieval request from the passport."""
        # Extract retrieval request from passport context
        retrieval_request = passport.context.get("retrieval_request", {})

        if not retrieval_request:
            return AgentResult(
                success=False,
                output="No retrieval request found in passport context",
                confidence=self.calculate_confidence(0.0),
                error="Missing retrieval_request in context",
            )

        # Route to appropriate retrieval method
        method = retrieval_request.get("method", "query")
        nodes: list[MemoryNode] = []

        if method == "symbols":
            symbols = retrieval_request.get("symbols", [])
            resolution = MemoryResolution(retrieval_request.get("resolution", "summary"))
            nodes = await self.retrieve(symbols, resolution)

        elif method == "query":
            pattern = retrieval_request.get("pattern")
            tags = retrieval_request.get("tags", {})
            layer = retrieval_request.get("layer")
            if layer:
                layer = MemoryLayer(layer)
            resolution = MemoryResolution(retrieval_request.get("resolution", "micro"))
            limit = retrieval_request.get("limit", 20)
            nodes = await self.query(pattern, tags, layer, resolution, limit)

        elif method == "similar":
            text = retrieval_request.get("text", "")
            layer = retrieval_request.get("layer")
            if layer:
                layer = MemoryLayer(layer)
            limit = retrieval_request.get("limit", 10)
            nodes = await self.find_similar(text, layer, limit)

        elif method == "traverse":
            start_symbol = retrieval_request.get("start_symbol", "")
            relation_types = [
                RelationType(rt) for rt in retrieval_request.get("relation_types", [])
            ]
            max_depth = retrieval_request.get("max_depth", 2)
            nodes = await self.traverse(start_symbol, relation_types, max_depth)

        # Store results in passport artifacts
        context_key = retrieval_request.get("context_key", "retrieved_context")
        passport.context[context_key] = [n.model_dump() for n in nodes]

        return AgentResult(
            success=True,
            output=f"Retrieved {len(nodes)} nodes via {method}",
            confidence=self.calculate_confidence(
                base_value=0.9 if nodes else 0.5,
                evidence_count=len(nodes),
                evidence_quality=0.8,
            ),
            artifacts={context_key: f"{len(nodes)} nodes"},
        )

    # -------------------------------------------------------------------------
    # Core Retrieval Methods
    # -------------------------------------------------------------------------

    async def retrieve(
        self,
        symbols: list[str],
        resolution: MemoryResolution = MemoryResolution.SUMMARY,
    ) -> list[MemoryNode]:
        """Retrieve specific nodes by symbol.

        Args:
            symbols: List of node symbols to retrieve
            resolution: Content resolution level

        Returns:
            List of memory nodes
        """
        nodes = await self._storage.get_many_by_symbols(symbols, resolution)

        # Boost salience for accessed nodes
        for node in nodes:
            await self._storage.boost_salience(
                node.symbol, self.lib_config.salience_boost_on_retrieve
            )

        return nodes

    async def query(
        self,
        pattern: str | None = None,
        tags: dict[str, str] | None = None,
        layer: MemoryLayer | None = None,
        resolution: MemoryResolution = MemoryResolution.MICRO,
        limit: int = 20,
    ) -> list[MemoryNode]:
        """Query memory by pattern or tags.

        Args:
            pattern: Symbol pattern (glob-style, e.g., "event.finding.*")
            tags: Tag filters as key-value pairs
            layer: Filter by memory layer
            resolution: Content resolution level
            limit: Max results to return

        Returns:
            List of matching nodes
        """
        builder = MemoryQueryBuilder(self.session, self.tenant_id, self.team_id)

        if pattern:
            builder = builder.pattern(pattern)
        if tags:
            for key, value in tags.items():
                builder = builder.tag(key, value)
        if layer:
            builder = builder.layer(layer)

        builder = builder.resolution(resolution).limit(limit)
        result = await builder.execute()
        return result.nodes

    async def find_similar(
        self,
        text: str,
        layer: MemoryLayer | None = None,
        limit: int = 10,
    ) -> list[MemoryNode]:
        """Find semantically similar nodes.

        Args:
            text: Query text for similarity search
            layer: Filter by memory layer
            limit: Max results to return

        Returns:
            List of similar nodes ordered by similarity
        """
        builder = MemoryQueryBuilder(self.session, self.tenant_id, self.team_id)
        builder = builder.semantic(text).limit(limit)
        if layer:
            builder = builder.layer(layer)

        result = await builder.execute()
        return result.nodes

    async def traverse(
        self,
        start_symbol: str,
        relation_types: list[RelationType],
        max_depth: int = 2,
    ) -> list[MemoryNode]:
        """Traverse the knowledge graph from a starting node.

        Args:
            start_symbol: Symbol of the node to start traversal
            relation_types: Types of relationships to follow
            max_depth: Maximum traversal depth

        Returns:
            List of connected nodes
        """
        return await self._storage.traverse(
            start_symbol,
            relation_types,
            max_depth,
            resolution=MemoryResolution.MICRO,
        )

    # -------------------------------------------------------------------------
    # Context Assembly
    # -------------------------------------------------------------------------

    async def assemble_agent_context(
        self,
        passport: Passport,
        agent_type: str,
        max_tokens: int | None = None,
    ) -> AgentContext:
        """Assemble relevant context for a specialist agent.

        Retrieves context appropriate for the agent type:
        - triage: Strategic goals, operational rules
        - executor: Entity data, relevant precedents
        - judge: Policies, compliance rules
        - inspector: Equipment standards, past findings

        Args:
            passport: Current passport state
            agent_type: Type of agent requesting context
            max_tokens: Max tokens for context (default from config)

        Returns:
            AgentContext with assembled nodes
        """
        max_tokens = max_tokens or self.lib_config.max_context_tokens
        nodes: list[MemoryNode] = []
        layers_represented: set[str] = set()

        # Agent-specific retrieval strategies
        if agent_type == "triage":
            # Get strategic goals and operational rules
            strategic = await self.query(
                layer=MemoryLayer.STRATEGIC,
                resolution=MemoryResolution.SUMMARY,
                limit=5,
            )
            operational = await self.query(
                layer=MemoryLayer.OPERATIONAL,
                resolution=MemoryResolution.MICRO,
                limit=10,
            )
            nodes.extend(strategic)
            nodes.extend(operational)

        elif agent_type == "executor":
            # Get relevant entities and similar past events
            mission_text = passport.mission.objective
            similar = await self.find_similar(
                mission_text,
                layer=MemoryLayer.EVENT,
                limit=5,
            )
            nodes.extend(similar)

        elif agent_type == "judge":
            # Get operational policies and compliance rules
            operational = await self.query(
                layer=MemoryLayer.OPERATIONAL,
                resolution=MemoryResolution.FULL,
                limit=10,
            )
            nodes.extend(operational)

        elif agent_type == "inspector":
            # Get equipment standards and past findings
            # Look for equipment context in passport
            equipment_type = passport.context.get("equipment_type")
            if equipment_type:
                standards = await self.query(
                    tags={"equipment_type": equipment_type},
                    layer=MemoryLayer.OPERATIONAL,
                    resolution=MemoryResolution.FULL,
                    limit=5,
                )
                nodes.extend(standards)

            # Find similar findings
            finding_desc = passport.context.get("finding_description", "")
            if finding_desc:
                similar_findings = await self.find_similar(
                    finding_desc,
                    layer=MemoryLayer.EVENT,
                    limit=5,
                )
                nodes.extend(similar_findings)

        else:
            # Generic: get high-salience nodes across layers
            for layer in MemoryLayer:
                layer_nodes = await self.query(
                    layer=layer,
                    resolution=MemoryResolution.MICRO,
                    limit=5,
                )
                nodes.extend(layer_nodes)

        # Collect unique layers
        for node in nodes:
            layers_represented.add(node.layer.value)

        # Estimate tokens (rough: 1 token per 4 chars)
        total_chars = sum(len(n.micro) + len(n.summary) for n in nodes)
        token_estimate = total_chars // 4

        # Trim if over budget
        if token_estimate > max_tokens:
            nodes = self._trim_to_budget(nodes, max_tokens)
            total_chars = sum(len(n.micro) + len(n.summary) for n in nodes)
            token_estimate = total_chars // 4

        return AgentContext(
            nodes=nodes,
            total_tokens_estimate=token_estimate,
            layers_represented=list(layers_represented),
            retrieval_summary=f"Retrieved {len(nodes)} nodes for {agent_type} agent",
        )

    def _trim_to_budget(self, nodes: list[MemoryNode], max_tokens: int) -> list[MemoryNode]:
        """Trim nodes to fit token budget, keeping highest salience."""
        # Sort by salience descending
        sorted_nodes = sorted(nodes, key=lambda n: n.salience, reverse=True)

        result: list[MemoryNode] = []
        current_tokens = 0

        for node in sorted_nodes:
            node_tokens = (len(node.micro) + len(node.summary)) // 4
            if current_tokens + node_tokens <= max_tokens:
                result.append(node)
                current_tokens += node_tokens
            else:
                break

        return result

    # -------------------------------------------------------------------------
    # Precedent Matching
    # -------------------------------------------------------------------------

    async def find_precedents(
        self,
        description: str,
        node_type: str | None = None,
        limit: int = 5,
    ) -> list[MemoryNode]:
        """Find similar past cases for precedent matching.

        Used by agents to find relevant past decisions and outcomes.

        Args:
            description: Description of current case
            node_type: Filter by node type (e.g., "finding", "decision")
            limit: Max precedents to return

        Returns:
            List of similar past cases ordered by relevance
        """
        builder = MemoryQueryBuilder(self.session, self.tenant_id, self.team_id)
        builder = (
            builder
            .semantic(description)
            .layer(MemoryLayer.EVENT)
            .resolution(MemoryResolution.SUMMARY)
            .limit(limit)
        )

        if node_type:
            builder = builder.type(node_type)

        result = await builder.execute()
        return result.nodes

    # -------------------------------------------------------------------------
    # Memory Management
    # -------------------------------------------------------------------------

    async def store(self, node: MemoryNode) -> MemoryNode:
        """Store a new memory node.

        Args:
            node: Node to store

        Returns:
            Stored node
        """
        # Store in PostgreSQL
        stored = await self._storage.create(node)

        # Store embedding in ChromaDB
        self._embeddings.add(node)

        return stored

    async def store_many(self, nodes: list[MemoryNode]) -> list[MemoryNode]:
        """Store multiple nodes in a batch.

        Args:
            nodes: Nodes to store

        Returns:
            Stored nodes
        """
        stored = await self._storage.create_many(nodes)
        self._embeddings.add_many(nodes)
        return stored

    async def update(self, node: MemoryNode) -> MemoryNode:
        """Update an existing memory node.

        Args:
            node: Node with updated content

        Returns:
            Updated node
        """
        updated = await self._storage.update(node)
        self._embeddings.update(node)
        return updated

    async def add_relationship(
        self,
        source_symbol: str,
        target_symbol: str,
        relation_type: RelationType,
        weight: float = 1.0,
    ) -> bool:
        """Add a relationship between two nodes.

        Args:
            source_symbol: Source node symbol
            target_symbol: Target node symbol
            relation_type: Type of relationship
            weight: Relationship weight (0-1)

        Returns:
            True if relationship created successfully
        """
        return await self._storage.add_relationship(
            source_symbol, target_symbol, relation_type, weight
        )

    async def get_stats(self) -> dict[str, Any]:
        """Get memory statistics for this team.

        Returns:
            Dict with node counts per layer and total embeddings
        """
        layer_counts = await self._storage.count_by_layer(self.team_id)
        embedding_count = self._embeddings.count()

        return {
            "nodes_by_layer": layer_counts,
            "total_nodes": sum(layer_counts.values()),
            "total_embeddings": embedding_count,
        }
