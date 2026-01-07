# Quandura Enterprise Platform: Comprehensive Plan

## Vision Statement

**Long-term (20+ years):** "The Operating System for Local Governments" - AI agent teams running entire government operations.

**Near-term:** Build profitable AI-assisted services for county Risk Management, starting with safety inspections.

---

## Founder Advantages

- Deep county government experience (not just contracting - actual operations)
- Intimate knowledge of Risk Management and Safety Team micro-processes
- Existing relationships with county personnel who can test in real-world environments
- Understanding of procurement cycles at a deeper level than most contractors
- Based in Maryland where Martinez Act creates immediate market opportunity

---

## Market Entry Strategy

### Phase 1: Safety Consulting Firm (Revenue Generation)

**The Opportunity: Martinez Act (Maryland)**

New legislation requires all Maryland local governments to implement self-inspection regimes. Counties are not prepared to stand up these programs quickly. They will need to outsource.

**Business Model:**
1. Launch consulting firm offering safety inspection services
2. Use Safety Team + Inspection App as force multiplier
3. Human inspectors augmented by agentic system
4. Undercut traditional consulting on price while maintaining quality
5. Each engagement is a touchpoint for upsell

**Why This First:**
- Immediate market demand (legislation-driven)
- Founder has deep expertise in running safety teams
- Real-world testers available through existing relationships
- Revenue generation before investor funding needed
- Validates the team system in production

### Phase 2: Agentic Risk Management Department

**Target:** Smaller counties that can't afford to spin up Risk Management departments (or can't do it quickly enough).

**Model:** Sell or license an operational Risk Management department as a service.

**Upsell Path:** Consulting clients → full Risk Management service

### Phase 3: Agentic TPA (Third-Party Administrator)

**The Market Insight:**

Most US counties are self-insured but use TPAs to manage claims. These TPAs are terrible:
- High turnover of claims managers
- Overloaded workloads
- Bad scheduling of services
- Poor communication
- This is a hole in the market

**Competitive Advantage:**
- All bidding information is publicly available
- If system works well, we know exactly how much we can underbid and still be profitable
- Quality can exceed incumbents because agents don't burn out

**Revenue Models:**
- Direct TPA services to counties
- License agentic TPA system to existing TPAs
- Hybrid models

### Phase 4: Seek Investment

**Timing:** When consulting firm is profitable AND we have:
- Functional (if not fully deployed) Risk Department product
- Strategic plan for TPA market entry
- Demonstrated real-world performance data

### Long-term: County OS (Aspirational)

Expand beyond Risk Management to other departments. 20-year horizon. Not relevant to near-term planning.

---

## Development Strategy

### Team System Architecture

Build a reusable "team system" that can be instantiated for different workflows:

| Team | Purpose | Status |
|------|---------|--------|
| **Safety Team** | Real-world deployment, revenue generation | First priority |
| **Legal Research Team** | Test harness for team system architecture | Test/validation |
| **Risk Management Team** | Product for small counties | After Safety validated |
| **Claims Team (TPA)** | Market disruption play | After Risk validated |

### Why Legal Research as Test Harness

Legal Research Team validates:
- Multi-agent coordination (5 agents in sequence)
- Passport state passing through workflow
- External tool integration
- Document generation
- Quality assurance patterns (Review agent)
- Knowledge persistence (Librarian)

This is not intended for deployment to actual county law departments (at least not soon). It's a controlled test of the team system before deploying Safety Team in the field.

### Why Safety Team First for Deployment

- Founder has deepest expertise here
- Real testers available
- Martinez Act creates market timing
- Inspection app provides concrete, usable artifact
- Revenue path is clearest

---

## Beachhead: Risk Management Departments

**Why Risk Management:**
- Chronically understaffed
- Drowning in data (incidents, claims, compliance)
- County governments have injury/incident rates far above private sector
- Clear, measurable ROI (reduced claims = reduced spending)
- Self-insured governments feel the pain directly
- Founder has extensive domain knowledge

**Expansion Path:**
```
Safety Consulting → Risk Management Dept → TPA → (long-term) Other Departments
        ↓                    ↓                ↓
    Revenue              Product           Market
   Generation             Sales          Disruption
```

---

## Core Platform Architecture

### Three-Layer Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLATFORM INTELLIGENCE LAYER                       │
│  (Self-improving, research-informed, human-approved changes)         │
├─────────────────────────────────────────────────────────────────────┤
│                    ORCHESTRATION LAYER                               │
│  (Multi-team coordination, department head agents, handoff routing)  │
├─────────────────────────────────────────────────────────────────────┤
│                    EXECUTION LAYER                                   │
│  (Individual agent teams doing the actual work)                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Execution Layer (Agent Teams)

### Team Types for Risk Management

| Team | Primary Function | Key Agents |
|------|------------------|------------|
| Incident Investigation | Phone intake, root cause analysis, recommendations | Investigator, Analyst, Reporter |
| Incident Triage | Categorize, prioritize, route incoming reports | Classifier, Router, Tracker |
| Claims Processing | Manage insurance claims lifecycle | Claims Handler, Document Manager, Carrier Liaison |
| Compliance Monitoring | Track training, policies, audit readiness | Compliance Tracker, Reminder Agent, Audit Preparer |
| Analytics & Reporting | Trends, metrics, leadership reports | Data Analyst, Visualization Agent, Report Writer |
| Safety Support | Inspection assistance, legal research, reports | Research Agent, Report Writer, Compliance Checker |

### Agent Team Structure (Per Team)

```
┌─────────────────────────────────────────────┐
│              TEAM ORCHESTRATOR              │
│  (Plans, delegates, synthesizes, reports)   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │Specialist│  │Specialist│  │Specialist│   │
│  │    A    │  │    B    │  │    C    │     │
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       └───────────┬┴───────────┘           │
│                   ▼                         │
│            ┌───────────┐                    │
│            │ LIBRARIAN │                    │
│            │(Knowledge)│                    │
│            └───────────┘                    │
└─────────────────────────────────────────────┘
```

### Core Components Per Team

**Passport (State Schema):**
```python
class Passport(BaseModel):
    # Identity
    mission_id: str
    team_id: str
    created_at: datetime

    # Mission
    objective: str
    success_criteria: List[str]
    constraints: List[str]

    # State
    current_phase: str
    ledger: List[LedgerEntry]  # Append-only work log
    artifacts: List[Artifact]  # Produced outputs

    # Routing
    next_agent: Optional[str]
    escalation_required: bool
    human_review_needed: bool

    # Confidence & Evidence
    confidence: ConfidenceVector
    evidence: List[Evidence]
    failure_risks: List[FailureRisk]

    # Audit
    decision_log: List[Decision]
    checkpoint_id: str  # LangGraph checkpoint reference
```

**Confidence Vector (not scalar):**
```python
class ConfidenceVector(BaseModel):
    score: float  # 0.0 - 1.0
    evidence_count: int
    evidence_quality: str  # "verified", "inferred", "assumed"
    historical_accuracy: float  # How often this confidence level was correct
    domain_weight: float  # How confident are we in this domain
    failure_modes: List[str]  # What could make this wrong
```

---

## Layer 2: Orchestration Layer

### Department Head Agent

Each department gets a meta-agent that oversees all teams:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPARTMENT HEAD AGENT                         │
│                                                                  │
│  Responsibilities:                                               │
│  • Monitor all team activities                                   │
│  • Provide status updates on request                             │
│  • Route work between teams (incident → claims → analytics)      │
│  • Escalate issues to human department head                      │
│  • Answer queries about any item in progress                     │
│                                                                  │
│  Authority Level: CONFIGURABLE PER ORG                           │
│  • Observe & Report: Monitor only, alert humans                  │
│  • Soft Intervention: Pause, clarify, escalate                   │
│  • Full Authority: Reassign, override, redirect                  │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ Incident │        │  Claims  │        │ Analytics│
    │   Team   │        │   Team   │        │   Team   │
    └──────────┘        └──────────┘        └──────────┘
```

### Cross-Team Handoff Protocol

```python
class TeamHandoff(BaseModel):
    source_team: str
    target_team: str
    passport: Passport
    handoff_type: Literal["automatic", "escalated", "human_dispatched"]
    routing_reason: str
    priority: Literal["low", "normal", "high", "urgent"]

    # For hybrid routing
    requires_human_approval: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
```

**Routing Rules (Configurable):**
- Routine items: Auto-route based on rules
- Complex items: Department Head Agent decides
- High-stakes items: Human approval required

---

## Layer 3: Platform Intelligence

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PLATFORM INTELLIGENCE LAYER                       │
│                                                                      │
│  ┌─────────────┐                              ┌──────────────────┐  │
│  │   Janitor   │──────┐                 ┌────▶│  Research Scout  │  │
│  │ (per-team)  │      │                 │     │    (arXiv)       │  │
│  └─────────────┘      │                 │     └──────────────────┘  │
│                       ▼                 │                           │
│  ┌─────────────┐  ┌──────────────┐      │     ┌──────────────────┐  │
│  │   Janitor   │─▶│  HOUSEKEEPER │◀─────┼────▶│  Research Scout  │  │
│  │ (per-team)  │  │  (platform)  │      │     │    (Blogs)       │  │
│  └─────────────┘  └──────┬───────┘      │     └──────────────────┘  │
│                          │              │                           │
│  ┌─────────────┐         │              │     ┌──────────────────┐  │
│  │   Janitor   │─────────┘              └────▶│  Research Scout  │  │
│  │ (per-team)  │                              │  (Partnerships)  │  │
│  └─────────────┘                              └──────────────────┘  │
│                                                                      │
│                          │                                           │
│                          ▼                                           │
│                  ┌───────────────┐                                   │
│                  │   PROPOSAL    │                                   │
│                  │    QUEUE      │                                   │
│                  └───────┬───────┘                                   │
│                          │                                           │
│                          ▼                                           │
│                  ┌───────────────┐                                   │
│                  │    HUMAN      │                                   │
│                  │   APPROVAL    │                                   │
│                  └───────────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

**Janitors (Per-Team):**
- Monitor team performance metrics
- Detect inefficiencies, redundancies, failures
- Flag issues to Housekeeper
- Track confidence calibration accuracy

**Housekeeper (Platform-Wide):**
- Aggregates issues from all Janitors
- Prioritizes by impact and frequency
- Correlates with Research Scout findings
- Generates improvement proposals

**Research Scouts (Multiple):**
- arXiv Scout: Monitor AI/ML papers
- Blog Scout: Track industry blogs, release notes
- Partnership Scout: Direct feeds from Anthropic, OpenAI, Google
- Community Scout: User/partner submitted findings

**Proposal Queue:**
- All improvements require human approval
- Proposals include: problem, solution, evidence, risk assessment
- Admins can approve, reject, or defer
- Approved changes are versioned and tracked

---

## Voice Interface: Incident Investigator

### Phone-Based Intake Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INCIDENT PHONE LINE                           │
│                                                                  │
│  Employee/Supervisor calls dedicated number                      │
│                          │                                       │
│                          ▼                                       │
│                  ┌───────────────┐                               │
│                  │    Twilio     │                               │
│                  │  Voice Gateway│                               │
│                  └───────┬───────┘                               │
│                          │                                       │
│                          ▼                                       │
│                  ┌───────────────┐                               │
│                  │  Speech-to-   │                               │
│                  │    Text       │                               │
│                  └───────┬───────┘                               │
│                          │                                       │
│                          ▼                                       │
│         ┌────────────────────────────────┐                       │
│         │     INVESTIGATOR AGENT         │                       │
│         │                                │                       │
│         │  • Structured interview flow   │                       │
│         │  • Clarifying questions        │                       │
│         │  • External data pulls:        │                       │
│         │    - Weather at time/location  │                       │
│         │    - Employee history          │                       │
│         │    - Location hazard data      │                       │
│         │    - Similar past incidents    │                       │
│         │  • Root cause analysis         │                       │
│         │  • Corrective action recs      │                       │
│         └────────────────┬───────────────┘                       │
│                          │                                       │
│                          ▼                                       │
│                  ┌───────────────┐                               │
│                  │   Incident    │                               │
│                  │    Report     │──────▶ Triage Team            │
│                  └───────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### Interview Structure

```python
class IncidentInterview(BaseModel):
    # Basic Info
    caller_name: str
    caller_role: Literal["employee", "supervisor", "witness"]
    incident_datetime: datetime
    location: str

    # What Happened
    description: str
    immediate_cause: str
    injuries_reported: bool
    property_damage: bool

    # Context (Agent Pulls)
    weather_conditions: WeatherData  # External API
    location_hazard_history: List[PastIncident]  # Internal DB
    employee_training_status: TrainingRecord  # HR System
    similar_incidents: List[PastIncident]  # Analytics

    # Analysis (Agent Generated)
    root_cause_analysis: RootCauseAnalysis
    contributing_factors: List[ContributingFactor]
    corrective_actions: List[CorrectiveAction]
    priority_level: Literal["low", "medium", "high", "critical"]
```

---

## Data Architecture

### Data Sources Integration

| Source | Type | Integration Method |
|--------|------|-------------------|
| Google Workspace | Email, Docs, Calendar | OAuth + API |
| Microsoft 365 | Email, Docs, Teams | Graph API |
| HR/Payroll Systems | Employee data, training | API or batch sync |
| Claims Management | Claims data | API integration |
| Weather Services | Historical weather | External API |
| GIS/Location | Hazard maps, facility data | API or import |

### Data Residency Options

**Customer Choice:**

| Option | Description | Use Case |
|--------|-------------|----------|
| Our Cloud | We host everything | Simplest, fastest deployment |
| Customer Cloud | Deploy in their Azure/GCP/AWS | They control infrastructure |
| Hybrid | Platform in our cloud, sensitive data in theirs | Balance of convenience and control |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SENSITIVE DATA ZONE                           │
│              (Customer's environment or encrypted)               │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Employee PII │  │ Claims Data  │  │ Incident     │          │
│  │              │  │              │  │ Reports      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         └─────────────────┼─────────────────┘                   │
│                           ▼                                      │
│                   ┌───────────────┐                              │
│                   │   SANDBOX     │                              │
│                   │  (Isolated)   │                              │
│                   └───────┬───────┘                              │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼ (Only summaries/decisions, not raw data)
┌───────────────────────────────────────────────────────────────────┐
│                    PLATFORM ZONE                                   │
│              (Our cloud infrastructure)                            │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │ Orchestration│  │   Platform   │  │    Team      │            │
│  │    Logic     │  │ Intelligence │  │  Templates   │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└───────────────────────────────────────────────────────────────────┘
```

---

## Access Control

### Layered Approach

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: Platform RBAC                                          │
│  • Platform Admin: Full system access                            │
│  • Org Admin: Manage their organization                          │
│  • Department Manager: Manage their department's teams           │
│  • Team Operator: Run and interact with assigned teams           │
│  • Viewer: Read-only access to outputs                           │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 2: Department Isolation                                   │
│  • Users only see their department's data                        │
│  • Cross-department access requires explicit grant               │
│  • Department Head Agent respects these boundaries               │
├─────────────────────────────────────────────────────────────────┤
│  LAYER 3: Custom Rules (ABAC)                                    │
│  • Fine-grained rules based on attributes                        │
│  • Example: "Claims over $50k require Manager approval"          │
│  • Example: "PII access only for HR-tagged users"                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Audit & Compliance

### Dual Audit Trail

**For Development Team (Full Replay):**
```python
class FullAuditEntry(BaseModel):
    timestamp: datetime
    session_id: str
    agent_id: str

    # Full trace
    input_received: Any
    thought_process: str  # Internal reasoning
    tool_calls: List[ToolCall]
    tool_results: List[ToolResult]
    output_produced: Any

    # State
    passport_before: Passport
    passport_after: Passport
    checkpoint_id: str
```

**For Customer (Decision Log):**
```python
class DecisionLogEntry(BaseModel):
    timestamp: datetime
    decision_type: str

    # What was decided
    summary: str
    outcome: str

    # Justification
    key_factors: List[str]
    confidence: ConfidenceVector
    evidence_summary: str

    # Accountability
    agent_responsible: str
    human_override: Optional[str]

    # Traceability
    related_items: List[str]  # IDs of related work items
```

### Compliance Features

| Requirement | Implementation |
|-------------|----------------|
| Data Retention | Configurable retention policies per data type |
| Right to Delete | Cascade deletion with audit trail |
| Access Logging | All data access logged with user/purpose |
| Encryption | At rest (AES-256) and in transit (TLS 1.3) |
| Audit Export | On-demand export for external auditors |

---

## Technology Stack

### Core Platform

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Orchestration | LangGraph | Checkpoint-based state, fault tolerance |
| Memory | ChromaDB + Neo4j | Vector search + knowledge graph (HippoRAG pattern) |
| State Schema | Pydantic | Type safety, validation, serialization |
| API Layer | FastAPI | Async, OpenAPI spec, modern Python |
| Message Queue | Redis Streams | Fast, reliable, supports pub/sub |
| Database | PostgreSQL | Relational data, JSONB for flexibility |
| Object Storage | S3-compatible | Documents, artifacts, audit logs |

### AI Models

| Use Case | Initial | Future |
|----------|---------|--------|
| Orchestration | Claude API | Fine-tuned local option |
| Specialists | Claude/GPT API | Mixed based on task |
| Librarian | Gemini (1M context) | Keep cloud (context size) |
| Voice | Whisper + TTS API | Local whisper option |
| Embeddings | OpenAI/Voyage | Local sentence-transformers |

### Infrastructure

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Containers | Docker + Kubernetes | Standard, portable |
| Sandbox | E2B initially, Firecracker later | Security isolation |
| Telephony | Twilio | Proven, reliable |
| Monitoring | Prometheus + Grafana | Industry standard |
| Logging | ELK Stack or Loki | Searchable logs |

---

## Service Tiers

### Tier 1: Setup + Support
- Embedded team builds custom teams
- Training for basic modifications
- Ongoing support and maintenance
- Best for: Departments wanting ownership

### Tier 2: Managed Templates
- Pre-built templates for common workflows
- Customer configures, we maintain
- Regular updates and improvements
- Best for: Standard administrative tasks

### Tier 3: Full Managed Service
- We run everything
- Customer gets outputs and dashboards
- Continuous optimization by our team
- Best for: End-state "OS for government" vision

---

## Implementation Phases

### Phase 1: Core Foundation + Legal Research Test (8-10 weeks)
**Goal:** Working team system validated with Legal Research test harness

- [ ] LangGraph state machine with Passport schema
- [ ] Base agent class with confidence tracking
- [ ] Legal Research Team (5 agents) as system test
- [ ] Basic memory (ChromaDB) with multi-resolution content
- [ ] Simple web UI for testing
- [ ] Audit logging

**Deliverable:** Legal Research Team processing test requests successfully

**Validation:** Multi-agent pipeline works, state passes correctly, memory persists

### Phase 2: Safety Team + Inspection App (6-8 weeks)
**Goal:** Real-world deployable Safety Team

- [ ] Safety Team specification (based on founder expertise)
- [ ] Inspection App (mobile-friendly, field-usable)
- [ ] Safety-specific agents (Inspector, Report Writer, Scheduler, etc.)
- [ ] Integration with inspection checklists and standards
- [ ] Real-world testing with founder's contacts

**Deliverable:** Safety Team + App ready for consulting firm launch

**Validation:** Real inspectors can use it in the field

### Phase 3: Consulting Firm Launch (Ongoing)
**Goal:** Revenue generation via safety inspection services

- [ ] Consulting firm legal setup
- [ ] Initial client engagements (Martinez Act opportunity)
- [ ] Iterate based on field feedback
- [ ] Build case studies and performance data

**Deliverable:** Profitable consulting operation

### Phase 4: Risk Management Department Product (6-8 weeks)
**Goal:** Packaged Risk Management department for small counties

- [ ] Full Risk Management Team suite
- [ ] Incident Investigation Team
- [ ] Claims Processing Team
- [ ] Compliance Monitoring Team
- [ ] Analytics & Reporting Team
- [ ] Cross-team orchestration

**Deliverable:** Sellable/licensable Risk Management product

### Phase 5: Platform Intelligence (When Needed)
**Goal:** Self-improving platform

- [ ] Janitor per team (observation)
- [ ] Housekeeper (aggregation and proposal)
- [ ] Research Scouts (external knowledge)
- [ ] Proposal queue with human approval

**Timing:** When multiple teams are running in production and manual monitoring becomes burdensome

**Deliverable:** Platform that proposes its own improvements

### Phase 6: TPA Market Entry (Year 2+)
**Goal:** Disrupt the TPA market

- [ ] Claims Team for TPA operations
- [ ] Competitive analysis using public bidding data
- [ ] Pricing model development
- [ ] Initial TPA contracts or partnerships

**Deliverable:** Operational agentic TPA service

---

## Open Items for Further Research

1. **Specific compliance certifications** for government (StateRAMP, SOC2, etc.)
2. **Pricing model** (per-seat, per-team, per-transaction, flat rate?)
3. **Partnership strategy** with government software vendors
4. **Competitive landscape** (who else is doing this?)
5. **Legal structure** for government contracts
6. **Insurance/liability** for AI-made decisions

---

## Success Metrics

### For Customers
- Reduction in incident resolution time
- Reduction in claims costs
- Improved compliance audit scores
- Staff time freed for high-value work

### For Platform
- Customer retention rate
- Net Promoter Score
- Platform improvement proposals approved/implemented
- Research Scout signal quality

---

*Version: 2.0*
*Created: 2025-01-05*
*Updated: 2025-01-06*

---

## Changelog

### v2.0 (2025-01-06)
- Rewrote Vision Statement to distinguish near-term (Safety Consulting) from long-term (County OS)
- Added Founder Advantages section
- Added Market Entry Strategy with 4-phase progression (Safety Consulting → Risk Dept → TPA → Investment)
- Added Development Strategy explaining Legal Research as test harness, Safety Team as first deployment
- Restructured Implementation Phases to prioritize Safety Team
- Added Martinez Act opportunity context

### v1.0 (2025-01-05)
- Initial plan from multi-model synthesis + founder interview
