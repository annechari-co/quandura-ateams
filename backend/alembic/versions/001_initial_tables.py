"""Initial tables including memory system.

Revision ID: 001
Revises:
Create Date: 2025-01-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Tenants
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("settings", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # Teams
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("team_type", sa.String(100), nullable=False),
        sa.Column("config", postgresql.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_teams_tenant_id", "teams", ["tenant_id"])

    # Passports
    op.create_table(
        "passports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_objective", sa.Text(), nullable=False),
        sa.Column("mission_data", postgresql.JSON(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "in_progress", "blocked", "completed", "failed", "escalated",
                name="passport_status",
            ),
            nullable=True,
        ),
        sa.Column("current_agent", sa.String(100), nullable=True),
        sa.Column("checkpoint_id", sa.String(255), nullable=True),
        sa.Column("routing", postgresql.JSON(), nullable=True),
        sa.Column("context", postgresql.JSON(), nullable=True),
        sa.Column("artifacts", postgresql.JSON(), nullable=True),
        sa.Column("overall_confidence", postgresql.JSON(), nullable=True),
        sa.Column("revision_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_passports_tenant_id", "passports", ["tenant_id"])
    op.create_index("ix_passports_team_id", "passports", ["team_id"])
    op.create_index("ix_passports_status", "passports", ["status"])

    # Ledger Entries
    op.create_table(
        "ledger_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("passport_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_id", sa.String(100), nullable=False),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("inputs_summary", sa.Text(), nullable=False),
        sa.Column("outputs_summary", sa.Text(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("cost_usd", sa.Float(), nullable=True),
        sa.Column("confidence", postgresql.JSON(), nullable=True),
        sa.Column("tool_calls", postgresql.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["passport_id"], ["passports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ledger_entries_passport_id", "ledger_entries", ["passport_id"])
    op.create_index("ix_ledger_entries_agent_id", "ledger_entries", ["agent_id"])
    op.create_index("ix_ledger_entries_timestamp", "ledger_entries", ["timestamp"])

    # Memory Nodes
    op.create_table(
        "memory_nodes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", sa.String(100), nullable=False),
        sa.Column("symbol", sa.String(500), nullable=False),
        sa.Column("layer", sa.String(50), nullable=False),
        sa.Column("node_type", sa.String(100), nullable=False),
        sa.Column("micro", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("full_content", postgresql.JSONB(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("salience", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memory_nodes_tenant_id", "memory_nodes", ["tenant_id"])
    op.create_index("ix_memory_nodes_team_id", "memory_nodes", ["team_id"])
    op.create_index("ix_memory_nodes_layer", "memory_nodes", ["layer"])
    op.create_index("ix_memory_nodes_node_type", "memory_nodes", ["node_type"])
    op.create_index(
        "ix_memory_nodes_tags",
        "memory_nodes",
        ["tags"],
        postgresql_using="gin",
    )
    op.create_index("ix_memory_nodes_salience", "memory_nodes", ["salience"])
    op.create_unique_constraint(
        "uq_memory_nodes_tenant_symbol",
        "memory_nodes",
        ["tenant_id", "symbol"],
    )

    # Memory Relationships
    op.create_table(
        "memory_relationships",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relation_type", sa.String(50), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("relation_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["source_id"], ["memory_nodes.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["memory_nodes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_memory_relationships_tenant_id", "memory_relationships", ["tenant_id"])
    op.create_index("ix_memory_relationships_source_id", "memory_relationships", ["source_id"])
    op.create_index("ix_memory_relationships_target_id", "memory_relationships", ["target_id"])
    op.create_index(
        "ix_memory_relationships_relation_type",
        "memory_relationships",
        ["relation_type"],
    )
    op.create_unique_constraint(
        "uq_memory_relationships_source_target_type",
        "memory_relationships",
        ["source_id", "target_id", "relation_type"],
    )


def downgrade() -> None:
    op.drop_table("memory_relationships")
    op.drop_table("memory_nodes")
    op.drop_table("ledger_entries")
    op.drop_table("passports")
    op.execute("DROP TYPE IF EXISTS passport_status")
    op.drop_table("teams")
    op.drop_table("tenants")
