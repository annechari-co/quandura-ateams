# Safety Team Specification

## Overview

**Team Type:** Safety Team (Risk Management)
**Deployment Status:** First real-world deployment target
**Market Opportunity:** Martinez Act (Maryland) creates immediate demand for self-inspection regimes

This team powers the inspection consulting firm that will generate initial revenue. The founder has deep domain expertise in running safety teams and knows the micro-processes intimately.

**Related Documents:**
- `planning/field-app/FIELD_APP_SPEC.md` - Complete inspection app specification (data model, workflows, equipment criteria)
- `planning/field-app/MEMORY_INTEGRATION.md` - How app data flows into memory system (tags, relationships, precedents)
- `planning/field-app/Risk Inspection Report Dayton_Fleet V3.0_signed.pdf` - Example report format

---

## Business Context

### Why This Team First

1. **Founder Expertise:** Deep knowledge of safety team operations, not just theory
2. **Testing Relationships:** Real county personnel available to test in field conditions
3. **Market Timing:** Martinez Act requires Maryland local governments to implement self-inspection
4. **Revenue Path:** Consulting firm → Risk Management product → TPA disruption
5. **Concrete Artifact:** Inspection App provides tangible, usable tool

### Target Users

- Safety Officers at county governments
- Risk Management staff
- Third-party inspection consultants
- Field inspectors using mobile devices

---

## Agent Architecture

### Team Structure

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

#### Safety Team Orchestrator
**Role:** Coordinate all safety team activities, route requests to appropriate specialists.

**Receives:**
- Inspection requests from users
- Status queries
- Report generation requests
- Follow-up inquiries

**Routes to:**
- Scheduler Agent for scheduling operations
- Inspector Assistant for field support
- Report Generator for document creation
- Compliance Checker for validation
- Follow-up Tracker for corrective action status

#### Scheduler Agent
**Role:** Schedule inspections based on risk factors, compliance deadlines, and resource availability.

**Inputs:**
- Facility list with risk profiles
- Inspector availability calendar
- Regulatory compliance deadlines (annual inspections, follow-up dates)
- Inspection history

**Outputs:**
- Scheduled inspection assignments
- Calendar notifications
- Deadline alerts

**Tools:**
- Calendar API integration
- Facility database queries
- Risk scoring calculator

#### Inspector Assistant Agent
**Role:** Support field inspectors during inspections with real-time guidance.

**Inputs:**
- Current room and equipment context
- Inspector questions about criteria
- Photo/finding capture requests
- Regulatory citation queries

**Outputs:**
- Applicable inspection criteria for current context
- Regulatory reference explanations
- Checklist completion guidance
- Similar past findings for reference

**Tools:**
- Memory queries (criteria, precedents)
- Equipment type lookup
- Regulatory citation database

**Integration with Inspection App:**
- Receives context from app (facility, room, equipment being inspected)
- Provides real-time assistance via chat interface
- Does NOT replace app workflow - augments it

#### Report Generator Agent
**Role:** Generate professional inspection reports from captured findings.

**Inputs:**
- Completed inspection data
- Finding photos and descriptions
- Checklist results (pass/fail/NA)
- Facility and attendee information

**Outputs:**
- PDF report matching RiskI format (see `FIELD_APP_SPEC.md` Report Structure)
- Executive summary narrative
- Findings table (Table 1)
- Self-inspection form (Appendix B)

**Report Sections (automated):**
1. Cover Page with facility photo
2. Executive Summary with priority breakdown
3. Table of Contents
4. Introduction and scope
5. Summary of Findings (Table 1 - failures only)
6. Floor Plan with color-coded pins
7. Corrective Actions by responsible party
8. Conclusion with next steps
9. References
10. Appendix A: Photo log
11. Appendix B: Complete checklist results
12. Appendix C: Supporting documents

#### Compliance Checker Agent
**Role:** Verify inspections meet regulatory requirements before report finalization.

**Inputs:**
- Draft inspection report
- Facility type and applicable regulations
- Inspection checklist coverage

**Outputs:**
- Validation pass/fail
- Missing inspection items
- Regulatory gap warnings
- Recommendations for additional checks

**Checks:**
- All required equipment types inspected for room type
- Regulatory citations correctly applied
- Priority levels appropriate for finding severity
- Timeline recommendations match regulatory requirements

#### Follow-up Tracker Agent
**Role:** Track corrective actions, send reminders, escalate overdue items.

**Inputs:**
- Open findings with assigned responsible parties
- Corrective action deadlines
- Status updates from facility staff

**Outputs:**
- 14-day check-in reminders
- Deadline approaching alerts
- Overdue escalation notices
- Corrective action completion reports

**Timeline Tracking (from priority):**
| Priority | Timeline | Check-in Schedule |
|----------|----------|-------------------|
| HIGH_IMMEDIATE | Same day | Daily until resolved |
| HIGH_30_DAYS | 30 days | 14 days, 7 days, 2 days |
| MEDIUM_60_DAYS | 60 days | 30 days, 14 days, 7 days |
| LOW_90_DAYS | 90 days | 45 days, 30 days, 14 days |

#### Librarian Agent
**Role:** Maintain inspection knowledge base and retrieve relevant context for other agents.

**Memory Types Stored:**

| Layer | Types | Examples |
|-------|-------|----------|
| Strategic | Goal, KPI | "Zero workplace injuries", "Inspection completion rate" |
| Operational | Standard, Checklist, Protocol | OSHA requirements, NFPA citations, inspection procedures |
| Entity | Facility, Equipment, Hazard | Building records, equipment inventory, known hazard history |
| Event | Inspection, Finding, CorrectiveAction | Past inspections, historical findings, resolution patterns |

**Retrieval Operations:**
- Find applicable criteria for equipment type
- Get regulatory citations for finding priority
- Retrieve similar past findings for reference
- Look up facility inspection history

---

## Inspection App Integration

The Field App is a separate mobile application that field inspectors use directly. The Safety Team agents augment the app experience but do not replace it.

**App Responsibilities (see `FIELD_APP_SPEC.md`):**
- Floor plan management and room navigation
- Room inventory cataloging
- Dynamic checklist generation
- Finding capture with photos
- Report PDF generation

**Agent Responsibilities:**
- Real-time guidance during inspections (via Inspector Assistant)
- Report narrative generation (via Report Generator)
- Compliance validation (via Compliance Checker)
- Follow-up tracking (via Follow-up Tracker)
- Knowledge retrieval (via Librarian)

**Integration Points:**
1. Inspector can ask questions via chat → routed to Inspector Assistant
2. Inspection complete → triggers Report Generator for narrative sections
3. Report draft ready → Compliance Checker validates before finalization
4. Findings saved → Follow-up Tracker begins timeline monitoring

---

## Workflows

### Standard Inspection Workflow

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

### Hazard Response Workflow

```
Inspector flags HIGH_IMMEDIATE finding
       │
       ▼
Immediate notification to:
  - Facility manager
  - Risk management
  - Safety officer
       │
       ▼
Follow-up Tracker → Daily check-ins until resolved
       │
       ▼
Resolution verified → Finding closed
```

### Compliance Deadline Workflow

```
Scheduler detects approaching deadline (annual inspection due)
       │
       ▼
14-day warning → Coordinator notified
       │
       ▼
7-day warning → Escalation to Risk Manager
       │
       ▼
Inspection scheduled and completed
       │
       ▼
Compliance requirement satisfied
```

---

## Memory Schema

Team-specific types extending the universal 4-layer structure from `MEMORY_SYSTEM.md`.

**For detailed data flow from app to memory (tag generation, relationships, precedent matching), see `planning/field-app/MEMORY_INTEGRATION.md`.**

```python
SAFETY_TEAM_TYPES = TeamMemorySchema(
    team_type="safety",
    strategic_types=["goal", "kpi", "policy_objective"],
    operational_types=["standard", "checklist", "protocol", "regulatory_requirement"],
    entity_types=["facility", "equipment", "hazard", "inspector", "room"],
    event_types=["inspection", "finding", "corrective_action", "incident"],
)
```

### Key Entity Structures

**Facility Memory:**
```python
{
    "symbol": "entity.facility.dayton-fleet",
    "type": "facility",
    "tags": ["department:fleet", "risk_level:medium", "last_inspection:2024-06"],
    "micro": "Dayton Fleet|Medium Risk|Annual Due 2025-06",
    "summary": "Fleet maintenance facility at 123 Industrial Dr. 15 rooms, 47 equipment items. Last inspection June 2024 found 12 findings (3 high, 5 medium, 4 low). All corrected.",
    "full": { ... complete facility record ... }
}
```

**Finding Memory:**
```python
{
    "symbol": "event.finding.fleet-dayton-2025-01",
    "type": "finding",
    "tags": ["facility:dayton-fleet", "priority:high_30", "equipment:fire_extinguisher", "status:open"],
    "micro": "Fire ext|High-30|Pressure low|Room 102",
    "summary": "Fire extinguisher in Room 102 (Maintenance Shop) found with pressure gauge in red zone. Requires service or replacement within 30 days per NFPA 10, 7.2.1.2.",
    "full": { ... complete finding with photos, recommendation, regulatory ref ... }
}
```

---

## Success Metrics

### For Consulting Firm

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to complete inspection | 50% reduction vs manual | Compare same facility inspections |
| Report generation time | < 1 hour after inspection | Timestamp from completion to PDF |
| Report quality score | > 4.5/5 from clients | Client feedback survey |
| Compliance gap detection | 100% of required items checked | Audit of checklist coverage |
| Follow-up completion rate | > 90% within deadline | Corrective action tracking |

### For Platform Validation

| Metric | Target | Measurement |
|--------|--------|-------------|
| Agent coordination accuracy | > 95% correct routing | Sample audit of orchestrator decisions |
| Passport state persistence | 100% across restarts | Checkpoint recovery testing |
| Memory retrieval relevance | > 80% useful results | Inspector feedback on Assistant responses |
| Field usability | < 5 complaints per 100 inspections | Inspector feedback tracking |

---

## Implementation Notes

### Phase 2 Deliverables (from roadmap)

1. Safety Team agents implementation (this specification)
2. Inspection App MVP (see `FIELD_APP_SPEC.md`)
3. Agent-App integration points
4. Real-world testing with founder's contacts

### Key Risks

| Risk | Mitigation |
|------|------------|
| Mobile app dev requires native expertise | Start with PWA, evaluate native later |
| Offline sync complexity | MVP requires connectivity, offline in v2 |
| Field conditions reveal UX issues | Early testing with real inspectors |
| Regulatory requirements vary by jurisdiction | Start with Maryland (Martinez Act), expand |

### Dependencies

- Core agent framework (Passport, Base Agent, Orchestrator) must be complete
- Memory system storage layer (PostgreSQL + ChromaDB) implemented
- Authentication working for multi-tenant isolation
- Inspection App MVP functional for field testing

---

*Version: 1.0*
*Created: 2025-01-06*
*Updated: 2025-01-06*
*Status: Specification ready for implementation*

**Changelog:**
- v1.0: Full specification integrating with FIELD_APP_SPEC.md; replaced placeholder TODOs with concrete details
- v0.1: Initial placeholder awaiting founder input
