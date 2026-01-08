# Quandura Build Plan

Development sequence for core engine, team system, and first deployment.

**Architecture Reference:** `QUANDURA_ARCHITECTURE.md` v2.4

---

## Current State

### Backend Structure (Built)

| Component | File | Status |
|-----------|------|--------|
| Passport + Confidence | `models/passport.py` | ✅ |
| Memory Models | `models/memory.py` | ✅ |
| Base Agent | `agents/base.py` | ✅ |
| Triage Agent | `agents/triage.py` | ✅ |
| Executor Agent | `agents/executor.py` | ✅ |
| Basic Team | `agents/teams/basic.py` | ✅ |
| LangGraph Orchestrator | `platform/orchestrator.py` | ✅ |
| PostgreSQL Checkpointer | `platform/checkpointer.py` | ✅ |
| SQLAlchemy Models | `db/models.py` | ✅ |
| Async DB Setup | `db/base.py` | ✅ |
| REST API | `api/missions.py` | ✅ |
| API Schemas | `api/schemas.py` | ✅ |
| Config | `core/config.py` | ✅ |
| Redis | `core/redis.py` | ✅ |
| FastAPI App | `main.py` | ✅ |

### Phase 1 Gaps (To Build)

| Component | Description | Priority |
|-----------|-------------|----------|
| Memory Storage | PostgreSQL persistence for MemoryNode | P0 |
| Embeddings | ChromaDB integration | P0 |
| Librarian Agent | Knowledge retrieval | P0 |
| Judge Agent | External validation (SCoRe) | P1 |
| **Team Templates** | YAML-based team definitions (v2.4) | P1 |
| **Agent Lifecycle** | Session/Sandbox/Identity layers (v2.4) | P1 |
| **Health Monitoring** | Heartbeat + staleness detection (v2.4) | P1 |
| **Escalation System** | Categories + tiered routing (v2.4) | P1 |
| Legal Research Team | 5-agent test harness | P1 |
| Tests | Agent behavior coverage | P1 |
| Context Sandbox | Minimal context per specialist | P2 |
| Symbolic Rules | Compliance/safety hard rules | P2 |

---

## Phase 1: Core Engine Completion

**Goal:** Working team system validated with Legal Research test harness

### Step 1: Environment Validation

```bash
# Start infrastructure
docker run -d --name quandura-db \
  -e POSTGRES_USER=quandura \
  -e POSTGRES_PASSWORD=quandura \
  -e POSTGRES_DB=quandura \
  -p 5432:5432 postgres:16

docker run -d --name quandura-redis -p 6379:6379 redis:7

# Backend setup
cd backend
cp .env.example .env  # Add ANTHROPIC_API_KEY
uv run alembic upgrade head
uv run uvicorn app.main:app --reload

# Validation: Create mission via /docs
```

### Step 2: Memory Storage Layer

**Files:**
```
backend/app/memory/
├── __init__.py
├── storage.py      # PostgreSQL CRUD for MemoryNode
├── embeddings.py   # ChromaDB integration
└── queries.py      # Tag filtering, traversal
```

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

**Validation:** Store and retrieve memory nodes with tag filtering

### Step 3: Librarian Agent

**File:** `backend/app/agents/librarian.py`

**Interface:**
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
        limit: int = 20,
    ) -> list[MemoryNode]: ...

    async def find_similar(
        self,
        text: str,
        limit: int = 10,
    ) -> list[MemoryNode]: ...

    async def assemble_agent_context(
        self,
        passport: Passport,
        agent_type: str,
        max_tokens: int = 4000,
    ) -> AgentContext: ...
```

**Validation:** Retrieve relevant memory for test query

### Step 4: Judge Agent

**File:** `backend/app/agents/judge.py`

**Interface:**
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

**Validation:** Accept/reject outputs with feedback

### Step 5: Team Templates (v2.4)

**Files:**
```
backend/app/teams/
├── __init__.py
├── schema.py       # TeamTemplate Pydantic model
├── loader.py       # YAML parsing + validation
└── registry.py     # Template storage/retrieval
```

**Template structure:** (from architecture v2.4)
```yaml
team:
  id: legal-research
  name: Legal Research Team
  version: "1.0"

roles:
  - id: triage
    name: Research Intake
    subscriptions: ["Ⓜ:*:legal:*"]
    capabilities: [classify, extract_requirements]

workflows:
  - id: standard-research
    name: Standard Legal Research
    steps:
      - id: intake
        agent: triage
        next: research
      - id: research
        agent: researcher
        next: analyze

escalation:
  categories: [decision, help, blocked, failed]
  tiers:
    - level: 1
      target: team_orchestrator
    - level: 2
      target: department_head
    - level: 3
      target: human

health:
  heartbeat_interval_seconds: 60
  stale_threshold_seconds: 300
  very_stale_threshold_seconds: 900
```

**Validation:** Load team from YAML, instantiate agents

### Step 6: Agent Lifecycle Layers (v2.4)

**File:** `backend/app/agents/lifecycle.py`

**Model:**
```python
class AgentLifecycle(BaseModel):
    # Identity Layer (persistent until reassigned)
    agent_id: str
    role_definition: str
    subscriptions: list[str]
    historical_accuracy: float
    created_at: datetime

    # Sandbox Layer (per-mission)
    current_mission_id: str | None
    sandbox_path: str | None
    work_state: dict

    # Session Layer (ephemeral, can cycle)
    session_id: str | None
    context_tokens_used: int = 0
    last_active: datetime | None = None
```

**Validation:** Session can cycle while sandbox/identity persist

### Step 7: Escalation System (v2.4)

**File:** `backend/app/escalation/`

**Categories:**
```python
class EscalationCategory(str, Enum):
    DECISION = "decision"      # Multiple valid paths
    HELP = "help"              # Need guidance
    BLOCKED = "blocked"        # Unresolvable dependency
    FAILED = "failed"          # Unexpected error
    EMERGENCY = "emergency"    # Security/data integrity
    GATE_TIMEOUT = "gate_timeout"  # Async condition failed
    LIFECYCLE = "lifecycle"    # Agent stuck
```

**Tiered routing:**
```
Agent → Team Orchestrator → Dept Head → Human (Ⓗ)
```

**Validation:** Escalation routes correctly by category and tier

### Step 8: Health Monitoring (v2.4)

**File:** `backend/app/health/`

**Config:**
```python
class HeartbeatConfig(BaseModel):
    interval_seconds: int = 60
    stale_threshold_seconds: int = 300
    very_stale_threshold_seconds: int = 900
```

**Staleness states:**
| Heartbeat Age | State | Action |
|---------------|-------|--------|
| < 5 min | Fresh | None |
| 5-15 min | Stale | Check for pending work |
| > 15 min | Very Stale | Alert orchestrator |

**Validation:** Detect stale agents, trigger alerts

### Step 9: Legal Research Team (Test Harness)

**Files:**
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

**Flow:**
```
Mission → Intake → Researcher → Analyst → Drafter → Reviewer → Complete
```

**Validation:** Process test legal research request end-to-end

### Step 10: Tests

**Files:**
```
backend/tests/
├── conftest.py
├── test_passport.py
├── test_memory.py
├── test_librarian.py
├── test_judge.py
├── test_team_templates.py
├── test_lifecycle.py
├── test_escalation.py
├── test_health.py
└── test_legal_research_team.py
```

**Coverage target:** > 80%

---

## Phase 1 Completion Checklist

### Core Engine
- [ ] Environment runs (PostgreSQL, Redis, FastAPI)
- [ ] Memory storage persists nodes
- [ ] ChromaDB stores/retrieves embeddings
- [ ] Librarian retrieves relevant context
- [ ] Judge validates outputs with feedback

### v2.4 Additions
- [ ] Team templates load from YAML
- [ ] Agent lifecycle layers work (session cycles, sandbox persists)
- [ ] Escalation routes by category and tier
- [ ] Health monitoring detects stale agents

### Validation
- [ ] Passport persists across restarts
- [ ] Confidence scores recorded in ledger
- [ ] Tenant isolation works (RLS)
- [ ] Legal Research Team processes test request
- [ ] Tests pass with > 80% coverage

---

## Phase 2: Safety Team + Inspection App

**Prerequisites:** Phase 1 complete

See `field-app/FIELD_APP_SPEC.md` for complete data model.
See `teams/SAFETY_TEAM.md` for agent specifications.

### Step 1: Inspection App Backend

**Files:**
```
backend/app/inspection/
├── models.py       # Facility, Room, Equipment, Inspection, Finding
├── schemas.py      # API schemas
├── storage.py      # Database operations
├── api.py          # REST endpoints
└── report.py       # PDF generation
```

### Step 2: Safety Team Agents

**Files:**
```
backend/app/agents/teams/safety/
├── orchestrator.py     # Safety Team Orchestrator
├── scheduler.py        # Scheduler Agent
├── inspector.py        # Inspector Assistant Agent
├── report_gen.py       # Report Generator Agent
├── compliance.py       # Compliance Checker Agent
├── followup.py         # Follow-up Tracker Agent
└── librarian.py        # Safety-specific Librarian
```

### Step 3: Memory Integration

From `field-app/MEMORY_INTEGRATION.md`:
- Automatic tag generation
- Multi-resolution content
- Relationship creation
- Precedent matching

### Step 4: Inspection App Frontend

**Tech:** React PWA with offline capability

**Key screens:**
- Floor plan viewer
- Room inspection checklist
- Finding capture with photos
- Report preview

### Phase 2 Completion Checklist

- [ ] Inspector completes full facility inspection on mobile
- [ ] PDF report matches RiskI format
- [ ] Safety agents analyze findings
- [ ] Corrective action tracking works
- [ ] Memory integration stores inspection data

---

## Parallel Work Opportunities

### Can start during Phase 1 testing:
- Inspection App data model (no agent deps)
- Facility/Room/Equipment CRUD
- Basic inspection workflow (non-AI)
- PDF report template

### Must wait for Phase 1:
- Safety Team agents
- Inspector Assistant (needs Librarian)
- Memory integration (needs storage layer)
- Precedent matching

---

## Document Relationships

```
QUANDURA_ARCHITECTURE.md (v2.4)  ← Source of truth
         │
         ├── BUILD_PLAN.md (this file)  ← Development sequence
         │
         ├── BUILD_CONSIDERATIONS.md  ← Phase-specific decisions
         │
         ├── teams/
         │   ├── LAW_OFFICE_LEGAL_RESEARCH.md  ← Test harness spec
         │   └── SAFETY_TEAM.md  ← Phase 2 spec
         │
         ├── field-app/
         │   ├── FIELD_APP_SPEC.md  ← Data model + UI
         │   └── MEMORY_INTEGRATION.md  ← Memory patterns
         │
         └── research/
             ├── UNIQ_SPEC.md  ← Communication grammar
             ├── GHOST_TOWN.md  ← Gas Town patterns adopted
             └── SCENARIO_OHS_INSPECTION.md  ← Reference workflow
```

---

*Version: 2.0 (synced with Architecture v2.4)*
*Updated: 2025-01-08*
