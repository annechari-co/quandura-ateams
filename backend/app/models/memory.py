"""Organizational memory system with multi-layer, multi-resolution architecture.

This module defines the memory schema that enables teams to:
- Store knowledge across 4 semantic layers (strategic, operational, entity, event)
- Retrieve at multiple resolutions (micro, summary, full) for context efficiency
- Define custom types per team with pluggable schemas
- Track relationships between nodes for graph traversal
- Use structured tags for fast filtering (e.g., "customer:042", "outcome:denied")
"""

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# =============================================================================
# LAYER DEFINITIONS
# =============================================================================

class MemoryLayer(str, Enum):
    """Universal semantic layers for organizational memory.

    Every team uses these 4 layers. The specific TYPES within each layer
    are pluggable per team.
    """

    STRATEGIC = "strategic"      # Why: Goals, values, optimization targets
    OPERATIONAL = "operational"  # How: Rules, constraints, procedures
    ENTITY = "entity"           # What: Persistent objects tracked over time
    EVENT = "event"             # When: Things that happen, with outcomes


# =============================================================================
# RELATIONSHIP TYPES
# =============================================================================

class RelationType(str, Enum):
    """Typed relationships between memory nodes."""

    # Cross-layer relationships
    INVOLVES = "involves"           # event → entity
    APPLIES = "applies"             # event → operational (policy used)
    ALIGNED_WITH = "aligned_with"   # event/operational → strategic
    INFORMS = "informs"             # strategic → operational

    # Within-layer relationships
    SUPERSEDES = "supersedes"       # operational → operational (version)
    CONFLICTS_WITH = "conflicts_with"  # operational → operational
    SIMILAR_TO = "similar_to"       # event → event
    ESCALATED_TO = "escalated_to"   # event → event
    FOLLOWS = "follows"             # event → event (sequence)
    DERIVED_FROM = "derived_from"   # pattern → source events
    RELATED_TO = "related_to"       # entity → entity

    # Causation
    CAUSED = "caused"               # event → decision/outcome
    CAUSED_BY = "caused_by"         # decision → event
    RESOLVED = "resolved"           # event → event
    BLOCKED_BY = "blocked_by"       # event → event


class Relationship(BaseModel):
    """A typed edge between two memory nodes."""

    source_symbol: str
    target_symbol: str
    relation_type: RelationType
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# MULTI-RESOLUTION CONTENT
# =============================================================================

class MemoryResolution(str, Enum):
    """Resolution levels for context retrieval."""

    MICRO = "micro"       # ~10-20 tokens, for listing/scanning
    SUMMARY = "summary"   # ~50-100 tokens, for reasoning
    FULL = "full"         # Complete content, loaded on demand


# =============================================================================
# BASE MEMORY NODE
# =============================================================================

class MemoryNode(BaseModel):
    """Base class for all memory nodes with multi-resolution content.

    Every node in organizational memory inherits from this. It provides:
    - Hierarchical symbol addressing
    - Multi-resolution content (micro, summary, full)
    - Structured tags for filtering (e.g., "customer:042", "policy:refund.v3")
    - Relationship tracking
    """

    # Identity
    id: UUID = Field(default_factory=uuid4)
    symbol: str = Field(
        ...,
        description="Hierarchical address: layer.type.id[.sub]*",
        pattern=r"^(strategic|operational|entity|event)\.\w+\.\w[\w\-]*(\.\w[\w\-]*)*$",
    )
    tenant_id: str
    team_id: str

    # Multi-resolution content
    micro: str = Field(
        ...,
        max_length=100,
        description="~10-20 tokens, dense representation for listing",
    )
    summary: str = Field(
        ...,
        max_length=500,
        description="~50-100 tokens, enough for reasoning",
    )
    full: str = Field(
        ...,
        description="Complete content, loaded on demand",
    )

    # Structured tags for filtering
    # Convention: "key:value" format, e.g., "customer:042", "outcome:denied"
    tags: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Quality signals
    salience: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance score, context-dependent",
    )
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    # Relationships (just symbols, not full nodes)
    relationships: list[Relationship] = Field(default_factory=list)

    # Embedding for similarity search
    embedding: list[float] | None = None

    @property
    def layer(self) -> MemoryLayer:
        """Extract layer from symbol."""
        return MemoryLayer(self.symbol.split(".")[0])

    @property
    def node_type(self) -> str:
        """Extract type from symbol."""
        return self.symbol.split(".")[1]

    @property
    def node_id(self) -> str:
        """Extract ID portion from symbol."""
        parts = self.symbol.split(".")
        return ".".join(parts[2:])

    # -------------------------------------------------------------------------
    # Structured Tag Helpers
    # -------------------------------------------------------------------------

    def add_tag(self, key: str, value: str) -> None:
        """Add a structured tag (key:value format)."""
        tag = f"{key}:{value}"
        if tag not in self.tags:
            self.tags.append(tag)

    def get_tag(self, key: str) -> str | None:
        """Get value for a structured tag key."""
        prefix = f"{key}:"
        for tag in self.tags:
            if tag.startswith(prefix):
                return tag[len(prefix):]
        return None

    def has_tag(self, key: str, value: str | None = None) -> bool:
        """Check if tag exists, optionally with specific value."""
        if value is None:
            prefix = f"{key}:"
            return any(tag.startswith(prefix) for tag in self.tags)
        return f"{key}:{value}" in self.tags

    def get_all_structured_tags(self) -> dict[str, str]:
        """Get all structured tags as a dict."""
        result = {}
        for tag in self.tags:
            if ":" in tag:
                key, value = tag.split(":", 1)
                result[key] = value
        return result

    def remove_tag(self, key: str, value: str | None = None) -> bool:
        """Remove a tag. Returns True if removed."""
        if value is None:
            prefix = f"{key}:"
            original_len = len(self.tags)
            self.tags = [t for t in self.tags if not t.startswith(prefix)]
            return len(self.tags) < original_len
        tag = f"{key}:{value}"
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False


# =============================================================================
# EXTENSION NODE (FOR TEAM-DEFINED TYPES)
# =============================================================================

class ExtensionNode(MemoryNode):
    """Flexible node for team-defined extension types.

    Extension types allow teams to add new node types at runtime without
    platform updates. They have minimal schema requirements.
    """

    # Arbitrary key-value properties
    properties: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    created_by: str = Field(default="", description="Who added this node")
    notes: str = Field(default="", description="Context about this node")


# =============================================================================
# TEAM MEMORY SCHEMA
# =============================================================================

class TypeDefinition(BaseModel):
    """Definition of a node type within a layer."""

    name: str
    description: str
    required_properties: list[str] = Field(default_factory=list)
    optional_properties: list[str] = Field(default_factory=list)
    micro_format: str = Field(
        default="{type}|{id}|{status}",
        description="Template for micro representation",
    )
    example_tags: list[str] = Field(default_factory=list)


class RelationshipRule(BaseModel):
    """Constraint on what relationships are allowed."""

    source_layer: MemoryLayer
    target_layer: MemoryLayer
    allowed_relations: list[RelationType]


class TeamMemorySchema(BaseModel):
    """Pluggable memory schema for a team.

    Defines what types exist in each layer, what relationships are allowed,
    and how nodes should be formatted.
    """

    id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    team_id: str
    team_type: str  # "customer_service", "legal_research", "prop_trading"

    # Type definitions per layer
    strategic_types: dict[str, TypeDefinition] = Field(default_factory=dict)
    operational_types: dict[str, TypeDefinition] = Field(default_factory=dict)
    entity_types: dict[str, TypeDefinition] = Field(default_factory=dict)
    event_types: dict[str, TypeDefinition] = Field(default_factory=dict)

    # Relationship constraints
    relationship_rules: list[RelationshipRule] = Field(default_factory=list)

    # Extension types (added at runtime)
    extension_types: dict[str, TypeDefinition] = Field(default_factory=dict)

    # Schema metadata
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_types_for_layer(self, layer: MemoryLayer) -> dict[str, TypeDefinition]:
        """Get all types (predefined + extension) for a layer."""
        layer_types = {
            MemoryLayer.STRATEGIC: self.strategic_types,
            MemoryLayer.OPERATIONAL: self.operational_types,
            MemoryLayer.ENTITY: self.entity_types,
            MemoryLayer.EVENT: self.event_types,
        }
        base_types = layer_types.get(layer, {})

        # Add extension types for this layer
        extensions = {
            k: v for k, v in self.extension_types.items()
            if k.startswith(f"{layer.value}.")
        }
        return {**base_types, **extensions}

    def register_extension_type(
        self,
        layer: MemoryLayer,
        type_name: str,
        description: str,
        created_by: str,
        example_tags: list[str] | None = None,
    ) -> TypeDefinition:
        """Register a new extension type at runtime."""
        type_def = TypeDefinition(
            name=type_name,
            description=description,
            example_tags=example_tags or [],
        )
        key = f"{layer.value}.{type_name}"
        self.extension_types[key] = type_def
        self.updated_at = datetime.utcnow()
        return type_def


# =============================================================================
# LAYER-SPECIFIC NODE TYPES (EXAMPLES)
# =============================================================================

class StrategicGoalNode(MemoryNode):
    """Organization-wide objective."""

    title: str
    success_metrics: list[str] = Field(default_factory=list)
    owner: str = ""
    timeframe: str = ""
    status: Literal["active", "achieved", "deprecated"] = "active"


class StrategicPriorityNode(MemoryNode):
    """Ranked importance for decision-making."""

    name: str
    rank: int
    weight: float = Field(default=1.0, ge=0.0, le=1.0)


class PolicyNode(MemoryNode):
    """Operational rule or procedure."""

    domain: str
    version: str
    effective_date: datetime
    applies_to: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    decision_factors: list[str] = Field(default_factory=list)
    approval_thresholds: dict[str, Any] = Field(default_factory=dict)


class CustomerEntityNode(MemoryNode):
    """Customer profile built over time."""

    external_id: str | None = None
    phone: str | None = None
    email: str | None = None
    tier: Literal["standard", "premium", "vip"] = "standard"
    tenure_days: int = 0
    lifetime_value: float = 0.0
    total_interactions: int = 0
    sentiment_trend: Literal["positive", "neutral", "negative", "mixed"] = "neutral"


class InteractionEventNode(MemoryNode):
    """A single customer interaction."""

    channel: Literal["call", "email", "chat", "ticket"]
    duration_seconds: int | None = None
    customer_symbol: str | None = None
    agent_id: str
    topic: str
    sentiment: Literal["positive", "neutral", "negative"]
    outcome: Literal["resolved", "escalated", "pending", "transferred"]
    resolution: str | None = None


class DecisionEventNode(MemoryNode):
    """A decision made during an interaction."""

    decision_type: str
    outcome: str
    amount: float | None = None
    reason: str
    factors: list[str] = Field(default_factory=list)
    policy_applied: str | None = None
    policy_section: str | None = None
    deciding_agent: str = ""


# =============================================================================
# PRECEDENT CONTEXT (FOR PASSPORT INTEGRATION)
# =============================================================================

class SimilarCase(BaseModel):
    """A relevant precedent for decision-making."""

    symbol: str
    similarity_score: float
    outcome: str
    reason: str
    key_factors: list[str] = Field(default_factory=list)


class PrecedentContext(BaseModel):
    """Relevant past decisions loaded into Passport context."""

    similar_cases: list[SimilarCase] = Field(default_factory=list)
    applicable_policies: list[str] = Field(default_factory=list)  # symbols
    entity_history: list[str] = Field(default_factory=list)  # symbols
    pattern_summary: str = ""


# =============================================================================
# MEMORY QUERY TYPES
# =============================================================================

class MemoryQuery(BaseModel):
    """Query specification for memory retrieval."""

    # What to find
    pattern: str | None = None  # "event.call.*" glob pattern
    text_query: str | None = None  # Semantic search
    symbols: list[str] | None = None  # Exact symbol lookup

    # Filters
    layer: MemoryLayer | None = None
    node_type: str | None = None
    tags: list[str] | None = None  # Filter by tags, e.g., ["customer:042", "outcome:denied"]
    tag_filter: dict[str, str] | None = None
    time_range: tuple[datetime, datetime] | None = None
    min_salience: float | None = None

    # Traversal
    traverse_from: str | None = None  # Start symbol for graph walk
    relation_types: list[RelationType] | None = None
    max_depth: int = 1

    # Output control
    resolution: MemoryResolution = MemoryResolution.SUMMARY
    limit: int = 10
    offset: int = 0


class MemoryQueryResult(BaseModel):
    """Result from memory query."""

    nodes: list[MemoryNode]
    total_count: int
    query_time_ms: int
    resolution_used: MemoryResolution


# =============================================================================
# CONSOLIDATION (SALIENCE RECALCULATION)
# =============================================================================

class ConsolidationConfig(BaseModel):
    """Configuration for memory consolidation."""

    # Decay parameters
    time_decay_rate: float = Field(
        default=0.1,
        description="How much salience decays per day without access",
    )
    access_boost: float = Field(
        default=0.05,
        description="Salience boost per retrieval",
    )

    # Relationship effects
    cross_layer_boost: float = Field(
        default=0.1,
        description="Boost for nodes with cross-layer relationships",
    )

    # Pruning
    prune_threshold: float = Field(
        default=0.01,
        description="Salience below which nodes are archived",
    )
    min_age_days: int = Field(
        default=30,
        description="Minimum age before pruning eligible",
    )


class ConsolidationResult(BaseModel):
    """Result of consolidation run."""

    nodes_updated: int
    nodes_pruned: int
    duration_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
