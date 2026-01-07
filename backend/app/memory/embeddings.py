"""ChromaDB integration for semantic search over memory nodes."""

import logging
from typing import Any
from uuid import UUID

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings
from app.models.memory import MemoryLayer, MemoryNode

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """ChromaDB-based embedding store for semantic memory search."""

    def __init__(
        self,
        tenant_id: UUID,
        team_id: str,
        collection_prefix: str = "memory",
    ):
        self.tenant_id = tenant_id
        self.team_id = team_id
        self.collection_prefix = collection_prefix

        settings = get_settings()
        self._client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._get_or_create_collection()

    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get or create the collection for this tenant/team."""
        collection_name = f"{self.collection_prefix}_{self.tenant_id}_{self.team_id}"
        # Sanitize collection name (ChromaDB has restrictions)
        collection_name = collection_name.replace("-", "_")[:63]

        return self._client.get_or_create_collection(
            name=collection_name,
            metadata={"tenant_id": str(self.tenant_id), "team_id": self.team_id},
        )

    # -------------------------------------------------------------------------
    # Storage Operations
    # -------------------------------------------------------------------------

    def add(self, node: MemoryNode) -> None:
        """Add a memory node to the embedding store."""
        # Use summary for embedding (good balance of context)
        text = f"{node.micro}\n{node.summary}"

        self._collection.add(
            ids=[str(node.id)],
            documents=[text],
            metadatas=[self._node_metadata(node)],
        )

    def add_many(self, nodes: list[MemoryNode]) -> None:
        """Add multiple nodes in a batch."""
        if not nodes:
            return

        ids = [str(n.id) for n in nodes]
        documents = [f"{n.micro}\n{n.summary}" for n in nodes]
        metadatas = [self._node_metadata(n) for n in nodes]

        self._collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def update(self, node: MemoryNode) -> None:
        """Update a node's embedding."""
        text = f"{node.micro}\n{node.summary}"

        self._collection.update(
            ids=[str(node.id)],
            documents=[text],
            metadatas=[self._node_metadata(node)],
        )

    def delete(self, node_id: UUID) -> None:
        """Delete a node from the embedding store."""
        self._collection.delete(ids=[str(node_id)])

    def delete_many(self, node_ids: list[UUID]) -> None:
        """Delete multiple nodes."""
        if not node_ids:
            return
        self._collection.delete(ids=[str(nid) for nid in node_ids])

    # -------------------------------------------------------------------------
    # Search Operations
    # -------------------------------------------------------------------------

    def find_similar(
        self,
        query: str,
        limit: int = 10,
        layer: MemoryLayer | None = None,
        node_type: str | None = None,
        min_score: float = 0.0,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Find nodes semantically similar to the query.

        Args:
            query: Text to search for
            limit: Max results to return
            layer: Filter by memory layer
            node_type: Filter by node type
            min_score: Minimum similarity score (0-1)

        Returns:
            List of (node_id, score, metadata) tuples
        """
        where_filter = self._build_where_filter(layer, node_type)

        results = self._collection.query(
            query_texts=[query],
            n_results=limit,
            where=where_filter if where_filter else None,
            include=["metadatas", "distances"],
        )

        # Convert results to list of tuples
        output: list[tuple[str, float, dict[str, Any]]] = []

        if results["ids"] and results["ids"][0]:
            ids = results["ids"][0]
            distances = results["distances"][0] if results["distances"] else [0] * len(ids)
            metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)

            for node_id, distance, metadata in zip(ids, distances, metadatas, strict=False):
                # ChromaDB returns L2 distance, convert to similarity score
                score = 1 / (1 + distance)
                if score >= min_score:
                    output.append((node_id, score, metadata))

        return output

    def find_similar_to_node(
        self,
        node: MemoryNode,
        limit: int = 10,
        same_layer_only: bool = True,
        exclude_self: bool = True,
    ) -> list[tuple[str, float, dict[str, Any]]]:
        """Find nodes similar to an existing node."""
        query = f"{node.micro}\n{node.summary}"
        layer = node.layer if same_layer_only else None

        results = self.find_similar(query, limit=limit + 1, layer=layer)

        # Filter out the node itself if requested
        if exclude_self:
            results = [(nid, score, meta) for nid, score, meta in results if nid != str(node.id)]

        return results[:limit]

    def find_by_tags(
        self,
        tags: list[str],
        limit: int = 20,
    ) -> list[tuple[str, dict[str, Any]]]:
        """Find nodes that have all specified tags."""
        # Build tag filter
        tag_filters = [{"tags": {"$contains": tag}} for tag in tags]

        if len(tag_filters) == 1:
            where_filter = tag_filters[0]
        else:
            where_filter = {"$and": tag_filters}

        results = self._collection.get(
            where=where_filter,
            limit=limit,
            include=["metadatas"],
        )

        output: list[tuple[str, dict[str, Any]]] = []
        if results["ids"]:
            ids = results["ids"]
            metadatas = results["metadatas"] if results["metadatas"] else [{}] * len(ids)
            for node_id, metadata in zip(ids, metadatas, strict=False):
                output.append((node_id, metadata))

        return output

    # -------------------------------------------------------------------------
    # Collection Management
    # -------------------------------------------------------------------------

    def count(self) -> int:
        """Get the number of embeddings in the collection."""
        return self._collection.count()

    def clear(self) -> None:
        """Clear all embeddings from the collection."""
        # ChromaDB doesn't have a clear method, so we delete and recreate
        collection_name = self._collection.name
        self._client.delete_collection(collection_name)
        self._collection = self._get_or_create_collection()

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _node_metadata(self, node: MemoryNode) -> dict[str, Any]:
        """Extract metadata for ChromaDB storage."""
        return {
            "symbol": node.symbol,
            "layer": node.layer.value,
            "node_type": node.node_type,
            "salience": node.salience,
            "tags": ",".join(node.tags),  # ChromaDB doesn't support list values well
            "created_at": node.timestamp.isoformat(),
        }

    def _build_where_filter(
        self,
        layer: MemoryLayer | None = None,
        node_type: str | None = None,
    ) -> dict[str, Any] | None:
        """Build ChromaDB where filter."""
        filters: list[dict[str, Any]] = []

        if layer:
            filters.append({"layer": layer.value})
        if node_type:
            filters.append({"node_type": node_type})

        if not filters:
            return None
        if len(filters) == 1:
            return filters[0]
        return {"$and": filters}


class EmbeddingStoreFactory:
    """Factory for creating EmbeddingStore instances per tenant/team."""

    _instances: dict[str, EmbeddingStore] = {}

    @classmethod
    def get_store(cls, tenant_id: UUID, team_id: str) -> EmbeddingStore:
        """Get or create an EmbeddingStore for the tenant/team."""
        key = f"{tenant_id}:{team_id}"
        if key not in cls._instances:
            cls._instances[key] = EmbeddingStore(tenant_id, team_id)
        return cls._instances[key]

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the store cache."""
        cls._instances.clear()
