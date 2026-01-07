# Quandura Build Plan

Development sequence for the core engine and team system.

---

## Current State Assessment

### What's Built (Backend Structure)

| File | Component | Status |
|------|-----------|--------|
| `models/passport.py` | Passport, ConfidenceVector, LedgerEntry, Mission | ✅ Complete |
| `models/memory.py` | MemoryNode, MemoryLayer, RelationType, TeamMemorySchema | ✅ Complete |
| `agents/base.py` | BaseAgent class with LLM calls, confidence tracking | ✅ Complete |
| `agents/triage.py` | Triage agent (classifies/routes missions) | ✅ Complete |
| `agents/executor.py` | Executor agent (performs work) | ✅ Complete |
| `agents/teams/basic.py` | 2-agent team wiring | ✅ Complete |
| `platform/orchestrator.py` | LangGraph state machine | ✅ Complete |
| `platform/checkpointer.py` | PostgreSQL checkpoint persistence | ✅ Complete |
| `db/models.py` | SQLAlchemy models (Tenant, Team, Passport, LedgerEntry) | ✅ Complete |
| `db/base.py` | Async database setup | ✅ Complete |
| `api/missions.py` | REST endpoints (create, list, get, execute) | ✅ Complete |
| `api/schemas.py` | API request/response schemas | ✅ Complete |
| `core/config.py` | Pydantic settings | ✅ Complete |
| `core/redis.py` | Redis connection pool | ✅ Complete |
| `main.py` | FastAPI app | ✅ Complete |

### What's Missing (Phase 1 Completion)

| Component | Description | Priority |
|-----------|-------------|----------|
| Memory Storage | PostgreSQL persistence for MemoryNode | P0 |
| Memory Embeddings | ChromaDB integration for semantic search | P0 |
| Librarian Agent | Knowledge retrieval agent | P0 |
| Judge Agent | External validation (SCoRe pattern) | P1 |
| Legal Research Team | 5 agents for test harness | P1 |
| Tests | Agent behavior tests | P1 |
| Context Sandbox | Minimal context extraction for specialists | P2 |
| Symbolic Rule Engine | Hard rules for compliance/safety | P2 |

---

## Phase 1: Core Engine Completion

**Goal:** Working team system validated with Legal Research test harness

### Step 1: Environment Setup & Smoke Test (Day 1)

```bash
# Create .env
cd backend && cp .env.example .env
# Add ANTHROPIC_API_KEY

# Start services
docker run -d --name quandura-db -e POSTGRES_USER=quandura -e POSTGRES_PASSWORD=quandura -e POSTGRES_DB=quandura -p 5432:5432 postgres:16
docker run -d --name quandura-redis -p 6379:6379 redis:7

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload

# Test: Create a mission via /docs
```

**Validation:** Server starts, can create/list missions

### Step 2: Memory Storage Layer (Days 2-4)

Create persistence for the memory system models.

**Files to create:**
```
backend/app/memory/
├── __init__.py
├── storage.py      # PostgreSQL storage for MemoryNode
├── embeddings.py   # ChromaDB integration
└── queries.py      # Query patterns (tag filter, traversal)
```

**Key implementations:**
1. `MemoryStorage` class - CRUD for MemoryNode in PostgreSQL (JSONB)
2. `EmbeddingStore` class - ChromaDB for semantic search
3. `MemoryQuery` class - Tag filtering, relationship traversal
4. Database migration for `memory_nodes` table

**SQLAlchemy model:**
```python
class MemoryNodeDB(Base):
    __tablename__ = "memory_nodes"

    id = Column(UUID, primary_key=True)
    tenant_id = Column(UUID, nullable=False, index=True)
    team_id = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, unique=True)
    layer = Column(String, nullable=False)  # strategic/operational/entity/event
    type = Column(String, nullable=False)
    tags = Column(ARRAY(String), default=[])
    micro = Column(Text)
    summary = Column(Text)
    full_content = Column(JSONB)
    salience = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
```

**Validation:** Can store and retrieve memory nodes with tag filtering

### Step 3: Librarian Agent (Days 5-7)

The Librarian retrieves relevant context for other agents.

**Files to create:**
```
backend/app/agents/librarian.py
```

**Key implementations:**
1. Query memory by symbol pattern
2. Query memory by tags
3. Semantic search via embeddings
4. Multi-resolution retrieval (micro → summary → full)
5. Relationship traversal
6. Context assembly for agents

**Core interface:**
```python
class Librarian(BaseAgent):
    async def retrieve(
        self,
        symbols: list[str],
        resolution: Literal["micro", "summary", "full"] = "summary",
    ) -> list[MemoryNode]: ...

    async def query(
        self,
        pattern: str | None = None,
        tags: dict[str, str] | None = None,
        layer: MemoryLayer | None = None,
        resolution: str = "micro",
        limit: int = 20,
    ) -> list[MemoryNode]: ...

    async def find_similar(
        self,
        text: str,
        layer: MemoryLayer | None = None,
        limit: int = 10,
    ) -> list[MemoryNode]: ...

    async def traverse(
        self,
        start_symbol: str,
        relation_types: list[RelationType],
        max_depth: int = 2,
    ) -> list[MemoryNode]: ...

    async def assemble_agent_context(
        self,
        passport: Passport,
        agent_type: str,
        max_tokens: int = 4000,
    ) -> AgentContext: ...
```

**Validation:** Can retrieve relevant memory for a test query

### Step 4: Judge Agent (Days 8-9)

External validation for agent outputs (SCoRe pattern).

**Files to create:**
```
backend/app/agents/judge.py
```

**Key implementations:**
1. Schema validation
2. Symbolic rule checking (basic version)
3. Semantic verification via LLM
4. Feedback generation for rejections

**Core interface:**
```python
class JudgeAgent(BaseAgent):
    async def judge(
        self,
        output: Any,
        expected_schema: type[BaseModel],
        context: SandboxedContext,
        verification_level: Literal["basic", "standard", "thorough"] = "standard",
    ) -> JudgmentResult: ...
```

**Validation:** Can accept/reject outputs with feedback

### Step 5: Legal Research Team (Days 10-14)

Test harness team with 5 agents.

**Files to create:**
```
backend/app/agents/teams/legal_research/
├── __init__.py
├── orchestrator.py    # Team orchestrator
├── intake.py          # Research Intake agent
├── researcher.py      # Legal Researcher agent
├── analyst.py         # Citation Analyst agent
├── drafter.py         # Opinion Drafter agent
└── reviewer.py        # Quality Reviewer agent
```

**Team flow:**
```
Mission arrives
    │
    ▼
Research Intake → Classify, extract requirements
    │
    ▼
Legal Researcher → Find relevant authorities
    │
    ▼
Citation Analyst → Verify citations, check conflicts
    │
    ▼
Opinion Drafter → Write draft opinion
    │
    ▼
Quality Reviewer → Review, approve or request revision
    │
    ▼
Mission complete
```

**Validation:** Can process a test legal research request end-to-end

### Step 6: Tests (Days 15-16)

**Files to create:**
```
backend/tests/
├── conftest.py
├── test_passport.py
├── test_memory.py
├── test_librarian.py
├── test_judge.py
└── test_legal_research_team.py
```

**Key test cases:**
1. Passport state persistence across checkpoints
2. Memory CRUD and tag filtering
3. Librarian retrieval at different resolutions
4. Judge acceptance/rejection logic
5. Legal Research Team end-to-end flow

**Validation:** Tests pass, coverage > 80%

---

## Phase 1 Completion Checklist

- [ ] Environment runs (PostgreSQL, Redis, FastAPI)
- [ ] Memory storage layer persists nodes
- [ ] ChromaDB stores and retrieves embeddings
- [ ] Librarian retrieves relevant context
- [ ] Judge validates outputs with feedback
- [ ] Legal Research Team processes test request
- [ ] Tests pass with > 80% coverage
- [ ] Passport persists across restarts
- [ ] Confidence scores recorded in ledger
- [ ] Tenant isolation works (RLS)

**Estimated time:** 2-3 weeks

---

## Phase 2: Safety Team + Inspection App

**Prerequisites:** Phase 1 complete and validated

### Step 1: Inspection App Backend (Week 1-2)

Implement data model from `planning/field-app/FIELD_APP_SPEC.md`:

**Files to create:**
```
backend/app/inspection/
├── __init__.py
├── models.py       # Facility, Room, Equipment, Inspection, Finding
├── schemas.py      # API schemas
├── storage.py      # Database operations
├── api.py          # REST endpoints
└── report.py       # PDF generation
```

**Key endpoints:**
- Facilities CRUD
- Floor plans upload/management
- Room inventory
- Inspection workflow (start, checklist, findings, complete)
- Report generation

### Step 2: Safety Team Agents (Week 2-3)

Implement agents from `planning/teams/SAFETY_TEAM.md`:

**Files to create:**
```
backend/app/agents/teams/safety/
├── __init__.py
├── orchestrator.py     # Safety Team Orchestrator
├── scheduler.py        # Scheduler Agent
├── inspector.py        # Inspector Assistant Agent
├── report_gen.py       # Report Generator Agent
├── compliance.py       # Compliance Checker Agent
├── followup.py         # Follow-up Tracker Agent
└── librarian.py        # Safety-specific Librarian
```

### Step 3: Memory Integration (Week 3)

Implement data flow from `planning/field-app/MEMORY_INTEGRATION.md`:

- Automatic tag generation on entity save
- Multi-resolution content generation
- Relationship creation
- Precedent matching for findings

### Step 4: Inspection App Frontend (Week 3-4)

**Tech:** React PWA with offline capability

**Key screens:**
- Floor plan viewer
- Room inspection checklist
- Finding capture with photos
- Report preview

### Step 5: Field Testing (Week 4+)

Real-world testing with founder's contacts.

---

## Development Sequence Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PHASE 1: CORE ENGINE                         │
│                           (2-3 weeks)                                │
├─────────────────────────────────────────────────────────────────────┤
│  Week 1                          │  Week 2                          │
│  ─────────────                   │  ─────────────                   │
│  • Environment setup             │  • Legal Research Team           │
│  • Memory storage layer          │  • Tests                         │
│  • ChromaDB integration          │  • Integration testing           │
│  • Librarian agent               │                                  │
│  • Judge agent                   │                                  │
└──────────────────────────────────┴──────────────────────────────────┘
                                   │
                                   ▼ Phase 1 validated
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE 2: SAFETY TEAM + APP                        │
│                           (4-6 weeks)                                │
├─────────────────────────────────────────────────────────────────────┤
│  Week 1-2                        │  Week 3-4                        │
│  ─────────────                   │  ─────────────                   │
│  • Inspection backend            │  • Inspection frontend (PWA)     │
│  • Safety Team agents            │  • Memory integration            │
│  • API endpoints                 │  • Field testing                 │
└──────────────────────────────────┴──────────────────────────────────┘
                                   │
                                   ▼ Phase 2 validated
┌─────────────────────────────────────────────────────────────────────┐
│                   PHASE 3: CONSULTING LAUNCH                         │
│                           (Ongoing)                                  │
├─────────────────────────────────────────────────────────────────────┤
│  • Real client engagements                                          │
│  • Iterate based on feedback                                        │
│  • Build case studies                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Parallel Work Opportunities

While colleague tests Legal Research Team (Phase 1 validation):

**Can start in parallel:**
- Inspection App backend data model (no agent dependencies)
- Facility/Room/Equipment CRUD
- Basic inspection workflow (non-AI parts)
- PDF report template

**Must wait for Phase 1:**
- Safety Team agents
- Inspector Assistant (needs Librarian)
- Memory integration (needs storage layer)
- Precedent matching

---

*Version: 1.0*
*Created: 2025-01-06*
*Status: Development plan for Phase 1 and Phase 2*
