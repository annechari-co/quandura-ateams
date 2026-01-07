"""Memory API endpoints for knowledge storage and retrieval."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.memory.queries import MemoryQueryBuilder
from app.memory.storage import MemoryStorage
from app.models.memory import MemoryLayer, MemoryNode, MemoryResolution, RelationType

router = APIRouter(prefix="/memory", tags=["memory"])


# =============================================================================
# Request/Response Models
# =============================================================================


class CreateNodeRequest(BaseModel):
    """Request to create a memory node."""

    symbol: str
    layer: MemoryLayer
    node_type: str
    micro: str
    summary: str
    full_content: dict = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    salience: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class UpdateNodeRequest(BaseModel):
    """Request to update a memory node."""

    micro: str | None = None
    summary: str | None = None
    full_content: dict | None = None
    tags: list[str] | None = None
    salience: float | None = None
    confidence: float | None = None


class NodeResponse(BaseModel):
    """Response containing a memory node."""

    id: UUID
    symbol: str
    layer: str
    node_type: str
    micro: str
    summary: str
    full_content: dict
    tags: list[str]
    salience: float
    confidence: float
    created_at: str
    updated_at: str

    @classmethod
    def from_node(cls, node: MemoryNode) -> "NodeResponse":
        """Convert MemoryNode to response."""
        return cls(
            id=node.id,
            symbol=node.symbol,
            layer=node.layer.value,
            node_type=node.node_type,
            micro=node.micro,
            summary=node.summary,
            full_content=node.full_content,
            tags=node.tags,
            salience=node.salience,
            confidence=node.confidence,
            created_at=node.created_at.isoformat(),
            updated_at=node.updated_at.isoformat(),
        )


class QueryRequest(BaseModel):
    """Request for querying memory."""

    pattern: str | None = None
    tags: dict[str, str] | None = None
    layer: MemoryLayer | None = None
    node_type: str | None = None
    resolution: MemoryResolution = MemoryResolution.MICRO
    limit: int = Field(default=20, ge=1, le=100)


class SimilarityRequest(BaseModel):
    """Request for semantic similarity search."""

    text: str
    layer: MemoryLayer | None = None
    limit: int = Field(default=10, ge=1, le=50)


class RelationshipRequest(BaseModel):
    """Request to create a relationship."""

    source_symbol: str
    target_symbol: str
    relation_type: RelationType
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class TraversalRequest(BaseModel):
    """Request for graph traversal."""

    start_symbol: str
    relation_types: list[RelationType] = Field(default_factory=list)
    max_depth: int = Field(default=2, ge=1, le=5)


# =============================================================================
# Endpoints
# =============================================================================


@router.post("/nodes/{tenant_id}/{team_id}", response_model=NodeResponse)
async def create_node(
    tenant_id: UUID,
    team_id: str,
    request: CreateNodeRequest,
    db: AsyncSession = Depends(get_db),
) -> NodeResponse:
    """Create a new memory node."""
    storage = MemoryStorage(db, tenant_id)

    node = MemoryNode(
        tenant_id=tenant_id,
        team_id=team_id,
        symbol=request.symbol,
        layer=request.layer,
        node_type=request.node_type,
        micro=request.micro,
        summary=request.summary,
        full_content=request.full_content,
        tags=request.tags,
        salience=request.salience,
        confidence=request.confidence,
    )

    stored = await storage.create(node)
    return NodeResponse.from_node(stored)


@router.get("/nodes/{tenant_id}/{team_id}/{symbol:path}", response_model=NodeResponse)
async def get_node(
    tenant_id: UUID,
    team_id: str,
    symbol: str,
    resolution: MemoryResolution = Query(default=MemoryResolution.SUMMARY),
    db: AsyncSession = Depends(get_db),
) -> NodeResponse:
    """Get a memory node by symbol."""
    storage = MemoryStorage(db, tenant_id)
    node = await storage.get_by_symbol(symbol, resolution)

    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found: {symbol}")

    return NodeResponse.from_node(node)


@router.patch("/nodes/{tenant_id}/{team_id}/{symbol:path}", response_model=NodeResponse)
async def update_node(
    tenant_id: UUID,
    team_id: str,
    symbol: str,
    request: UpdateNodeRequest,
    db: AsyncSession = Depends(get_db),
) -> NodeResponse:
    """Update a memory node."""
    storage = MemoryStorage(db, tenant_id)
    existing = await storage.get_by_symbol(symbol, MemoryResolution.FULL)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Node not found: {symbol}")

    # Apply updates
    if request.micro is not None:
        existing.micro = request.micro
    if request.summary is not None:
        existing.summary = request.summary
    if request.full_content is not None:
        existing.full_content = request.full_content
    if request.tags is not None:
        existing.tags = request.tags
    if request.salience is not None:
        existing.salience = request.salience
    if request.confidence is not None:
        existing.confidence = request.confidence

    updated = await storage.update(existing)
    return NodeResponse.from_node(updated)


@router.delete("/nodes/{tenant_id}/{team_id}/{symbol:path}")
async def delete_node(
    tenant_id: UUID,
    team_id: str,
    symbol: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete a memory node."""
    storage = MemoryStorage(db, tenant_id)
    success = await storage.delete(symbol)

    if not success:
        raise HTTPException(status_code=404, detail=f"Node not found: {symbol}")

    return {"status": "deleted", "symbol": symbol}


@router.post("/query/{tenant_id}/{team_id}", response_model=list[NodeResponse])
async def query_nodes(
    tenant_id: UUID,
    team_id: str,
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
) -> list[NodeResponse]:
    """Query memory nodes with filters."""
    builder = MemoryQueryBuilder(db, tenant_id, team_id)

    if request.pattern:
        builder = builder.pattern(request.pattern)
    if request.tags:
        for key, value in request.tags.items():
            builder = builder.tag(key, value)
    if request.layer:
        builder = builder.layer(request.layer)
    if request.node_type:
        builder = builder.type(request.node_type)

    builder = builder.resolution(request.resolution).limit(request.limit)
    result = await builder.execute()

    return [NodeResponse.from_node(n) for n in result.nodes]


@router.post("/similar/{tenant_id}/{team_id}", response_model=list[NodeResponse])
async def find_similar(
    tenant_id: UUID,
    team_id: str,
    request: SimilarityRequest,
    db: AsyncSession = Depends(get_db),
) -> list[NodeResponse]:
    """Find semantically similar nodes."""
    builder = MemoryQueryBuilder(db, tenant_id, team_id)
    builder = builder.semantic(request.text).limit(request.limit)

    if request.layer:
        builder = builder.layer(request.layer)

    result = await builder.execute()
    return [NodeResponse.from_node(n) for n in result.nodes]


@router.post("/relationships/{tenant_id}")
async def create_relationship(
    tenant_id: UUID,
    request: RelationshipRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Create a relationship between nodes."""
    storage = MemoryStorage(db, tenant_id)

    success = await storage.add_relationship(
        request.source_symbol,
        request.target_symbol,
        request.relation_type,
        request.weight,
    )

    if not success:
        raise HTTPException(status_code=400, detail="Failed to create relationship")

    return {
        "status": "created",
        "source": request.source_symbol,
        "target": request.target_symbol,
        "type": request.relation_type.value,
    }


@router.post("/traverse/{tenant_id}/{team_id}", response_model=list[NodeResponse])
async def traverse_graph(
    tenant_id: UUID,
    team_id: str,
    request: TraversalRequest,
    db: AsyncSession = Depends(get_db),
) -> list[NodeResponse]:
    """Traverse the knowledge graph from a starting node."""
    storage = MemoryStorage(db, tenant_id)

    nodes = await storage.traverse(
        request.start_symbol,
        request.relation_types if request.relation_types else list(RelationType),
        request.max_depth,
        MemoryResolution.SUMMARY,
    )

    return [NodeResponse.from_node(n) for n in nodes]


@router.get("/stats/{tenant_id}/{team_id}")
async def get_stats(
    tenant_id: UUID,
    team_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get memory statistics for a team."""
    storage = MemoryStorage(db, tenant_id)
    layer_counts = await storage.count_by_layer(team_id)

    return {
        "tenant_id": str(tenant_id),
        "team_id": team_id,
        "nodes_by_layer": layer_counts,
        "total_nodes": sum(layer_counts.values()),
    }
