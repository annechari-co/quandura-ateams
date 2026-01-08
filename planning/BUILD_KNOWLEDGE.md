# Quandura Build Knowledge

External memory for development sessions. Read at session start, update as you discover relationships.

**Last Updated:** 2025-01-08

---

## Core Dependency Map

### Passport (models/passport.py)
```
@uses confidence | @usedby agents.*, orchestrator, api.schemas, api.missions, db.models
```

**USED BY:**
- `agents/base.py` - Agent.execute() receives and returns Passport
- `agents/triage.py` - TriageAgent.process()
- `agents/executor.py` - ExecutorAgent.process()
- `agents/librarian.py` - Librarian.process(), context assembly
- `agents/judge.py` - JudgeAgent.process()
- `platform/orchestrator.py` - PassportState wraps Passport
- `api/schemas.py` - PassportResponse, PassportDetailResponse serialize it
- `api/missions.py` - Creates Passport from MissionCreate, persists to DB
- `db/models.py` - PassportModel stores passport_state as JSONB

**CONTAINS:**
- `ConfidenceVector` - Evidence-based confidence (value, evidence_count, evidence_quality, historical_accuracy)
- `LedgerEntry` - Immutable audit record
- `RoutingInfo` - Next agent, escalation info
- `Mission` - Objective, constraints, success_criteria

**CONTRACTS:**
- `Agent.execute()` always returns Passport, never None
- `confidence` field is `ConfidenceVector`, not a float
- `ledger` is append-only via `add_ledger_entry()`
- `status` must be one of: pending, in_progress, blocked, completed, failed, escalated

**IF MODIFIED:**
- Update `PassportResponse` in api/schemas.py if adding fields
- Update `PassportModel` in db/models.py if adding persisted fields
- Run Alembic migration if DB schema changes
- Check all agent process() methods

---

### Agent Base Class (agents/base.py)
```
@uses passport, confidence, config | @usedby triage, executor, librarian, judge, orchestrator
```

**USED BY:**
- `agents/triage.py` - Subclass
- `agents/executor.py` - Subclass
- `agents/librarian.py` - Subclass
- `agents/judge.py` - Subclass
- `platform/orchestrator.py` - Creates agent nodes, calls execute()

**DEPENDS ON:**
- `models/passport.py` - Passport, ConfidenceVector
- `core/config.py` - get_settings()
- `anthropic` - AsyncAnthropic client

**CONTAINS:**
- `AgentConfig` - agent_id, agent_type, model, system_prompt, autonomy_level
- `AgentResult` - success, output, confidence, tool_calls, artifacts
- `Agent` - Abstract base with execute(), process(), call_llm()

**CONTRACTS:**
- `process(passport) → AgentResult` - Abstract, must implement
- `execute(passport) → Passport` - Wraps process(), updates ledger
- `call_llm(messages) → (text, tool_uses, tokens)` - LLM wrapper
- Confidence tracked via `calculate_confidence()` and `record_outcome()`

**IF MODIFIED:**
- Check ALL subclasses (triage, executor, librarian, judge)
- Check orchestrator._create_agent_node()
- If changing execute() signature, update orchestrator

---

### Orchestrator (platform/orchestrator.py)
```
@uses agents.base, passport, langgraph | @usedby api.missions
```

**USED BY:**
- `api/missions.py` - execute_mission() creates team and calls run()
- `agents/teams/basic.py` - create_basic_team() returns Orchestrator

**DEPENDS ON:**
- `agents/base.py` - Agent class
- `models/passport.py` - Passport
- `langgraph` - StateGraph, BaseCheckpointSaver
- `platform/checkpointer.py` - PostgresCheckpointer (optional)

**CONTAINS:**
- `TeamConfig` - team_id, agents dict, entry_point, routing_rules
- `PassportState` - LangGraph state wrapper (passport + iteration)
- `Orchestrator` - Graph builder and runner

**CONTRACTS:**
- `run(passport, thread_id) → Passport` - Execute workflow
- `resume(thread_id, updates) → Passport` - Resume from checkpoint
- Routing determined by passport.routing.next_agent or routing_rules
- Terminates on: completed, failed, escalated, max_iterations

**IF MODIFIED:**
- Check api/missions.py execute_mission()
- Check agents/teams/basic.py create_basic_team()
- If changing PassportState, ensure LangGraph compatibility

---

### Memory Node (models/memory.py)
```
@uses - | @usedby memory.storage, memory.embeddings, librarian, db.models
```

**USED BY:**
- `memory/storage.py` - MemoryStorage CRUD operations
- `memory/embeddings.py` - EmbeddingStore
- `memory/queries.py` - MemoryQueryBuilder
- `agents/librarian.py` - All retrieval methods
- `db/models.py` - MemoryNodeModel (SQLAlchemy equivalent)

**CONTAINS:**
- `MemoryLayer` - strategic, operational, entity, event
- `MemoryResolution` - micro, summary, full
- `RelationType` - involves, applies, similar_to, etc.
- `MemoryNode` - Base node with symbol, micro/summary/full, tags, salience
- `Relationship` - Typed edge between nodes

**CONTRACTS:**
- `symbol` format: `layer.type.id` (e.g., "event.finding.F-2024-001")
- `micro` ≤ 100 chars, `summary` ≤ 500 chars
- `tags` are "key:value" format (e.g., "facility:dayton-fleet")
- `salience` 0.0-1.0, decays over time

**IF MODIFIED:**
- Update MemoryNodeModel in db/models.py
- Update MemoryStorage._to_pydantic() conversion
- Run Alembic migration if DB schema changes
- Check Librarian retrieval methods

---

### Memory Storage (memory/storage.py)
```
@uses memory.models, db.models | @usedby librarian
```

**USED BY:**
- `agents/librarian.py` - All CRUD and query operations

**DEPENDS ON:**
- `models/memory.py` - MemoryNode, MemoryLayer, MemoryResolution, RelationType
- `db/models.py` - MemoryNodeModel, MemoryRelationshipModel
- `sqlalchemy.ext.asyncio` - AsyncSession

**CONTRACTS:**
- All operations scoped by tenant_id (RLS pattern)
- `create()`, `update()`, `delete()` - Standard CRUD
- `find_by_tags()`, `find_by_layer()`, `find_by_pattern()` - Query methods
- `traverse()` - Graph traversal
- `boost_salience()`, `decay_salience()` - Salience management

**IF MODIFIED:**
- Check Librarian methods that use storage
- Ensure tenant_id scoping is maintained (security)

---

### API Schemas (api/schemas.py)
```
@uses passport | @usedby api.missions
```

**USED BY:**
- `api/missions.py` - All endpoint request/response types

**DEPENDS ON:**
- `models/passport.py` - Mirrors Passport structure for API

**CONTAINS:**
- `MissionCreate` - Create request
- `PassportResponse` - List/summary response
- `PassportDetailResponse` - Full response with ledger
- `MissionStatusUpdate` - Update request

**CONTRACTS:**
- `overall_confidence` is serialized as float (from ConfidenceVector.value)
- `ledger` entries serialized as dicts

**IF MODIFIED:**
- Check api/missions.py endpoint return types
- If adding fields, ensure Passport has them

---

### Database Models (db/models.py)
```
@uses sqlalchemy | @usedby api.missions, memory.storage
```

**USED BY:**
- `api/missions.py` - PassportModel, LedgerEntryModel CRUD
- `memory/storage.py` - MemoryNodeModel, MemoryRelationshipModel CRUD

**CONTAINS:**
- `TenantModel` - Multi-tenant root
- `TeamModel` - Agent team configuration
- `PassportModel` - Persisted passport state
- `LedgerEntryModel` - Audit log entries
- `MemoryNodeModel` - Memory nodes
- `MemoryRelationshipModel` - Memory edges

**CONTRACTS:**
- ALL models have tenant_id (RLS requirement)
- UUIDs for primary keys
- JSONB for complex nested data (mission_data, context, etc.)
- Timestamps: created_at, updated_at

**IF MODIFIED:**
- Create Alembic migration
- Update corresponding Pydantic model if schema changes
- Check storage/API code that queries these models

---

### Librarian (agents/librarian.py)
```
@uses agent.base, memory.*, passport | @usedby orchestrator, teams
```

**USED BY:**
- Teams that need context retrieval
- Orchestrator (as a node in workflow)

**DEPENDS ON:**
- `agents/base.py` - Agent base class
- `memory/storage.py` - MemoryStorage
- `memory/embeddings.py` - EmbeddingStore
- `memory/queries.py` - MemoryQueryBuilder
- `models/memory.py` - All memory types

**CONTAINS:**
- `LibrarianConfig` - tenant_id, team_id, max_context_tokens
- `AgentContext` - Assembled context for other agents
- Retrieval methods: retrieve(), query(), find_similar(), traverse()
- Context assembly: assemble_agent_context()

**CONTRACTS:**
- Requires AsyncSession for DB access
- ChromaDB for embeddings (sync client, may need executor wrapper)
- Boosts salience on retrieval

**IF MODIFIED:**
- Check teams that use Librarian
- If changing retrieval interface, update calling code

---

## Cross-Cutting Concerns

### Multi-Tenancy
```
ALL database operations MUST be scoped by tenant_id
```
- Every DB model has tenant_id column
- RLS policies will be added in production
- API extracts tenant_id from JWT (TODO: currently hardcoded "default")

### Async Patterns
```
Backend is async-first
```
- Use `async def` for all IO operations
- SQLAlchemy uses AsyncSession
- Anthropic uses AsyncAnthropic
- **GOTCHA:** ChromaDB client is sync - wrap in `run_in_executor` if needed

### LangGraph Integration
```
Orchestrator uses LangGraph StateGraph
```
- PassportState wraps Passport for LangGraph compatibility
- Checkpointer enables pause/resume
- thread_id links to checkpoint storage

---

## Known Gotchas

1. **ChromaDB is sync** - The EmbeddingStore uses sync ChromaDB client. For async contexts, may need to wrap in executor.

2. **Passport.confidence is ConfidenceVector** - Not a float. The API serializes it as `overall_confidence.value`.

3. **tenant_id hardcoded** - Currently "default" in API. TODO: Extract from JWT.

4. **team_id type mismatch** - Sometimes str, sometimes UUID. Be careful with serialization.

5. **Alembic migrations required** - Any db/models.py change needs `alembic revision --autogenerate`.

6. **LangGraph state must be Pydantic** - PassportState must be BaseModel for LangGraph.

7. **Ledger is append-only** - Never modify existing entries. Use `add_ledger_entry()`.

---

## Recent Discoveries

*(Add entries as you learn things during development)*

- [2025-01-08] Initial knowledge base created from codebase analysis
- [2025-01-08] Memory layer fully implemented with PostgreSQL + ChromaDB
- [2025-01-08] Librarian agent complete with retrieval methods

---

## File Quick Reference

```
backend/app/
├── models/
│   ├── passport.py      # Passport, ConfidenceVector, LedgerEntry, Mission
│   └── memory.py        # MemoryNode, MemoryLayer, RelationType
├── agents/
│   ├── base.py          # Agent, AgentConfig, AgentResult
│   ├── triage.py        # TriageAgent
│   ├── executor.py      # ExecutorAgent
│   ├── librarian.py     # Librarian (context retrieval)
│   └── judge.py         # JudgeAgent
├── platform/
│   ├── orchestrator.py  # Orchestrator, TeamConfig, PassportState
│   └── checkpointer.py  # PostgresCheckpointer
├── memory/
│   ├── storage.py       # MemoryStorage (PostgreSQL CRUD)
│   ├── embeddings.py    # EmbeddingStore (ChromaDB)
│   └── queries.py       # MemoryQueryBuilder
├── api/
│   ├── missions.py      # REST endpoints
│   └── schemas.py       # Request/response models
├── db/
│   ├── base.py          # SQLAlchemy setup
│   └── models.py        # SQLAlchemy models
├── core/
│   ├── config.py        # Settings
│   └── redis.py         # Redis client
└── main.py              # FastAPI app
```

---

## Session Checklist

**At Session Start:**
- [ ] Read this file to restore context
- [ ] Check git status for pending changes
- [ ] Note any new gotchas from last session

**Before Modifying Core Files:**
- [ ] Check "IF MODIFIED" section for that file
- [ ] Read the downstream dependencies
- [ ] Consider if tests need updating

**When You Discover Something:**
- [ ] Add to "Recent Discoveries" section
- [ ] Update relevant dependency sections
- [ ] Add to "Known Gotchas" if it's a trap

**At Session End:**
- [ ] Update "Recent Discoveries" with learnings
- [ ] Commit this file if changed

---

*This file is your external memory. Keep it accurate.*
