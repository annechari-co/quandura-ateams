# Build Considerations by Phase

Gap analysis and considerations for each build phase. Not blockers - things to think about at the right time.

---

## Strategic Context

### What We're Actually Building

**Primary Product:** Safety Consulting platform (agent team + field inspection app) that generates revenue while we prove out the agentic approach.

**Platform Validation:** Legal Research Team built by a partner with legal domain expertise. This validates the platform is flexible enough for domain experts to build their own agent teams on top of it.

**Iteration Vehicle:** We'll build many agent teams (beyond just these two) to validate the process and refine the platform. Each team teaches us what the core engine needs.

**Revenue Path:**
```
Safety Consulting → Agentic Risk Department → TPA Services
     (now)              (near-term)            (longer-term)
```

Most counties are self-insured but use Third Party Administrators (TPAs) to manage claims. The aspirational end state isn't abstract "county OS" - it's becoming the agentic TPA that handles risk management operations end-to-end.

### Build Priorities (Adjusted)

| Priority | Component | Why |
|----------|-----------|-----|
| **1** | Core Agent Engine | Foundation everything else needs |
| **2** | Safety Team + Field App | Revenue generator, proves real-world value |
| **3** | Legal Team (partner-built) | Platform validation, proves partners can build on it |
| **4** | Additional Teams | Iterate, learn, expand platform capabilities |
| **5** | Full Risk Dept / TPA | Aspirational end state, emerges from 1-4 |

### Partner Model

- **We build:** Core platform, Safety team, Field inspection app
- **Partners build:** Domain-specific teams (Legal, HR, etc.) using our platform
- **Platform requirement:** Must support partners creating their own agent teams without deep platform knowledge

This means the core engine needs to be:
- Well-documented with clear extension points
- Flexible enough for different domain workflows
- Observable so partners can debug their teams

---

## Build Order Overview

```
Phase 1: Core Agent Engine  ←────────────→  Platform UI (parallel)
                   │                              │
                   └──────────┬───────────────────┘
                              ▼
                        Integration
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    Safety Team + Field App            Legal Team (partner)
         [PRIORITY]                    [VALIDATION]
              │                               │
              ▼                               ▼
    Revenue Generation              Platform Validation
              │                               │
              └───────────────┬───────────────┘
                              ▼
                   Additional Agent Teams
                   (iterate and expand)
                              │
                              ▼
                    Agentic Risk Dept / TPA
                       (aspirational)
```

**Build Sequence:**
1. **Core Engine + Platform UI** - Built in parallel (define API contracts first, UI mocks backend)
2. **Safety Team + Field App** - Primary focus, revenue generator (we build this)
3. **Legal Team** - Partner builds on our platform (validates platform extensibility)
4. **Additional Teams** - Iterate on platform based on learnings

**Critical Dependency:** Lock down shared schemas (Facility, Finding, User, Tenant) before Safety Team work begins.

---

## Phase 1: Core Agent Engine

### What's Well-Defined ✓

- Passport schema with confidence vectors
- Three-layer architecture (Platform Intelligence, Orchestration, Execution)
- Context sandboxing pattern
- Dual-loop orchestration (Magentic-One)
- Agent base class with confidence tracking
- Memory architecture (working, episodic, semantic)
- Judge agent for external validation
- De-scaffolding/autonomy levels
- Multi-tenant with PostgreSQL RLS
- MCP tool schema compatibility
- Hybrid symbolic + neural rule engine

### Considerations for Phase 1

| Area | Question | When to Decide |
|------|----------|----------------|
| **LangGraph Integration** | How do we map Passport state to LangGraph nodes? What's the checkpoint key pattern? | Start of Phase 1 |
| **Tool Registry Bootstrap** | Which MCP tools do we build first? What's the minimum viable set? | Week 1 |
| **Database Migrations** | Alembic strategy? How to handle Passport schema evolution? | Week 1 |
| **Event/Message System** | How does passport completion trigger downstream workflows? Redis pub/sub? Celery? | Week 2 |
| **Error Handling** | Retry strategy? Circuit breakers for LLM calls? Timeout policies? | Week 2 |
| **Testing Strategy** | How do we test agent behaviors? Mock LLM responses? Record/replay? | Week 1 |
| **Configuration Storage** | How are team configurations stored? DB? YAML? Both? | Week 2 |
| **Observability** | OpenTelemetry integration - spans for each agent step? LLM call tracing? | Week 3 |
| **Auth Foundation** | Keycloak setup, tenant context extraction from JWT, service-to-service auth | Week 1 |
| **Background Jobs** | Celery beat for scheduled tasks (Janitor, Scouts)? Job priority? | Week 3 |
| **Rate Limiting** | Per-tenant token budgets? Per-model limits? Cost caps? | Week 3 |
| **Librarian Interface** | ChromaDB query patterns? Embedding model choice? Chunk strategy? | Week 2 |

### Missing Pieces to Build

1. **Concrete LangGraph Graph Definition** - How Passport moves through agent states
2. **Base Tool Implementations** - Document retrieval, web search, email send
3. **Confidence Calibration Storage** - Where does historical accuracy live?
4. **Tenant Context Middleware** - FastAPI dependency that sets tenant from JWT
5. **Audit Log Schema** - Actual table structure for decision logs
6. **Health Check Patterns** - LLM provider health, memory store health
7. **Secrets Management** - Vault integration or encrypted env vars?

### Phase 1 Validation Criteria

From QUANDURA_ARCHITECTURE.md:
> Run a 3-agent pipeline (Triage → Draft → Review) on test inputs

Add these checks:
- [ ] Passport persists across restarts (checkpoint works)
- [ ] Confidence scores are recorded in ledger
- [ ] Tenant isolation prevents cross-tenant reads
- [ ] Judge agent can reject and trigger revision

---

## Phase 1 (Parallel): Platform UI

### Purpose

Web dashboard for interacting with agent teams. Can be built in parallel with Core Engine using mocked API responses.

### Key Screens (from architecture docs)

| Screen | Purpose |
|--------|---------|
| Dashboard | Overview of active missions, team status |
| Mission Detail | Passport view, ledger, artifacts |
| Team Configuration | Agent settings, authority levels |
| Knowledge Base | Librarian content, document upload |
| Audit Log | Decision history, replay |
| Admin | User management, tenant settings |

### Considerations for Platform UI

| Area | Question | When to Decide |
|------|----------|----------------|
| **Framework** | React (specified in CLAUDE.md) + what state management? | Week 1 |
| **Component Library** | shadcn/ui (specified) - which components first? | Week 1 |
| **API Mocking** | MSW? Static JSON? OpenAPI mock server? | Week 1 |
| **Real-time Updates** | WebSocket for mission progress? Polling? SSE? | Week 2 |
| **Design System** | Colors, typography, spacing - government-appropriate | Week 1 |
| **Accessibility** | WCAG 2.1 AA required for government | Throughout |
| **Responsive** | Desktop-first? Mobile support needed? | Week 1 |

### Dependencies on Core Engine

| Need from Backend | Can Mock? | Notes |
|-------------------|-----------|-------|
| API contracts (OpenAPI) | Required upfront | Define before parallel work |
| Auth endpoints | Yes | Mock JWT, user context |
| Mission/Passport endpoints | Yes | Mock state progression |
| WebSocket events | Yes | Mock with timers |
| Actual data | No | Integration phase |

### Platform UI Validation Criteria

- [ ] Can view mocked mission progress
- [ ] Can browse mocked audit log
- [ ] Auth flow works with Keycloak (or mock)
- [ ] Responsive on tablet (field use case)
- [ ] Meets basic accessibility standards

---

## Phase 2a: Safety Consulting Team + Field App [PRIMARY]

> **This is the revenue-generating product we build ourselves.**

The Safety Team agents + Field Inspection App work together:
- **Field App** captures inspection data (facilities, rooms, findings, photos)
- **Safety Agents** generate reports, analyze trends, track corrective actions

See `FIELD_APP_SPEC.md` for complete field app specification. Safety agent team spec (`SAFETY_CONSULTING_TEAM.md`) to be created during this phase.

### What's Well-Defined ✓

**Field App (fully specified):**
- Complete data model (Facility, Room, Equipment, Inspection, Finding)
- RBAC roles
- Full inspection workflow
- Equipment types with regulatory criteria (20+ types)
- UI screen list (mobile + web)
- API endpoints (draft)
- Report structure matching RiskI format

**Safety Agents (needs specification):**
- Report Generator, Finding Analyst, Corrective Action Tracker, Compliance Advisor
- Integration points with Field App data
- PDF report generation requirements

### Considerations

| Area | Question | When to Decide |
|------|----------|----------------|
| **Field App Tech Stack** | React Native? Flutter? PWA? | Before starting |
| **Team Specification** | Create SAFETY_CONSULTING_TEAM.md | Week 1 |
| **PDF Report Generation** | WeasyPrint? ReportLab? | Week 1 |
| **Photo Storage** | S3? Cloudinary? Compression? | Week 1 |
| **Regulatory Knowledge Base** | OSHA, NFPA, ANSI ingestion | Week 2 |
| **Offline Strategy** | Design now, build later | Week 1 |

### Validation Criteria

- [ ] Inspector can complete full facility inspection on mobile
- [ ] Generated PDF matches RiskI report layout exactly
- [ ] Finding Analyst agent identifies patterns across inspections
- [ ] Corrective Action Tracker sends overdue alerts
- [ ] Revenue-ready: could charge a customer for this

---

## Phase 2b: Legal Research Team [PARTNER VALIDATION]

> **Built by a partner with legal domain expertise. Validates that external teams can build on our platform.**

This team tests whether our core engine is flexible and documented enough for domain experts (not us) to build agent teams. Success here means partners can extend Quandura without deep platform knowledge.

### What's Well-Defined ✓

- Agent roles: Triage, Research, Drafting, Review, Delivery
- Complete workflow diagram
- LegalResearchPassport extension
- Output schemas (TriageResult, ResearchMemo, DraftOpinion, ReviewResult)
- Escalation criteria (6 triggers)
- Success metrics with targets

> **Note:** `LAW_OFFICE_LEGAL_RESEARCH.md` is a draft. Legal expert partner will own refinement. Our job is to ensure the platform supports their needs.

### Considerations for Legal Team (Partner Decisions)

| Area | Question | Notes |
|------|----------|-------|
| **Legal Database Choice** | Westlaw, LexisNexis, CourtListener, etc. | Partner decides based on budget |
| **Citation Parser** | eyecite library? Custom? | Platform provides hooks |
| **Document Templates** | Letterhead, style preferences | Partner provides |
| **Email Integration** | Gmail? Microsoft Graph? | Platform supports both |

### Platform Requirements for Legal Team

What WE must provide for the partner to succeed:

1. **Clear extension API** - How to create custom Passport types
2. **Tool registration** - How to add domain-specific tools (legal DB search)
3. **Agent template** - Base class that handles boilerplate
4. **Documentation** - Partner onboarding guide
5. **Observability** - Partner can debug their agents

### Legal Team Validation Criteria

This validates the PLATFORM, not the legal team itself:
- [ ] Partner can create custom Passport extension without our help
- [ ] Partner can register custom tools
- [ ] Partner can deploy their team to our infrastructure
- [ ] Partner can monitor their agents' performance
- [ ] Platform documentation was sufficient

---

## Cross-Cutting Concerns (All Phases)

### Shared Data Models - LOCK DOWN FIRST

These entities are used by multiple workstreams:

| Entity | Used By | Notes |
|--------|---------|-------|
| `Facility` | Safety Team, Field App | Same table, same schema |
| `Room` | Safety Team, Field App | Floor plan relationship |
| `Finding` | Safety Team, Field App | Core to both |
| `EquipmentType` | Safety Team, Field App | Reference data |
| `User` | All | Auth shared |
| `Tenant` | All | Multi-tenancy shared |

**Action:** Finalize these schemas before Phase 2 parallel work begins.

### Authentication Architecture

| Question | Options | Recommendation |
|----------|---------|----------------|
| Single Keycloak for all? | Yes / Separate per app | Single - simpler |
| Mobile app auth flow | OAuth PKCE / Device code | OAuth PKCE |
| Service-to-service | Client credentials / Shared secrets | Client credentials |
| Token refresh on mobile | Background refresh / On-demand | On-demand with grace period |

### API Versioning

With parallel development, APIs will evolve. Need strategy:

- URL versioning: `/api/v1/facilities`
- Header versioning: `Accept-Version: 1.0`
- Or strict contracts locked before parallel work

### Deployment Architecture

| Component | Where | Why |
|-----------|-------|-----|
| Platform API | Main cluster | Core services |
| Field App Backend | Same cluster? Separate? | Depends on scale needs |
| Field App Frontend | CDN / App stores | Mobile distribution |
| Web Dashboard | CDN | Static hosting |
| Report Generation | Separate service? | PDF generation is CPU-heavy |

### Cost Attribution

Primary cost centers (what we build):
1. **Safety Team** - LLM tokens (moderate), photo storage, PDF generation
2. **Field App** - Photo storage, sync bandwidth
3. **Platform overhead** - Orchestration, memory stores, monitoring

Partner cost centers (passed through):
4. **Legal Team (partner)** - LLM tokens (heavy), legal DB API calls
5. **Future partner teams** - Variable based on domain

Need per-tenant cost tracking from day one. Partners should see their costs clearly.

---

## Recommended Pre-Work

### Before Phase 1 Parallel Work (Core Engine + Platform UI)

1. **[ ] Define API contracts** - OpenAPI specs so UI can mock backend
2. **[ ] Design auth flow** - Keycloak endpoints, JWT structure
3. **[ ] Agree on WebSocket event schema** - For real-time mission updates

### Before Phase 2 Parallel Work (Legal + Safety + Inspection App)

1. **[ ] Finalize shared data models** - Facility, Room, Finding, User, Tenant
2. **[ ] Choose Field App tech stack** - React Native vs Flutter vs PWA
3. **[ ] Core Engine MVP complete** - Basic agent pipeline working

**Created during Phase 2 (not blockers):**
- Safety Team agent spec - created when Phase 2b starts
- Legal Team refinements - partner review when Phase 2a starts

---

## Phase 3: Integration Considerations

After parallel Phase 2 work, integration phase will need:

1. **Inspection → Agent Flow** - Completed inspections trigger analysis agents
2. **Cross-System Dashboard** - Legal + Safety status in one view
3. **Unified Notification System** - Escalations, alerts, reminders
4. **Combined Reporting** - County-level dashboards
5. **Shared Document Storage** - Legal opinions + Inspection reports in one vault
6. **Billing Consolidation** - Single invoice for all services

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Legal DB costs explode | High | Budget cap, fallback to free sources |
| Mobile app performance | Medium | Lazy loading, offline-first design |
| PDF generation bottleneck | Medium | Queue + async, scale workers |
| Schema changes during parallel dev | High | Lock schemas before split |
| LLM rate limits hit | Medium | Token budgets, queue backpressure |
| Photo storage costs | Low | Compression, tiered storage |

---

*Created: 2025-01-05*
*Purpose: Guide implementation decisions at appropriate time*
