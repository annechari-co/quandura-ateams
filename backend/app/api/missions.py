"""Mission and Passport API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.teams import create_basic_team
from app.api.schemas import (
    LedgerEntryResponse,
    MissionCreate,
    MissionStatusUpdate,
    PassportDetailResponse,
    PassportListResponse,
    PassportResponse,
)
from app.db import LedgerEntryModel, PassportModel, get_db
from app.models.passport import ConfidenceVector, Mission, Passport, RoutingInfo

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", response_model=PassportResponse, status_code=201)
async def create_mission(
    request: MissionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: str = "default",  # TODO: Extract from JWT
    team_id: str = "default",  # TODO: Determine from matter_type
) -> PassportResponse:
    """Create a new mission and return its passport."""
    # Create Pydantic passport
    mission = Mission(
        objective=request.objective,
        constraints=request.constraints,
        success_criteria=request.success_criteria,
        requester_id=tenant_id,  # TODO: Extract from auth
        requester_department=request.requester_department,
        matter_type=request.matter_type,
    )

    passport = Passport(
        tenant_id=tenant_id,
        team_id=team_id,
        mission=mission,
        routing=RoutingInfo(
            priority=request.priority,
            deadline=request.deadline,
        ),
        context=request.context,
    )

    # Persist to database
    db_passport = PassportModel(
        id=passport.id,
        tenant_id=tenant_id,
        team_id=team_id,
        mission_objective=mission.objective,
        mission_data=mission.model_dump(),
        status=passport.status,
        routing=passport.routing.model_dump(),
        context=passport.context,
        overall_confidence=passport.overall_confidence.model_dump(),
    )
    db.add(db_passport)
    await db.flush()

    return PassportResponse(
        id=db_passport.id,
        tenant_id=db_passport.tenant_id,
        team_id=str(db_passport.team_id),
        status=db_passport.status,
        current_agent=db_passport.current_agent,
        mission_objective=db_passport.mission_objective,
        created_at=db_passport.created_at,
        updated_at=db_passport.updated_at,
        overall_confidence=db_passport.overall_confidence.get("value", 0.0),
        revision_count=db_passport.revision_count,
        artifacts=db_passport.artifacts,
    )


@router.get("", response_model=PassportListResponse)
async def list_missions(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: str = "default",  # TODO: Extract from JWT
    status: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PassportListResponse:
    """List missions with pagination."""
    query = select(PassportModel).where(PassportModel.tenant_id == tenant_id)

    if status:
        query = query.where(PassportModel.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    # Apply pagination
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(PassportModel.created_at.desc())

    result = await db.execute(query)
    passports = result.scalars().all()

    return PassportListResponse(
        items=[
            PassportResponse(
                id=p.id,
                tenant_id=p.tenant_id,
                team_id=str(p.team_id),
                status=p.status,
                current_agent=p.current_agent,
                mission_objective=p.mission_objective,
                created_at=p.created_at,
                updated_at=p.updated_at,
                overall_confidence=p.overall_confidence.get("value", 0.0),
                revision_count=p.revision_count,
                artifacts=p.artifacts,
            )
            for p in passports
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{mission_id}", response_model=PassportDetailResponse)
async def get_mission(
    mission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: str = "default",
) -> PassportDetailResponse:
    """Get detailed mission information."""
    result = await db.execute(
        select(PassportModel).where(
            PassportModel.id == mission_id,
            PassportModel.tenant_id == tenant_id,
        )
    )
    passport = result.scalar_one_or_none()

    if not passport:
        raise HTTPException(status_code=404, detail="Mission not found")

    # Get ledger entries
    ledger_result = await db.execute(
        select(LedgerEntryModel)
        .where(LedgerEntryModel.passport_id == mission_id)
        .order_by(LedgerEntryModel.timestamp)
    )
    ledger_entries = ledger_result.scalars().all()

    return PassportDetailResponse(
        id=passport.id,
        tenant_id=passport.tenant_id,
        team_id=str(passport.team_id),
        status=passport.status,
        current_agent=passport.current_agent,
        mission_objective=passport.mission_objective,
        created_at=passport.created_at,
        updated_at=passport.updated_at,
        overall_confidence=passport.overall_confidence.get("value", 0.0),
        revision_count=passport.revision_count,
        artifacts=passport.artifacts,
        mission=passport.mission_data,
        routing=passport.routing,
        context=passport.context,
        ledger=[
            {
                "id": str(e.id),
                "timestamp": e.timestamp.isoformat(),
                "agent_id": e.agent_id,
                "action": e.action,
                "inputs_summary": e.inputs_summary,
                "outputs_summary": e.outputs_summary,
                "duration_ms": e.duration_ms,
                "tokens_used": e.tokens_used,
                "cost_usd": e.cost_usd,
                "confidence": e.confidence,
                "tool_calls": e.tool_calls,
                "notes": e.notes,
            }
            for e in ledger_entries
        ],
    )


@router.patch("/{mission_id}", response_model=PassportResponse)
async def update_mission(
    mission_id: UUID,
    request: MissionStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: str = "default",
) -> PassportResponse:
    """Update mission status or provide feedback."""
    result = await db.execute(
        select(PassportModel).where(
            PassportModel.id == mission_id,
            PassportModel.tenant_id == tenant_id,
        )
    )
    passport = result.scalar_one_or_none()

    if not passport:
        raise HTTPException(status_code=404, detail="Mission not found")

    if request.status:
        passport.status = request.status

    if request.context_updates:
        passport.context = {**passport.context, **request.context_updates}

    if request.feedback:
        # Add feedback to context for agent consumption
        feedback_list = passport.context.get("human_feedback", [])
        feedback_list.append(request.feedback)
        passport.context["human_feedback"] = feedback_list

    return PassportResponse(
        id=passport.id,
        tenant_id=passport.tenant_id,
        team_id=str(passport.team_id),
        status=passport.status,
        current_agent=passport.current_agent,
        mission_objective=passport.mission_objective,
        created_at=passport.created_at,
        updated_at=passport.updated_at,
        overall_confidence=passport.overall_confidence.get("value", 0.0),
        revision_count=passport.revision_count,
        artifacts=passport.artifacts,
    )


@router.get("/{mission_id}/ledger", response_model=list[LedgerEntryResponse])
async def get_mission_ledger(
    mission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: str = "default",
) -> list[LedgerEntryResponse]:
    """Get audit ledger for a mission."""
    # Verify mission exists and belongs to tenant
    passport_result = await db.execute(
        select(PassportModel.id).where(
            PassportModel.id == mission_id,
            PassportModel.tenant_id == tenant_id,
        )
    )
    if not passport_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Mission not found")

    result = await db.execute(
        select(LedgerEntryModel)
        .where(LedgerEntryModel.passport_id == mission_id)
        .order_by(LedgerEntryModel.timestamp)
    )
    entries = result.scalars().all()

    return [
        LedgerEntryResponse(
            id=e.id,
            timestamp=e.timestamp,
            agent_id=e.agent_id,
            action=e.action,
            inputs_summary=e.inputs_summary,
            outputs_summary=e.outputs_summary,
            duration_ms=e.duration_ms,
            tokens_used=e.tokens_used,
            cost_usd=e.cost_usd,
            confidence=e.confidence,
            tool_calls=e.tool_calls,
            notes=e.notes,
        )
        for e in entries
    ]


@router.post("/{mission_id}/execute", response_model=PassportDetailResponse)
async def execute_mission(
    mission_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant_id: str = "default",
) -> PassportDetailResponse:
    """Execute a mission through the agent pipeline."""
    # Get mission from database
    result = await db.execute(
        select(PassportModel).where(
            PassportModel.id == mission_id,
            PassportModel.tenant_id == tenant_id,
        )
    )
    db_passport = result.scalar_one_or_none()

    if not db_passport:
        raise HTTPException(status_code=404, detail="Mission not found")

    if db_passport.status not in ("pending", "blocked"):
        raise HTTPException(
            status_code=400,
            detail=f"Mission cannot be executed in {db_passport.status} status",
        )

    # Reconstruct Pydantic passport from DB
    mission = Mission(**db_passport.mission_data)
    passport = Passport(
        id=db_passport.id,
        tenant_id=db_passport.tenant_id,
        team_id=str(db_passport.team_id),
        mission=mission,
        status="in_progress",
        routing=RoutingInfo(**db_passport.routing),
        context=db_passport.context,
        artifacts=db_passport.artifacts,
        overall_confidence=ConfidenceVector(**db_passport.overall_confidence),
        revision_count=db_passport.revision_count,
    )

    # Create and run team
    team = create_basic_team()
    final_passport = await team.run(passport, thread_id=str(mission_id))

    # Update database with results
    db_passport.status = final_passport.status
    db_passport.current_agent = final_passport.current_agent
    db_passport.routing = final_passport.routing.model_dump()
    db_passport.context = final_passport.context
    db_passport.artifacts = final_passport.artifacts
    db_passport.overall_confidence = final_passport.overall_confidence.model_dump()
    db_passport.revision_count = final_passport.revision_count

    # Persist ledger entries
    for entry in final_passport.ledger:
        db_entry = LedgerEntryModel(
            id=entry.id,
            passport_id=mission_id,
            agent_id=entry.agent_id,
            action=entry.action,
            inputs_summary=entry.inputs_summary,
            outputs_summary=entry.outputs_summary,
            duration_ms=entry.duration_ms,
            tokens_used=entry.tokens_used,
            cost_usd=entry.cost_usd,
            confidence=entry.confidence.model_dump(),
            tool_calls=entry.tool_calls,
            notes=entry.notes,
            timestamp=entry.timestamp,
        )
        db.add(db_entry)

    await db.flush()

    # Fetch updated ledger for response
    ledger_result = await db.execute(
        select(LedgerEntryModel)
        .where(LedgerEntryModel.passport_id == mission_id)
        .order_by(LedgerEntryModel.timestamp)
    )
    ledger_entries = ledger_result.scalars().all()

    return PassportDetailResponse(
        id=db_passport.id,
        tenant_id=db_passport.tenant_id,
        team_id=str(db_passport.team_id),
        status=db_passport.status,
        current_agent=db_passport.current_agent,
        mission_objective=db_passport.mission_objective,
        created_at=db_passport.created_at,
        updated_at=db_passport.updated_at,
        overall_confidence=db_passport.overall_confidence.get("value", 0.0),
        revision_count=db_passport.revision_count,
        artifacts=db_passport.artifacts,
        mission=db_passport.mission_data,
        routing=db_passport.routing,
        context=db_passport.context,
        ledger=[
            {
                "id": str(e.id),
                "timestamp": e.timestamp.isoformat(),
                "agent_id": e.agent_id,
                "action": e.action,
                "inputs_summary": e.inputs_summary,
                "outputs_summary": e.outputs_summary,
                "duration_ms": e.duration_ms,
                "tokens_used": e.tokens_used,
                "cost_usd": e.cost_usd,
                "confidence": e.confidence,
                "tool_calls": e.tool_calls,
                "notes": e.notes,
            }
            for e in ledger_entries
        ],
    )
