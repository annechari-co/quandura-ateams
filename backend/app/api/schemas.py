"""API request/response schemas."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MissionCreate(BaseModel):
    """Request to create a new mission."""

    objective: str = Field(..., min_length=1, max_length=2000)
    constraints: list[str] = []
    success_criteria: list[str] = []
    requester_department: str
    matter_type: str
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    deadline: datetime | None = None
    context: dict[str, Any] = {}


class PassportResponse(BaseModel):
    """Passport data for API response."""

    id: UUID
    tenant_id: str
    team_id: str
    status: str
    current_agent: str | None
    mission_objective: str
    created_at: datetime
    updated_at: datetime
    overall_confidence: float
    revision_count: int
    artifacts: dict[str, str]

    class Config:
        from_attributes = True


class PassportDetailResponse(PassportResponse):
    """Detailed passport response including ledger."""

    mission: dict[str, Any]
    routing: dict[str, Any]
    context: dict[str, Any]
    ledger: list[dict[str, Any]]


class PassportListResponse(BaseModel):
    """Paginated list of passports."""

    items: list[PassportResponse]
    total: int
    page: int
    page_size: int


class LedgerEntryResponse(BaseModel):
    """Single ledger entry response."""

    id: UUID
    timestamp: datetime
    agent_id: str
    action: str
    inputs_summary: str
    outputs_summary: str
    duration_ms: int
    tokens_used: int
    cost_usd: float
    confidence: dict[str, Any]
    tool_calls: list[str]
    notes: str


class MissionStatusUpdate(BaseModel):
    """Update mission status or provide feedback."""

    status: (
        Literal["pending", "in_progress", "blocked", "completed", "failed", "escalated"] | None
    ) = None
    feedback: str | None = None
    context_updates: dict[str, Any] = {}
