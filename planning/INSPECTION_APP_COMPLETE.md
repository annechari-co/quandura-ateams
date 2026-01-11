# Quandura Inspection App - Complete Specification

Consolidated reference for the Safety Inspection Field Application and Safety Team agents.

**Version:** 1.0
**Last Updated:** 2025-01-08

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Context](#business-context)
3. [Field App Specification](#field-app-specification)
4. [Safety Team Agents](#safety-team-agents)
5. [Memory Integration](#memory-integration)
6. [End-to-End Workflow](#end-to-end-workflow)
7. [Data Model](#data-model)
8. [Equipment & Inspection Criteria](#equipment--inspection-criteria)
9. [Report Format](#report-format)
10. [API Endpoints](#api-endpoints)
11. [UI Screens](#ui-screens)
12. [Implementation Plan](#implementation-plan)
13. [Success Metrics](#success-metrics)

---

## Executive Summary

### What We're Building

A mobile-first inspection application that:
- Enables field inspectors to conduct facility safety inspections
- Generates professional PDF reports matching the RiskI format
- Integrates with AI agents for real-time guidance and report generation
- Stores inspection data in organizational memory for precedent matching

### Why This First

1. **Founder Expertise:** Deep knowledge of safety team operations
2. **Market Timing:** Martinez Act (Maryland) requires self-inspection regimes
3. **Revenue Path:** Consulting firm → Risk Management product → TPA disruption
4. **Concrete Artifact:** Tangible, usable tool for real customers
5. **Testing Relationships:** Real county personnel available for field testing

### Scope

**MVP (Phase 2):**
- Facility inspections (walkthrough identifying hazards)
- Dynamic checklist generation based on room inventory
- Finding capture with photos
- PDF report generation
- AI-assisted real-time guidance

**Future:**
- Field inspections (active jobsite operations)
- Offline mode with sync
- AI floor plan processing
- Automated scheduling based on risk profiles

---

## Business Context

### Target Users

| User | Use Case |
|------|----------|
| Safety Officers | Schedule and review inspections |
| Field Inspectors | Conduct inspections via mobile app |
| Risk Managers | Track findings and corrective actions |
| Compliance Officers | Validate regulatory compliance |
| Consultants | Deliver inspection services to clients |

### Roles (RBAC)

| Role | Permissions |
|------|-------------|
| Basic User | Read inspection reports |
| Coordinator | Read + Schedule inspections |
| Compliance Officer | Read + Write + Conduct inspections + Generate reports |
| Admin | Full access + User management + System config |

### Market Context

**Martinez Act (Maryland):** Requires local governments to implement self-inspection regimes. Creates immediate demand for:
- Standardized inspection tools
- Compliance tracking
- Professional report generation

---

## Field App Specification

### Core Concepts

**Two Outputs from Every Inspection:**

```
Room Inventory → Generates Checklist → Inspector Evaluates
                                              ↓
                    ┌─────────────────────────┴─────────────────────────┐
                    ↓                                                   ↓
           ALL Results                                          FAILURES Only
                    ↓                                                   ↓
        Appendix B: Self-Inspection Form                    Table 1: Findings
        (Proof of due diligence)                            (Corrective actions)
```

- **Appendix B** = Complete record of everything inspected (pass and fail)
- **Table 1** = Only items requiring corrective action

### Inspection Workflow

#### 1. Pre-Inspection Setup

```
New Inspection
     ↓
Select Facility (from registry)
     ↓
Enter metadata:
  - Date/Time
  - Inspector name(s)
  - Inspection type (Annual, Follow-up, Complaint-based)
  - Weather conditions
     ↓
Load or Create Floor Plan
```

#### 2. Floor Plan Management

**Initial Setup (First Visit):**
- Upload floor plan image (PDF, PNG, JPG)
- Define room boundaries manually
- Future: AI simplification via Nano Banana

**Interaction:**
- Pan and zoom
- Long-press to access pin menu
- Tap room to enter room inspection mode

#### 3. Room Inventory Cataloging

When entering a room for the first time:

```
Long-press on room → "Catalog Room"
     ↓
Room Details:
  - Name: "Room 102"
  - Description: "Maintenance Shop"
  - Room Type: [Dropdown]
     ↓
Equipment Present: (searchable, multi-select)
  ☑ Fire Extinguisher (qty: 2)
  ☑ Flammables Cabinet (qty: 1)
  ☑ Electrical Panel (qty: 1)
  ☐ Eye Wash Station
  ☐ First Aid Kit
  ☐ AED
  ... (full list in Equipment section)
     ↓
Pin each item on floor plan (optional)
Add photo of item (optional)
```

#### 4. Dynamic Checklist Generation

**Formula:**
```
Checklist = Baseline Items + Room Type Items + Equipment-Specific Items
```

**Baseline Checklist (ALL rooms):**

| Item | Criteria |
|------|----------|
| Egress | Path clear, door operational, signage visible |
| Trip Hazards | Floor clear of cords, debris, uneven surfaces |
| Lighting | Adequate illumination, fixtures secure |
| Ceiling/Walls | No damage, stains, or deterioration |
| Floor Condition | No cracks, holes, or damage |
| Water Damage | No visible leaks, stains, or mold |
| Storage | Items stored safely, not blocking egress |

**Room Type Additions:**

| Room Type | Additional Items |
|-----------|------------------|
| Office | Ergonomics, electrical cord management |
| Kitchen/Break Room | Appliance condition, food storage |
| Restroom | Fixture condition, ADA compliance |
| Mechanical Room | Access restricted, equipment guarding |
| Storage | Weight limits, stacking safety |

#### 5. Conducting the Inspection

```
Select Room on Floor Plan
     ↓
View Generated Checklist
     ↓
For Each Item:
  ├── Pass ✓
  ├── Fail ✗ → Capture Finding
  └── N/A
     ↓
If Fail:
  - Take photo (required)
  - Select priority
  - Add description
  - Add recommendation
  - Link regulatory citation
     ↓
Mark Room Complete → Move to Next Room
```

#### 6. Finding Capture

```
Finding Details:
  - Finding ID: Auto-generated (Site-Location-Year-Seq)
    Example: Fleet-Dayton-2025-06

  - Location: Room name + specific location
    Example: "Room 102 - South wall"

  - Priority:
    ○ High (Immediate) - Life safety
    ○ High (30 days) - Serious violation
    ○ Medium (60 days) - Moderate concern
    ○ Low (90 days) - Minor issue

  - Photo: Required

  - Description: What is wrong
  - Recommendation: How to fix
  - Regulatory Reference: (dropdown)
  - Responsible Party: Who should fix
```

---

## Safety Team Agents

### Team Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   SAFETY TEAM ORCHESTRATOR                       │
│              (Plans inspections, coordinates agents)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Scheduler  │  │  Inspector   │  │   Report     │           │
│  │    Agent     │  │   Assistant  │  │   Generator  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │  Compliance  │  │   Follow-up  │  │  Librarian   │           │
│  │   Checker    │  │   Tracker    │  │ (Knowledge)  │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Descriptions

#### Scheduler Agent
**Role:** Schedule inspections based on risk factors, compliance deadlines, resource availability.

**Outputs:**
- Scheduled inspection assignments
- Calendar notifications
- Deadline alerts

#### Inspector Assistant Agent
**Role:** Real-time guidance during inspections.

**Outputs:**
- Applicable inspection criteria
- Regulatory reference explanations
- Similar past findings for reference

**Integration:** Receives context from app, provides chat-based assistance.

#### Report Generator Agent
**Role:** Generate professional PDF reports from findings.

**Outputs:**
- Executive summary narrative
- Findings table (Table 1)
- Self-inspection form (Appendix B)
- Complete PDF matching RiskI format

#### Compliance Checker Agent
**Role:** Validate inspections meet regulatory requirements.

**Checks:**
- All required equipment types inspected
- Regulatory citations correctly applied
- Priority levels appropriate
- Timeline recommendations valid

#### Follow-up Tracker Agent
**Role:** Track corrective actions, send reminders.

**Timeline Tracking:**

| Priority | Timeline | Check-in Schedule |
|----------|----------|-------------------|
| HIGH_IMMEDIATE | Same day | Daily until resolved |
| HIGH_30_DAYS | 30 days | 14 days, 7 days, 2 days |
| MEDIUM_60_DAYS | 60 days | 30 days, 14 days, 7 days |
| LOW_90_DAYS | 90 days | 45 days, 30 days, 14 days |

#### Librarian Agent
**Role:** Knowledge retrieval for all other agents.

**Retrieval Operations:**
- Find applicable criteria for equipment type
- Get regulatory citations for finding priority
- Retrieve similar past findings
- Look up facility inspection history

---

## Memory Integration

### Entity to Memory Layer Mapping

| App Entity | Memory Layer | Memory Type |
|------------|--------------|-------------|
| EquipmentType | Operational | `standard` |
| InspectionCriteria | Operational | `checklist` |
| Facility | Entity | `facility` |
| Room | Entity | `room` |
| RoomInventoryItem | Entity | `equipment` |
| Inspection | Event | `inspection` |
| Finding | Event | `finding` |
| CorrectiveAction | Event | `corrective_action` |

### Automatic Tag Generation

**Finding Tags (Critical for Precedent Matching):**
```python
tags = [
    f"facility:{finding.facility_id}",
    f"room:{finding.room_id}",
    f"priority:{finding.priority}",           # "priority:high_30"
    f"equipment_type:{finding.equipment_type}", # "equipment_type:fire_extinguisher"
    f"status:{finding.status}",               # "status:open"
    f"regulation:{finding.regulatory_ref}",   # "regulation:nfpa-10"
]
```

### Multi-Resolution Content

| Resolution | Size | Use Case |
|------------|------|----------|
| Micro | ~12 tokens | Listing, scanning |
| Summary | ~60-70 tokens | Reasoning, context |
| Full | Complete | Detail view |

**Finding Example:**
```
micro: "Fire ext|High-30|Pressure gauge red|Room 102|NFPA 10"

summary: "Fire extinguisher in Room 102 (Maintenance Shop, south wall)
has pressure gauge in red zone. Priority: High (30 days) per NFPA 10.
Recommendation: Service or replace. Similar findings at facility: 2 previous."
```

### Precedent Matching

When a new Finding is stored:
1. Find similar past findings (same equipment type + criteria)
2. Create SIMILAR_TO relationships
3. Store resolution patterns for future reference

This enables: "What happened when we found this before?"

---

## End-to-End Workflow

### Standard Inspection Flow

```
1. Scheduler → Identifies due inspections, assigns inspector
       │
       ▼
2. Inspector → Conducts inspection via Field App
       │
       │ ← Inspector Assistant provides real-time support
       │
       ▼
3. Report Generator → Creates report from findings
       │
       ▼
4. Compliance Checker → Validates completeness
       │
       ▼
5. Report finalized → PDF delivered to facility
       │
       ▼
6. Follow-up Tracker → Monitors corrective actions
```

### Job Lifecycle States

```
INTAKE → PARSING → ANALYSIS → LEGAL_REVIEW → DRAFTING → REVIEW
    → SIGNOFF → TRANSMITTED → INVOICED → PAYMENT_PENDING
    → PAYMENT_RECEIVED → RECONCILED → CLOSED
```

**Exception paths:**
- Any → BLOCKED (waiting on dependency)
- Any → ESCALATED (needs human intervention)
- REVIEW → REVISION (issues found)
- SIGNOFF → REJECTED (human rejected)

---

## Data Model

### Core Entities

```
Facility
  - id: UUID
  - tenant_id: UUID
  - name: string
  - address: string
  - floor_plans: FloorPlan[]
  - rooms: Room[]

FloorPlan
  - id: UUID
  - facility_id: UUID
  - name: string (e.g., "Floor 1")
  - image_url: string
  - rooms: Room[]

Room
  - id: UUID
  - floor_plan_id: UUID
  - name: string
  - description: string
  - room_type: RoomType
  - boundary_coords: JSON
  - inventory: RoomInventoryItem[]

RoomInventoryItem
  - id: UUID
  - room_id: UUID
  - equipment_type_id: UUID
  - quantity: int
  - pin_location: JSON
  - photo_url: string

Inspection
  - id: UUID
  - facility_id: UUID
  - inspector_id: UUID
  - inspection_type: InspectionType
  - status: InspectionStatus
  - scheduled_date: date
  - completed_date: date
  - checklist_results: ChecklistResult[]
  - findings: Finding[]

Finding
  - id: UUID
  - inspection_id: UUID
  - finding_id: string (e.g., "Fleet-Dayton-2025-06")
  - room_id: UUID
  - priority: Priority
  - description: string
  - recommendation: string
  - regulatory_reference: string
  - responsible_party: ResponsibleParty
  - photo_urls: string[]
  - status: FindingStatus
```

### Enums

```
RoomType: GENERAL_SPACE, OFFICE, KITCHEN_BREAK_ROOM, RESTROOM,
          MECHANICAL_ROOM, STORAGE, WAREHOUSE, LABORATORY, CUSTOM

Priority: HIGH_IMMEDIATE, HIGH_30_DAYS, MEDIUM_60_DAYS, LOW_90_DAYS

InspectionType: ANNUAL, FOLLOW_UP, COMPLAINT_BASED, SPECIAL_REQUEST, NEW_FACILITY

FindingStatus: OPEN, IN_PROGRESS, PENDING_VERIFICATION, CLOSED

ResponsibleParty: LOCATION_STAFF, FACILITIES_MANAGEMENT, IT_TECHNOLOGY,
                  EXTERNAL_CONTRACTOR, OTHER
```

### Relationships

```
Facility 1──∞ FloorPlan
FloorPlan 1──∞ Room
Room ∞──∞ EquipmentType (via RoomInventoryItem)
EquipmentType 1──∞ InspectionCriteria
Facility 1──∞ Inspection
Inspection 1──∞ Finding
```

---

## Equipment & Inspection Criteria

### Fire Safety

**Fire Extinguisher**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Pressure gauge in green zone | High | NFPA 10, 7.2.1.2 |
| Inspection tag current (< 12 months) | High | NFPA 10, 7.2.2 |
| Mounted at proper height (3.5-5 ft) | Medium | NFPA 10, 6.1.3 |
| Unobstructed (3 ft clearance) | High | NFPA 10, 6.1.3.8 |
| No visible damage or corrosion | High | NFPA 10, 7.2.1.1 |

**Exit Sign**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Illuminated and visible | High | NFPA 101, 7.10 |
| Backup battery functional | High | NFPA 101, 7.10.4 |

**Smoke Detector**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Test button responsive | High | NFPA 72, 14.4.5 |
| Not painted over | High | NFPA 72, 14.4.5.3 |

### Electrical

**Electrical Panel**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| 36" clearance maintained | High | NFPA 70, 110.26 |
| All breakers labeled | Medium | NFPA 70, 408.4 |
| Cover secured | High | NFPA 70, 408.38 |
| No exposed wiring | High | NFPA 70, 110.12 |

**Extension Cord**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Not daisy-chained | High | OSHA 1910.334(a)(1) |
| Not used as permanent wiring | High | OSHA 1910.334(a)(1) |

### Chemical Storage

**Flammables Cabinet**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Self-closing doors functional | High | NFPA 30, 9.5.3 |
| Properly grounded | High | NFPA 30, 9.5.4 |
| No incompatible materials | High | OSHA 1910.106(d)(3) |

**Compressed Gas Cylinders**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Secured upright (chain/strap) | High | OSHA 1910.253(b)(2) |
| Caps in place when not in use | High | OSHA 1910.253(b)(2) |
| Proper segregation (O2 from fuel) | High | OSHA 1910.253(b)(4) |

### Emergency Equipment

**Eye Wash Station**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Weekly activation test logged | High | ANSI Z358.1 |
| Water flow adequate | High | ANSI Z358.1, 4.5 |
| Within 10 seconds of hazard | High | ANSI Z358.1, 4.5.2 |

**AED**
| Criteria | Priority | Regulatory Ref |
|----------|----------|----------------|
| Status indicator shows ready | High | AHA Guidelines |
| Pads not expired | High | AHA Guidelines |
| Battery status OK | High | AHA Guidelines |

---

## Report Format

### Report Structure (Matching RiskI Format)

1. **Cover Page**
   - Facility photo
   - Facility name and address
   - Inspection date
   - Inspector name

2. **Executive Summary**
   - Priority breakdown table
   - Key concerns summary

3. **Table of Contents**

4. **Introduction**
   - Purpose and scope
   - Site information
   - Inspection attendees

5. **Summary of Findings**
   - **Table 1: Findings** (failures only)
   - Finding ID, Location, Priority, Citations, Description, Recommendation

6. **Floor Plan with Findings**
   - **Figure 3: Findings Map**
   - Color-coded pins by priority

7. **Corrective Actions by Responsible Party**

8. **Conclusion**
   - Next steps
   - Re-inspection date
   - 14-day check-in commitment

9. **References**

10. **Appendix A: Photograph Log**

11. **Appendix B: Self-Inspection Form**
    - Room-by-room checklist results
    - ALL items (pass and fail)

12. **Appendix C: Supporting Documents**

---

## API Endpoints

### Facilities
- `GET /facilities` - List facilities for tenant
- `POST /facilities` - Create facility
- `GET /facilities/{id}` - Get facility with floor plans
- `PUT /facilities/{id}` - Update facility

### Floor Plans
- `POST /facilities/{id}/floor-plans` - Upload floor plan
- `GET /facilities/{id}/floor-plans/{fp_id}` - Get floor plan with rooms
- `PUT /floor-plans/{id}/rooms` - Update room boundaries

### Room Inventory
- `GET /rooms/{id}` - Get room with inventory
- `POST /rooms/{id}/inventory` - Add equipment to room
- `PUT /rooms/{id}/inventory/{item_id}` - Update inventory item

### Inspections
- `POST /inspections` - Create new inspection
- `GET /inspections/{id}` - Get inspection with results
- `POST /inspections/{id}/start` - Begin inspection
- `POST /inspections/{id}/complete` - Mark complete

### Checklist
- `GET /inspections/{id}/rooms/{room_id}/checklist` - Get generated checklist
- `POST /inspections/{id}/results` - Submit checklist results

### Findings
- `POST /inspections/{id}/findings` - Create finding
- `GET /inspections/{id}/findings` - List findings
- `PUT /findings/{id}` - Update finding
- `POST /findings/{id}/photos` - Upload photo

### Reports
- `GET /inspections/{id}/report` - Generate PDF report
- `GET /inspections/{id}/report/preview` - Preview report data

---

## UI Screens

### Mobile (Inspector)

1. **Dashboard** - Upcoming, in-progress, recent inspections
2. **Inspection Detail** - Facility info, progress indicator
3. **Floor Plan View** - Interactive map, room status, finding pins
4. **Room Inspection** - Checklist, pass/fail buttons, photo capture
5. **Finding Capture** - Photo, priority, description, recommendation
6. **Room Inventory** - Equipment selection, quantity, pin placement
7. **Inspection Review** - Summary, generate report button

### Web (Admin/Coordinator)

1. **Facility Management** - List, floor plan upload, room definition
2. **Inspection Scheduling** - Calendar, assign inspectors
3. **Report Viewer** - Generated reports, export options
4. **Finding Tracking** - Open findings dashboard, status updates

---

## Implementation Plan

### Phase 2 Deliverables

| Component | Description | Dependencies |
|-----------|-------------|--------------|
| Inspection App Backend | Facility, Room, Equipment, Inspection, Finding models + API | Phase 1 complete |
| Safety Team Agents | 6 agents + orchestrator | Librarian, Memory system |
| Memory Integration | Auto-tagging, relationships, precedent matching | Memory storage layer |
| Inspection App Frontend | React PWA for mobile | Backend API |
| PDF Report Generation | Match RiskI format | All above |

### Build Sequence

```
Phase 1 (Core Engine) must complete first:
├── Memory storage (PostgreSQL)
├── Embeddings (ChromaDB)
├── Librarian agent
├── Team templates

Then Phase 2 (Safety Team):
├── Week 1-2: Inspection backend models + API
├── Week 3-4: Safety Team agents
├── Week 5-6: Memory integration
├── Week 7-8: Frontend (PWA)
├── Week 9-10: PDF generation + testing
```

### Parallel Work (Can Start During Phase 1)

- Inspection App data model (no agent deps)
- Facility/Room/Equipment CRUD
- Basic inspection workflow (non-AI)
- PDF report template design

### Must Wait for Phase 1

- Safety Team agents
- Inspector Assistant (needs Librarian)
- Memory integration (needs storage layer)
- Precedent matching

---

## Success Metrics

### For Consulting Firm

| Metric | Target |
|--------|--------|
| Time to complete inspection | 50% reduction vs manual |
| Report generation time | < 1 hour after inspection |
| Report quality score | > 4.5/5 from clients |
| Compliance gap detection | 100% of required items checked |
| Follow-up completion rate | > 90% within deadline |

### For Platform Validation

| Metric | Target |
|--------|--------|
| Agent coordination accuracy | > 95% correct routing |
| Passport state persistence | 100% across restarts |
| Memory retrieval relevance | > 80% useful results |
| Field usability | < 5 complaints per 100 inspections |

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Mobile app dev requires native expertise | Start with PWA, evaluate native later |
| Offline sync complexity | MVP requires connectivity, offline in v2 |
| Field conditions reveal UX issues | Early testing with real inspectors |
| Regulatory requirements vary by jurisdiction | Start with Maryland (Martinez Act) |

---

## Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Field App Spec | `planning/field-app/FIELD_APP_SPEC.md` | Complete technical specification |
| Memory Integration | `planning/field-app/MEMORY_INTEGRATION.md` | Data flow to memory system |
| Safety Team | `planning/teams/SAFETY_TEAM.md` | Agent specifications |
| OHS Scenario | `planning/research/SCENARIO_OHS_INSPECTION.md` | Full lifecycle workflow |
| Example Report | `planning/field-app/Risk Inspection Report Dayton_Fleet V3.0_signed.pdf` | Target format |
| Flow Diagram | `planning/field-app/Quandura Inspection App Flow.pptx` | Visual workflow |

---

*This document consolidates all inspection app specifications for stakeholder reference.*

*Version: 1.0*
*Created: 2025-01-08*
