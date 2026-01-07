"""SQLAlchemy models for database persistence."""

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TenantModel(Base):
    """Multi-tenant organization."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    teams: Mapped[list["TeamModel"]] = relationship(back_populates="tenant")
    passports: Mapped[list["PassportModel"]] = relationship(back_populates="tenant")


class TeamModel(Base):
    """Agent team configuration."""

    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    team_type: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant: Mapped["TenantModel"] = relationship(back_populates="teams")
    passports: Mapped[list["PassportModel"]] = relationship(back_populates="team")

    __table_args__ = (Index("ix_teams_tenant_id", "tenant_id"),)


class PassportModel(Base):
    """Persisted passport state."""

    __tablename__ = "passports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("teams.id"), nullable=False)

    # Mission
    mission_objective: Mapped[str] = mapped_column(Text, nullable=False)
    mission_data: Mapped[dict] = mapped_column(JSON, default=dict)

    # State
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "in_progress",
            "blocked",
            "completed",
            "failed",
            "escalated",
            name="passport_status",
        ),
        default="pending",
    )
    current_agent: Mapped[str | None] = mapped_column(String(100), nullable=True)
    checkpoint_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Routing
    routing: Mapped[dict] = mapped_column(JSON, default=dict)

    # Working memory and artifacts
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    artifacts: Mapped[dict] = mapped_column(JSON, default=dict)

    # Quality
    overall_confidence: Mapped[dict] = mapped_column(JSON, default=dict)
    revision_count: Mapped[int] = mapped_column(default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    tenant: Mapped["TenantModel"] = relationship(back_populates="passports")
    team: Mapped["TeamModel"] = relationship(back_populates="passports")
    ledger_entries: Mapped[list["LedgerEntryModel"]] = relationship(
        back_populates="passport", order_by="LedgerEntryModel.timestamp"
    )

    __table_args__ = (
        Index("ix_passports_tenant_id", "tenant_id"),
        Index("ix_passports_team_id", "team_id"),
        Index("ix_passports_status", "status"),
    )


class LedgerEntryModel(Base):
    """Immutable audit log entry."""

    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    passport_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("passports.id"), nullable=False)

    # Agent action
    agent_id: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    inputs_summary: Mapped[str] = mapped_column(Text, nullable=False)
    outputs_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Metrics
    duration_ms: Mapped[int] = mapped_column(default=0)
    tokens_used: Mapped[int] = mapped_column(default=0)
    cost_usd: Mapped[float] = mapped_column(default=0.0)

    # Confidence
    confidence: Mapped[dict] = mapped_column(JSON, default=dict)

    # Additional data
    tool_calls: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, default="")

    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    passport: Mapped["PassportModel"] = relationship(back_populates="ledger_entries")

    __table_args__ = (
        Index("ix_ledger_entries_passport_id", "passport_id"),
        Index("ix_ledger_entries_agent_id", "agent_id"),
        Index("ix_ledger_entries_timestamp", "timestamp"),
    )


class MemoryNodeModel(Base):
    """Persisted memory node with multi-resolution content."""

    __tablename__ = "memory_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    team_id: Mapped[str] = mapped_column(String(100), nullable=False)

    # Symbol addressing: layer.type.id
    symbol: Mapped[str] = mapped_column(String(500), nullable=False)
    layer: Mapped[str] = mapped_column(String(50), nullable=False)
    node_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Multi-resolution content
    micro: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    full_content: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Structured tags for filtering: ["facility:dayton-fleet", "priority:high_30"]
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Quality signals
    salience: Mapped[float] = mapped_column(Float, default=0.5)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    tenant: Mapped["TenantModel"] = relationship()
    outgoing_relations: Mapped[list["MemoryRelationshipModel"]] = relationship(
        back_populates="source_node",
        foreign_keys="MemoryRelationshipModel.source_id",
    )
    incoming_relations: Mapped[list["MemoryRelationshipModel"]] = relationship(
        back_populates="target_node",
        foreign_keys="MemoryRelationshipModel.target_id",
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "symbol", name="uq_memory_nodes_tenant_symbol"),
        Index("ix_memory_nodes_tenant_id", "tenant_id"),
        Index("ix_memory_nodes_team_id", "team_id"),
        Index("ix_memory_nodes_layer", "layer"),
        Index("ix_memory_nodes_node_type", "node_type"),
        Index("ix_memory_nodes_tags", "tags", postgresql_using="gin"),
        Index("ix_memory_nodes_salience", "salience"),
    )


class MemoryRelationshipModel(Base):
    """Typed edge between memory nodes."""

    __tablename__ = "memory_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memory_nodes.id"), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memory_nodes.id"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)

    weight: Mapped[float] = mapped_column(Float, default=1.0)
    relation_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    source_node: Mapped["MemoryNodeModel"] = relationship(
        back_populates="outgoing_relations",
        foreign_keys=[source_id],
    )
    target_node: Mapped["MemoryNodeModel"] = relationship(
        back_populates="incoming_relations",
        foreign_keys=[target_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "source_id", "target_id", "relation_type",
            name="uq_memory_relationships_source_target_type"
        ),
        Index("ix_memory_relationships_tenant_id", "tenant_id"),
        Index("ix_memory_relationships_source_id", "source_id"),
        Index("ix_memory_relationships_target_id", "target_id"),
        Index("ix_memory_relationships_relation_type", "relation_type"),
    )
