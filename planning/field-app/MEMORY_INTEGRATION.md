# Inspection App Memory Integration

How data from the Field Inspection App integrates with the Quandura organizational memory system.

## Overview

The Field App captures structured inspection data. This document specifies:
1. How app entities map to memory layers
2. Automatic tag generation rules
3. Relationship creation between memory nodes
4. Multi-resolution content generation
5. Precedent matching for similar findings

---

## Entity to Memory Layer Mapping

### From App Data Model to Memory Layers

| App Entity | Memory Layer | Memory Type | Rationale |
|------------|--------------|-------------|-----------|
| EquipmentType | Operational | `standard` | Defines inspection requirements |
| InspectionCriteria | Operational | `checklist` | Rules applied during inspections |
| Facility | Entity | `facility` | Persistent object tracked over time |
| Room | Entity | `room` | Persistent sub-entity of facility |
| RoomInventoryItem | Entity | `equipment` | Trackable equipment instances |
| Inspection | Event | `inspection` | Thing that happened with outcome |
| ChecklistResult | Event | `checklist_result` | Sub-event within inspection |
| Finding | Event | `finding` | Decision point with reasoning |
| CorrectiveAction | Event | `corrective_action` | Follow-up event |

### Layer Hierarchy

```
Strategic Layer (rarely from app - manual configuration)
├── Goal: "Zero workplace injuries"
├── KPI: "Inspection completion rate"
│
Operational Layer (seeded from equipment types)
├── Standard: "NFPA 10 Fire Extinguisher Requirements"
├── Checklist: Equipment-specific inspection criteria
│
Entity Layer (created from facilities/rooms/inventory)
├── Facility: "entity.facility.dayton-fleet"
│   ├── Room: "entity.room.dayton-fleet.room-102"
│   └── Equipment: "entity.equipment.dayton-fleet.room-102.fire-ext-1"
│
Event Layer (created during/after inspections)
├── Inspection: "event.inspection.dayton-fleet.2025-01-15"
│   ├── Finding: "event.finding.fleet-dayton-2025-01"
│   └── CorrectiveAction: "event.corrective.fleet-dayton-2025-01.resolved"
```

---

## Automatic Tag Generation

Tags are generated automatically when data enters the memory system.

### Facility Tags

When a Facility is stored:
```python
tags = [
    f"department:{facility.department}",      # "department:fleet"
    f"risk_level:{facility.risk_level}",      # "risk_level:medium"
    f"facility_type:{facility.type}",         # "facility_type:maintenance"
    f"jurisdiction:{facility.jurisdiction}",  # "jurisdiction:montgomery-county"
]
```

### Room Tags

When a Room is stored:
```python
tags = [
    f"facility:{room.facility_id}",           # Links to parent
    f"room_type:{room.room_type}",            # "room_type:mechanical_room"
    f"floor:{room.floor_plan.name}",          # "floor:floor-1"
]
# Add equipment category tags based on inventory
for item in room.inventory:
    tags.append(f"has_equipment:{item.equipment_type.category}")
# Results in: "has_equipment:fire_safety", "has_equipment:electrical"
```

### Inspection Tags

When an Inspection is stored:
```python
tags = [
    f"facility:{inspection.facility_id}",
    f"inspection_type:{inspection.inspection_type}",  # "inspection_type:annual"
    f"inspector:{inspection.inspector_id}",
    f"status:{inspection.status}",
    f"year:{inspection.completed_date.year}",
    f"month:{inspection.completed_date.month:02d}",
]
```

### Finding Tags (Critical for Precedent Matching)

When a Finding is stored:
```python
tags = [
    f"facility:{finding.inspection.facility_id}",
    f"room:{finding.room_id}",
    f"priority:{finding.priority}",            # "priority:high_30"
    f"equipment_type:{finding.equipment_type}", # "equipment_type:fire_extinguisher"
    f"equipment_category:{finding.category}",  # "equipment_category:fire_safety"
    f"status:{finding.status}",                # "status:open"
    f"responsible:{finding.responsible_party}", # "responsible:facilities_management"
    f"criteria:{finding.criteria_id}",         # Links to specific failed criteria
]
# Extract regulatory reference as tag
if finding.regulatory_reference:
    tags.append(f"regulation:{finding.regulatory_ref.code}")  # "regulation:nfpa-10"
```

### Corrective Action Tags

When a CorrectiveAction is stored:
```python
tags = [
    f"finding:{corrective.finding_id}",
    f"facility:{corrective.facility_id}",
    f"status:{corrective.status}",             # "status:completed"
    f"responsible:{corrective.responsible_party}",
    f"days_to_resolve:{corrective.days_open}",  # "days_to_resolve:14"
    f"on_time:{corrective.resolved_by_deadline}",  # "on_time:yes"
]
```

---

## Multi-Resolution Content Generation

Each memory node has three resolutions generated automatically.

### Facility Example

```python
{
    "symbol": "entity.facility.dayton-fleet",
    "type": "facility",
    "tags": ["department:fleet", "risk_level:medium", "jurisdiction:montgomery-county"],

    "micro": "Dayton Fleet|Fleet Maint|Medium|15 rooms|47 equip",  # ~12 tokens

    "summary": """Fleet maintenance facility at 123 Industrial Dr, Dayton.
        15 rooms across 2 floors with 47 tracked equipment items.
        Risk level: Medium (vehicle maintenance, flammables storage).
        Last inspection: 2024-06-15 (Annual).
        Historical findings: 23 total (5 high, 10 medium, 8 low), all resolved.""",  # ~60 tokens

    "full": {
        "id": "uuid-here",
        "name": "Dayton Fleet Maintenance",
        "address": "123 Industrial Dr, Dayton, OH 45402",
        "department": "fleet",
        "risk_level": "medium",
        "floor_plans": [...],
        "rooms": [...],
        "inspection_history": [...],
        # Complete record with all metadata
    }
}
```

### Finding Example

```python
{
    "symbol": "event.finding.fleet-dayton-2025-01",
    "type": "finding",
    "tags": [
        "facility:dayton-fleet",
        "room:room-102",
        "priority:high_30",
        "equipment_type:fire_extinguisher",
        "status:open",
        "regulation:nfpa-10"
    ],

    "micro": "Fire ext|High-30|Pressure gauge red|Room 102|NFPA 10",  # ~12 tokens

    "summary": """Fire extinguisher in Room 102 (Maintenance Shop, south wall)
        has pressure gauge in red zone, indicating discharge or leak.
        Priority: High (30 days) per NFPA 10, 7.2.1.2.
        Recommendation: Service or replace extinguisher immediately.
        Responsible: Facilities Management.
        Similar findings at this facility: 2 previous (both resolved <14 days).""",  # ~70 tokens

    "full": {
        "id": "uuid-here",
        "finding_id": "Fleet-Dayton-2025-01",
        "inspection_id": "...",
        "room_id": "room-102",
        "location_detail": "South wall near exit door",
        "priority": "HIGH_30_DAYS",
        "description": "Fire extinguisher pressure gauge in red zone",
        "recommendation": "Service or replace fire extinguisher",
        "regulatory_reference": "NFPA 10, 7.2.1.2",
        "responsible_party": "FACILITIES_MANAGEMENT",
        "photo_urls": ["https://..."],
        "created_at": "2025-01-15T14:32:00Z",
        # Complete record
    }
}
```

### Micro Format Guidelines

| Entity Type | Micro Format | Example |
|-------------|--------------|---------|
| Facility | `{name}\|{type}\|{risk}\|{rooms} rooms\|{equip} equip` | `Dayton Fleet\|Maint\|Medium\|15 rooms\|47 equip` |
| Room | `{name}\|{type}\|{equip_count} items` | `Room 102\|Mechanical\|8 items` |
| Inspection | `{facility}\|{type}\|{date}\|{findings} findings` | `Dayton Fleet\|Annual\|2025-01\|12 findings` |
| Finding | `{equip}\|{priority}\|{issue}\|{location}\|{reg}` | `Fire ext\|High-30\|Pressure red\|Room 102\|NFPA 10` |
| Corrective | `{finding}\|{status}\|{days} days\|{resolver}` | `Fleet-2025-01\|Closed\|14 days\|Facilities` |

---

## Relationship Generation

Relationships are created automatically when data is stored.

### Cross-Layer Relationships

```python
# Finding → Equipment (what failed)
INVOLVES: finding → equipment

# Finding → Criteria (which rule was violated)
APPLIES: finding → checklist_criteria

# Finding → Standard (regulatory context)
ALIGNED_WITH: finding → standard

# Inspection → Facility
INVOLVES: inspection → facility

# Corrective Action → Finding
RESOLVES: corrective_action → finding
```

### Within-Layer Relationships

```python
# Similar findings (for precedent matching)
SIMILAR_TO: finding → finding  # Based on equipment_type + criteria match

# Supersedes (for updated policies)
SUPERSEDES: checklist_v2 → checklist_v1

# Caused (reasoning chain)
CAUSED: inspection → finding  # This inspection caused this finding to be recorded
```

### Automatic Similarity Detection

When a new Finding is stored, automatically find similar past findings:

```python
async def find_similar_findings(new_finding: Finding) -> list[MemoryNode]:
    """Find similar past findings for precedent context."""

    # Primary match: same equipment type + same criteria
    primary_matches = await memory.query(
        layer=MemoryLayer.EVENT,
        type="finding",
        tags={
            "equipment_type": new_finding.equipment_type,
            "criteria": new_finding.criteria_id,
        },
        resolution="micro",
        limit=20,
    )

    # Secondary match: same equipment type + same priority (broader)
    secondary_matches = await memory.query(
        layer=MemoryLayer.EVENT,
        type="finding",
        tags={
            "equipment_type": new_finding.equipment_type,
            "priority": new_finding.priority,
        },
        exclude_ids=[m.id for m in primary_matches],
        resolution="micro",
        limit=10,
    )

    # Create SIMILAR_TO relationships for top matches
    for match in primary_matches[:5]:
        await memory.create_relationship(
            from_symbol=new_finding.symbol,
            to_symbol=match.symbol,
            relation_type=RelationType.SIMILAR_TO,
            metadata={"match_type": "primary", "score": 0.9}
        )

    return primary_matches + secondary_matches
```

---

## Data Flow: App → Memory

### On Facility Creation

```python
async def sync_facility_to_memory(facility: Facility):
    """Sync new/updated facility to memory system."""

    node = MemoryNode(
        symbol=f"entity.facility.{slugify(facility.name)}",
        layer=MemoryLayer.ENTITY,
        type="facility",
        tags=generate_facility_tags(facility),
        micro=generate_facility_micro(facility),
        summary=generate_facility_summary(facility),
        full=facility.dict(),
    )
    await memory.store(node)

    # Sync rooms
    for room in facility.rooms:
        await sync_room_to_memory(room, facility)
```

### On Inspection Completion

```python
async def sync_inspection_to_memory(inspection: Inspection):
    """Sync completed inspection and all findings to memory."""

    # Store inspection event
    inspection_node = MemoryNode(
        symbol=f"event.inspection.{inspection.facility.slug}.{inspection.date}",
        layer=MemoryLayer.EVENT,
        type="inspection",
        tags=generate_inspection_tags(inspection),
        micro=generate_inspection_micro(inspection),
        summary=generate_inspection_summary(inspection),
        full=inspection.dict(),
    )
    await memory.store(inspection_node)

    # Store each finding
    for finding in inspection.findings:
        finding_node = await sync_finding_to_memory(finding, inspection)

        # Create relationships
        await memory.create_relationship(
            from_symbol=inspection_node.symbol,
            to_symbol=finding_node.symbol,
            relation_type=RelationType.CAUSED,
        )

        # Find and link similar findings
        await find_similar_findings(finding)

    # Update facility memory with latest inspection info
    await update_facility_inspection_history(inspection.facility)
```

### On Finding Status Change

```python
async def sync_finding_status_change(finding: Finding, old_status: str):
    """Update memory when finding status changes."""

    # Update tags
    finding_node = await memory.retrieve(finding.symbol)
    finding_node.tags = [t for t in finding_node.tags if not t.startswith("status:")]
    finding_node.tags.append(f"status:{finding.status}")

    # Regenerate summary to reflect status
    finding_node.summary = generate_finding_summary(finding)

    await memory.update(finding_node)

    # If closed, create corrective action record
    if finding.status == "CLOSED" and old_status != "CLOSED":
        await create_corrective_action_memory(finding)
```

---

## Precedent Retrieval for Inspector Assistant

When an inspector asks for help or context:

```python
async def get_inspector_context(
    facility_id: str,
    room_id: str,
    equipment_type: str,
    criteria_id: str | None = None,
) -> InspectorContext:
    """Build context for Inspector Assistant agent."""

    context = InspectorContext()

    # 1. Get facility history (summary resolution)
    context.facility = await memory.retrieve(
        f"entity.facility.{facility_id}",
        resolution="summary",
    )

    # 2. Get room inventory (micro for list)
    context.room = await memory.retrieve(
        f"entity.room.{facility_id}.{room_id}",
        resolution="summary",
    )

    # 3. Get applicable criteria (full - need complete rules)
    context.criteria = await memory.query(
        layer=MemoryLayer.OPERATIONAL,
        type="checklist",
        tags={"equipment_type": equipment_type},
        resolution="full",
    )

    # 4. Get similar past findings at this facility (micro for scan)
    context.facility_findings = await memory.query(
        layer=MemoryLayer.EVENT,
        type="finding",
        tags={"facility": facility_id, "equipment_type": equipment_type},
        resolution="micro",
        limit=10,
    )

    # 5. Get similar findings anywhere (for precedent)
    context.precedents = await memory.query(
        layer=MemoryLayer.EVENT,
        type="finding",
        tags={"equipment_type": equipment_type, "criteria": criteria_id} if criteria_id else {"equipment_type": equipment_type},
        resolution="micro",
        limit=20,
    )

    # 6. Expand top 3 precedents to summary
    if context.precedents:
        context.precedent_details = await memory.retrieve(
            [p.symbol for p in context.precedents[:3]],
            resolution="summary",
        )

        # Get their outcomes (corrective actions)
        for precedent in context.precedent_details:
            outcomes = await memory.traverse(
                precedent.symbol,
                relation_types=[RelationType.RESOLVES],  # inverse lookup
                direction="incoming",
            )
            precedent.outcomes = outcomes

    return context
```

---

## Report Generator Memory Usage

When generating a report, the Report Generator agent uses memory to:

1. **Generate Executive Summary** - Uses facility history and finding patterns
2. **Add Similar Past Findings** - References precedents for context
3. **Calculate Risk Trends** - Compares to historical inspections

```python
async def build_report_context(inspection: Inspection) -> ReportContext:
    """Build context for report generation."""

    # Get all historical inspections at this facility
    historical = await memory.query(
        layer=MemoryLayer.EVENT,
        type="inspection",
        tags={"facility": inspection.facility_id},
        resolution="summary",
        sort_by="date",
        limit=10,
    )

    # Calculate trend (findings increasing or decreasing?)
    trend = calculate_finding_trend(historical, inspection)

    # Find systemic issues (same finding type recurring)
    systemic = await find_recurring_findings(
        facility_id=inspection.facility_id,
        current_findings=inspection.findings,
    )

    return ReportContext(
        historical_inspections=historical,
        finding_trend=trend,
        systemic_issues=systemic,
    )
```

---

## Memory Consolidation for Safety Data

Periodic consolidation (nightly) for safety team memory:

```python
async def consolidate_safety_memory():
    """Nightly consolidation for safety team memory."""

    # 1. Update facility risk scores based on finding patterns
    facilities = await memory.query(
        layer=MemoryLayer.ENTITY,
        type="facility",
    )
    for facility in facilities:
        new_risk = await calculate_facility_risk(facility.symbol)
        if new_risk != facility.get_tag("risk_level"):
            facility.tags = update_tag(facility.tags, "risk_level", new_risk)
            await memory.update(facility)

    # 2. Decay old finding salience (closed findings from >1 year ago)
    old_findings = await memory.query(
        layer=MemoryLayer.EVENT,
        type="finding",
        tags={"status": "closed"},
        min_age_days=365,
    )
    for finding in old_findings:
        finding.salience *= 0.8  # Decay by 20%
        await memory.update(finding)

    # 3. Boost findings with systemic patterns
    systemic = await find_systemic_findings()
    for finding in systemic:
        finding.salience = min(1.0, finding.salience + 0.1)
        await memory.update(finding)
```

---

## Summary

Key integration points:

1. **Automatic Tag Generation** - Every entity gets structured tags for fast filtering
2. **Multi-Resolution Content** - Micro for scanning, summary for reasoning, full for detail
3. **Relationship Creation** - INVOLVES, APPLIES, SIMILAR_TO, CAUSED built automatically
4. **Precedent Matching** - Similar findings linked on storage for future reference
5. **Context Assembly** - Inspector Assistant and Report Generator use memory queries

This enables:
- "Show me all fire extinguisher findings at Fleet facilities" → tag query
- "What happened when we found this before?" → SIMILAR_TO traversal
- "Is this facility getting better or worse?" → historical inspection query
- "What's the typical resolution time for high priority findings?" → aggregate query

---

*Version: 1.0*
*Created: 2025-01-06*
*Status: Integration specification for Field App ↔ Memory System*
