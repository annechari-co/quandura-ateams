# Parallel Development Plan

Two developers working simultaneously on Quandura using Claude Opus 4.5.

---

## Developer Assignments

| Developer | Focus Areas |
|-----------|-------------|
| **Walt** | Safety Team, Inspection App, UI, Core tests (passport/orchestrator) |
| **Partner** | Legal Research Team, Core tests (memory/librarian/judge) |

---

## Current State (Ready to Split)

### Core Engine - COMPLETE ✅
- ✅ Memory models with 4-layer architecture
- ✅ Memory storage (PostgreSQL + ChromaDB)
- ✅ Librarian agent (knowledge retrieval)
- ✅ Judge agent (external validation)
- ✅ Base agents (triage, executor)
- ✅ Orchestrator + checkpointer
- ✅ APIs (missions, memory)
- ✅ Database migrations

### Remaining Core Work
- ⏳ Environment validation (both developers)
- ⏳ Tests (split between developers)

---

## Phase 1: Core Engine Completion

### Both Developers - Environment Setup

Each developer needs their own local environment:

```bash
git clone https://github.com/annechari-co/quandura.git
cd quandura/backend
cp .env.example .env
# Edit .env: Add ANTHROPIC_API_KEY=sk-ant-...

# Start PostgreSQL
cd .. && docker-compose up -d

# Run migrations
cd backend
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload

# Test at http://localhost:8000/docs
# Try: Create a mission, list missions
```

**Validation checkpoint:** Server starts, can create/list missions via /docs

---

## Phase 1: Tests (Split)

### Partner - Core Agent Tests

Create `backend/tests/` with:

```
backend/tests/
├── conftest.py           # Shared fixtures
├── test_memory.py        # Memory storage CRUD, tag filtering
├── test_librarian.py     # Retrieval at different resolutions
└── test_judge.py         # Accept/reject logic, feedback generation
```

**Key test cases:**
1. `test_memory.py`
   - Create/read/update/delete memory nodes
   - Tag filtering works
   - Pattern matching works
   - Relationship traversal works

2. `test_librarian.py`
   - Retrieve by symbol
   - Query by tags
   - Find similar (semantic search)
   - Assemble agent context

3. `test_judge.py`
   - Schema validation catches errors
   - Symbolic rule checking
   - Verdict determination logic
   - Feedback generation

### Walt - Orchestrator Tests

Create:
```
backend/tests/
├── test_passport.py      # Passport state, confidence vectors
└── test_orchestrator.py  # State machine, checkpointing
```

**Key test cases:**
1. `test_passport.py`
   - Passport serialization/deserialization
   - Confidence vector calculations
   - Ledger entry creation
   - Status transitions

2. `test_orchestrator.py`
   - State machine transitions
   - Checkpoint persistence
   - Mission execution flow

---

## Phase 2: Team Development (Parallel)

### Partner - Legal Research Team

**Location:** `backend/app/agents/teams/legal_research/`

**Files to create:**
```
legal_research/
├── __init__.py          # ✅ EXISTS (update exports)
├── schemas.py           # ✅ EXISTS (complete)
├── orchestrator.py      # Team coordinator
├── intake.py            # Research Intake agent
├── researcher.py        # Legal Researcher agent
├── analyst.py           # Citation Analyst agent
├── drafter.py           # Opinion Drafter agent
└── reviewer.py          # Quality Reviewer agent
```

**Reference:** `planning/teams/LAW_OFFICE_LEGAL_RESEARCH.md`

**Team flow:**
```
Mission arrives
    │
    ▼
Research Intake → Parse question, identify sub-questions
    │
    ▼
Legal Researcher → Find statutes, cases, regulations
    │
    ▼
Citation Analyst → Verify citations, check conflicts
    │
    ▼
Opinion Drafter → Write formal opinion
    │
    ▼
Quality Reviewer → Review, approve or request revision
    │
    ▼
Mission complete
```

**Deliverable:** Process a test legal research request end-to-end

**Test file:** `backend/tests/test_legal_research_team.py`

---

### Walt - Inspection Backend + Safety Team

#### Step 1: Inspection Backend

**Location:** `backend/app/inspection/`

**Files to create:**
```
inspection/
├── __init__.py
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic request/response
├── storage.py       # Database operations
└── api.py           # REST endpoints
```

**Data models:**
```python
# models.py
class FacilityModel(Base):
    id, tenant_id, name, address, facility_type, floor_plan_url, ...

class RoomModel(Base):
    id, facility_id, floor, room_number, room_type, square_footage, ...

class EquipmentModel(Base):
    id, room_id, equipment_type, manufacturer, model, serial_number, ...

class InspectionModel(Base):
    id, facility_id, inspector_id, status, started_at, completed_at, ...

class FindingModel(Base):
    id, inspection_id, equipment_id, room_id, severity, description, photos, ...
```

**Migration:** `backend/alembic/versions/002_inspection_tables.py`

**API endpoints:**
- Facilities CRUD
- Rooms CRUD (nested under facilities)
- Equipment CRUD (nested under rooms)
- Inspections: start, add finding, complete
- Findings: create, update, list by inspection

**Reference:** `planning/field-app/FIELD_APP_SPEC.md`

#### Step 2: Safety Team

**Location:** `backend/app/agents/teams/safety/`

**Files to create:**
```
safety/
├── __init__.py
├── schemas.py           # Team-specific schemas
├── orchestrator.py      # Safety Team Orchestrator
├── scheduler.py         # Scheduler Agent
├── inspector.py         # Inspector Assistant Agent
├── report_gen.py        # Report Generator Agent
├── compliance.py        # Compliance Checker Agent
├── followup.py          # Follow-up Tracker Agent
└── librarian.py         # Safety-specific Librarian config
```

**Reference:** `planning/teams/SAFETY_TEAM.md`

**Deliverable:** Process a test inspection workflow end-to-end

---

## Phase 3: UI Development (Walt)

### Inspection App UI (PWA)

**Location:** `frontend/` (or `frontend/inspection/`)

**Key screens:**
- Facility list and details
- Floor plan viewer
- Room inspection checklist
- Finding capture with photos
- Report preview

### Teams UI

**Key screens:**
- Team dashboard (status of all teams)
- Mission queue and status
- Agent activity viewer
- Passport inspector (debug view)

---

## Coordination Points

### Shared Files - Coordinate Before Editing
- `backend/app/main.py` - Both add routers
- `backend/app/db/__init__.py` - Both add model exports
- `backend/alembic/env.py` - Both reference new models
- `docker-compose.yml` - If adding services

### Git Workflow

**Simple approach (recommended for now):**
- Both work on `main`
- Pull before starting each session
- Commit frequently with clear messages
- Push at end of session
- Communicate if touching shared files

**Commit message format:**
```
feat(legal): add research intake agent
feat(inspection): add facility CRUD endpoints
test(memory): add tag filtering tests
fix(judge): handle empty constraint list
```

---

## Timeline Suggestion

### Week 1
| Walt | Partner |
|------|---------|
| Environment validation | Environment validation |
| test_passport.py | test_memory.py |
| test_orchestrator.py | test_librarian.py, test_judge.py |
| Inspection models + migration | Legal Research schemas review |

### Week 2
| Walt | Partner |
|------|---------|
| Inspection API endpoints | Legal Research: intake, researcher |
| Start Safety Team schemas | Legal Research: analyst, drafter |

### Week 3
| Walt | Partner |
|------|---------|
| Safety Team agents | Legal Research: reviewer, orchestrator |
| Memory integration | test_legal_research_team.py |

### Week 4+
| Walt | Partner |
|------|---------|
| Inspection App UI | Support/fixes |
| Teams UI | Documentation |

---

## Getting Started Checklist

### Partner
- [ ] Clone repo, set up environment
- [ ] Run migrations, start server
- [ ] Test that /docs works
- [ ] Read `planning/teams/LAW_OFFICE_LEGAL_RESEARCH.md`
- [ ] Create `backend/tests/conftest.py`
- [ ] Start with `test_memory.py`

### Walt
- [ ] Validate environment runs
- [ ] Create `backend/tests/test_passport.py`
- [ ] Create `backend/app/inspection/models.py`
- [ ] Create migration for inspection tables
- [ ] Read `planning/teams/SAFETY_TEAM.md`

---

## Key References

| Document | Who | Purpose |
|----------|-----|---------|
| `planning/BUILD_PLAN.md` | Both | Overall sequence |
| `planning/QUANDURA_ARCHITECTURE.md` | Both | System architecture |
| `planning/teams/LAW_OFFICE_LEGAL_RESEARCH.md` | Partner | Legal team spec |
| `planning/teams/SAFETY_TEAM.md` | Walt | Safety team spec |
| `planning/field-app/FIELD_APP_SPEC.md` | Walt | Inspection app spec |
| `planning/field-app/MEMORY_INTEGRATION.md` | Walt | How inspection → memory |

---

## Sync Points

**Merge checkpoint 1:** Core tests pass
- Partner: memory, librarian, judge tests
- Walt: passport, orchestrator tests
- Run full test suite together

**Merge checkpoint 2:** Teams functional
- Partner: Legal Research Team processes test request
- Walt: Inspection CRUD + Safety Team processes test workflow

**Merge checkpoint 3:** Integration
- Both teams use shared Librarian
- Memory populated from both domains
- Cross-team patterns validated

---

*Created: 2025-01-07*
*Last updated: 2025-01-07*
