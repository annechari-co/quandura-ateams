"""
Core Passport schema - the state object that travels between agents.

The Passport is the single source of truth for any work item in the system.
"""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ConfidenceVector(BaseModel):
    """Evidence-based confidence with historical calibration."""

    value: float = Field(ge=0.0, le=1.0, description="Current confidence 0-1")
    evidence_count: int = Field(default=0, description="Number of supporting sources")
    evidence_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    historical_accuracy: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How accurate this agent has been on similar tasks",
    )
    failure_modes: list[str] = Field(
        default_factory=list,
        description="Known failure patterns for this type of task",
    )
    calibration_samples: int = Field(default=0, description="Training samples for this pattern")


class LedgerEntry(BaseModel):
    """Immutable record of an agent action."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    action: str
    inputs_summary: str
    outputs_summary: str
    duration_ms: int
    tokens_used: int = 0
    cost_usd: float = 0.0
    confidence: ConfidenceVector
    tool_calls: list[str] = Field(default_factory=list)
    notes: str = ""


class RoutingInfo(BaseModel):
    """Where the passport should go next."""

    next_agent: str | None = None
    fallback_agent: str | None = None
    escalation_required: bool = False
    escalation_reason: str | None = None
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    deadline: datetime | None = None


class Mission(BaseModel):
    """What we're trying to accomplish."""

    objective: str
    constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    requester_id: str
    requester_department: str
    matter_type: str
    sub_tasks: list[str] = Field(default_factory=list)


class Passport(BaseModel):
    """
    Core state object that travels between agents.

    This is the single source of truth for any work item in the system.
    """

    # Identity
    id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    team_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Mission
    mission: Mission

    # State
    status: Literal["pending", "in_progress", "blocked", "completed", "failed", "escalated"] = (
        "pending"
    )
    current_agent: str | None = None
    checkpoint_id: str | None = None  # LangGraph checkpoint reference

    # Routing
    routing: RoutingInfo = Field(default_factory=RoutingInfo)

    # Audit trail (append-only)
    ledger: list[LedgerEntry] = Field(default_factory=list)

    # Working memory (mutable, agent-specific)
    context: dict[str, Any] = Field(default_factory=dict)

    # Artifacts produced
    artifacts: dict[str, str] = Field(default_factory=dict)  # name -> storage_ref

    # Quality tracking
    overall_confidence: ConfidenceVector = Field(default_factory=ConfidenceVector)
    revision_count: int = 0

    def add_ledger_entry(
        self,
        agent_id: str,
        action: str,
        inputs_summary: str,
        outputs_summary: str,
        duration_ms: int,
        confidence: ConfidenceVector,
        **kwargs: Any,
    ) -> None:
        """Append a new entry to the immutable ledger."""
        entry = LedgerEntry(
            agent_id=agent_id,
            action=action,
            inputs_summary=inputs_summary,
            outputs_summary=outputs_summary,
            duration_ms=duration_ms,
            confidence=confidence,
            **kwargs,
        )
        self.ledger.append(entry)
        self.updated_at = datetime.utcnow()
