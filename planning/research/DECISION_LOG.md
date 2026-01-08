# Decision Log

*Systematic analysis of design decisions arising from scenario walkthroughs*

## Methodology

For each decision point:
1. **State the question clearly**
2. **List options** (including "solve via team structure" or "defer")
3. **Evaluate against principles** (fractal, hub-spoke, auditability, simplicity)
4. **Consider downstream implications**
5. **Recommend or flag for deeper analysis**

## Our Principles (Reference)

From architecture and UNI-Q spec:
1. Multi-tenant from day one
2. Passport is the state
3. Hub-and-spoke communication (orchestrator routes, specialists don't talk directly)
4. Evidence-based confidence
5. External validation required
6. De-scaffolding (start structured, earn autonomy)
7. Fractal architecture (same pattern at every level)
8. Three-tier resolution (micro/summary/full)
9. Subscriptions for message routing

---

## Decision Points

| # | Question | Category | Status |
|---|----------|----------|--------|
| DP-01 | Cross-team request/response pattern | Communication | ✓ Decided |
| DP-02 | External data ingestion | Infrastructure | Pending |
| DP-03 | Artifact/document storage | Infrastructure | Pending |
| DP-04 | Human escalation protocol | Communication | Pending |
| DP-05 | External transmission (outbound) | Infrastructure | Pending |
| DP-06 | Time-based event handling | Infrastructure | Pending |
| DP-07 | Template management | Data | Pending |
| DP-08 | Financial operations ownership | Team Structure | Pending |
| DP-09 | Metrics and analytics | Infrastructure | Pending |
| DP-10 | Job lifecycle state machine | Data | Pending |

---

## DP-01: Cross-Team Request/Response Pattern

**Source:** Scenario Stage 4 (OHS → Legal for citations)

### Question

When one team needs something from another team (e.g., OHS needs legal citations from Legal), what communication pattern should be used?

### Context

- OHS has 5 findings needing OSHA code citations
- Legal will look them up and return formatted citations
- This is a discrete request/response, not ongoing collaboration
- Interaction is relatively short-lived

### Options

**Option A: Full Mission Sandbox**

Same pattern as any cross-team work. Spin up sandbox, route through department orchestrator, close when done.

**Option B: Consultation Pattern (Separate Concept)**

New lighter-weight pattern specifically for quick request/response. Different from sandbox.

**Option C: Parameterized Sandbox**

Keep sandbox as the only cross-team pattern, but allow sandboxes to have a "weight" or "complexity" parameter (light/standard/heavy).

**Option D: Solve via Team Structure**

Perhaps Legal Team has a "citation service" that operates differently? Or OHS has a legal-liaison agent?

### Principle Evaluation

| Principle | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Fractal (same pattern everywhere) | ✓ | ✗ | ✓ | ? |
| Hub-spoke (orchestrator routes) | ✓ | ✓ | ✓ | ? |
| Auditability (uniform trail) | ✓ | ✗ | ✓ | ? |
| Simplicity (fewer concepts) | ✓ | ✗ | ~ | ✗ |
| Efficiency (low overhead) | ? | ✓ | ✓ | ? |

### Downstream Implications

**If Option B (separate Consultation pattern):**
- Every cross-team interaction requires pattern choice: "sandbox or consultation?"
- Creates ongoing decision overhead
- Audit trails have two structures
- Must define the boundary (what qualifies as "consultation"?)
- Risk of pattern proliferation

**If Option A/C (always sandbox):**
- One pattern to learn, one audit structure
- Question becomes: is sandbox overhead acceptable?
- If overhead is the concern, make sandboxes cheaper (Option C)

**If Option D (team structure):**
- Pushes complexity into team design
- May create inconsistency across teams
- Harder to reason about system behavior

### Analysis

The concern driving Option B was "a sandbox seems heavy for a quick citation request."

But what is the actual overhead of a sandbox?
- Create sandbox record (database write)
- Set up subscription routing (orchestrator config)
- Message thread storage (already needed)
- Cleanup on completion (automated)

This is not expensive. The "weight" is perception, not reality.

The real cost of Option B is cognitive: everyone must learn two patterns and know when to use which. That's a tax paid on every interaction, forever.

**Key insight:** Don't optimize for sandbox creation overhead. Optimize for cognitive simplicity of one pattern.

### Decision

**Option C: Parameterized Sandbox** (or Option A if we find parameters unnecessary)

All cross-team interactions use sandboxes. Sandboxes can be "light" (minimal context, auto-close) or "standard" (shared workspace, manual close). The parameter can potentially be inferred from request type.

```python
class MissionSandbox(BaseModel):
    complexity: Literal["light", "standard"] = "light"
    # light: auto-close on response, minimal shared context
    # standard: persistent workspace, manual close
    auto_close_on: str | None = None  # e.g., "Ⓥcitations·{mission_id}✓"
```

**Rationale:**
- Preserves fractal consistency
- Uniform audit trail
- One pattern to learn
- "Light" sandboxes address efficiency concerns
- Auto-close can be pattern-matched from the request type

---

## DP-02: External Data Ingestion

**Source:** Scenario Stage 1 (Inspection App → System)

### Question

How does data from external systems (apps, APIs, human uploads) enter our agent system and trigger mission creation?

### Context

- Inspector uses mobile app to collect data/photos in the field
- Data needs to enter our system
- This should trigger mission creation
- OHS Team should receive the intake

### Options

**Option A: External Gateway Service**

Dedicated service/component that:
- Receives external data (API endpoints)
- Validates and sanitizes input
- Stores artifacts
- Creates mission record
- Sends intake message to appropriate team

**Option B: Orchestrator Handles External Input**

Department or Team Orchestrator has external-facing endpoints that receive and process external data directly.

**Option C: Human-Mediated Intake**

External data goes to a human operator who reviews and submits to the system. System only receives human-validated input.

**Option D: Dedicated Intake Agent**

Each team has an "Intake Agent" that handles external input for that team. Not a shared service.

### Principle Evaluation

| Principle | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Hub-spoke | ✓ Gateway → Orch | ~ Orch is exposed | ✓ Human → Orch | ✓ Agent → Orch |
| Security | ✓ Single boundary | ✗ Multiple surfaces | ✓ Human validates | ~ Per-team surface |
| Simplicity | ✓ One entry point | ✗ Orchestrators do too much | ~ Manual step | ~ Duplicated logic |
| Scalability | ✓ | ~ | ✗ Bottleneck | ✓ |
| Auditability | ✓ All external input logged | ✓ | ✓ | ✓ |

### Downstream Implications

**If Option A (Gateway):**
- Clear boundary between external and internal
- Single place for authentication, rate limiting, validation
- Gateway needs routing logic to know which team gets what
- New infrastructure component

**If Option B (Orchestrator exposure):**
- Orchestrators become more complex
- Multiple attack surfaces
- Less separation of concerns

**If Option C (Human-mediated):**
- Safe but doesn't scale
- Good for early phase, problematic later
- Could be a "de-scaffolding" pattern (start here, remove later)

**If Option D (Intake agents):**
- Each team defines its own intake
- Flexible but potentially inconsistent
- Duplicated validation logic

### Analysis

This maps to a classic architectural question: where is the boundary?

The hub-spoke principle suggests orchestrators are internal coordinators, not external interfaces. Exposing them externally (Option B) violates this separation.

Option A (Gateway) aligns with:
- Single entry point for security
- Separation of concerns
- Clear external/internal boundary

Option C (Human-mediated) aligns with:
- De-scaffolding principle (start constrained)
- Early-phase risk mitigation
- Can be relaxed later

**Hybrid possibility:** Start with Option C (human-mediated intake via Gateway UI), evolve to Option A (automated Gateway API) as trust is established.

### Decision

**Option A: External Gateway Service** with **phased implementation**

Phase 1: Gateway with human review UI (de-scaffolding)
- External data → Gateway → Human review queue → Mission creation

Phase 2: Gateway with automated intake for trusted sources
- Known apps/APIs → Gateway → Auto-validation → Mission creation
- Unknown sources → Human review queue

```python
class ExternalGateway:
    """Boundary between external world and agent system."""

    async def receive(
        self,
        source: str,
        source_type: Literal["api", "upload", "integration"],
        payload: dict,
        artifacts: list[bytes],
        trust_level: Literal["verified", "unverified"]
    ) -> str:
        """
        Receive external input.
        Returns intake_id for tracking.
        """
        if trust_level == "unverified":
            return await self.queue_for_review(...)
        else:
            return await self.create_mission(...)
```

**Rationale:**
- Clean external/internal separation
- Single security boundary
- Supports de-scaffolding (human review → automated)
- Aligns with hub-spoke (Gateway routes to Orchestrators)

---

## DP-03: Artifact/Document Storage

**Source:** Scenario Stages 3, 6, 9 (findings, reports, transmissions)

### Question

Where do documents, photos, reports, and other artifacts live? How are they referenced in UNI-Q messages vs. stored in full?

### Context

- Inspection photos (binary, possibly large)
- Findings details (structured data)
- Report drafts and finals (documents)
- Invoices (documents)
- Need to be: stored, versioned, retrieved, transmitted

UNI-Q micro messages should reference artifacts, not contain them:
```
Ⓥfindings·inspection-2024-0089✓⟨artifact:findings-ref-002⟩
```

### Options

**Option A: Dedicated Artifact Store Service**

Shared service that stores and retrieves artifacts. All teams use the same store.

**Option B: Per-Mission Artifact Storage**

Artifacts stored within the mission sandbox. Each sandbox has its own artifact space.

**Option C: External Document Management**

Use external system (S3, SharePoint, etc.) and store references.

**Option D: Hybrid - Hot/Cold Storage**

Active mission artifacts in Option B, archived artifacts in Option C.

### Principle Evaluation

| Principle | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Multi-tenant | Must enforce | Natural isolation | Depends on system | Natural in hot |
| Auditability | Central logging | Per-sandbox logging | External logs | Split logging |
| Simplicity | One store | Distributed | External dependency | Complex |
| Scalability | Must scale store | Scales with sandboxes | Externally scaled | Good |

### Analysis

Key questions:
1. **Isolation:** Should Team A ever see Team B's artifacts? (Usually no)
2. **Sharing:** Can artifacts be shared across teams in a mission? (Yes, in cross-team sandboxes)
3. **Retention:** How long do artifacts need to live? (Government = long)
4. **Size:** How big are artifacts? (Photos could be large)

Option B (per-mission) provides natural isolation and fits the sandbox model. But cross-team sandboxes need shared artifact access.

Option A (central store) requires explicit access control but enables sharing.

**Insight:** Artifacts belong to missions, not teams. A mission sandbox (even cross-team) should have a unified artifact space. This is already implicit in our sandbox design.

```python
class MissionSandbox(BaseModel):
    shared_artifacts: dict[str, str]  # Already in our model!
```

The question is: where does `shared_artifacts` actually store data?

### Decision

**Option B with Central Backing Store**

- Artifacts are logically scoped to missions (sandbox artifact space)
- Physically stored in a central artifact service
- Access controlled by mission membership
- References use mission-scoped URIs

```
artifact:inspection-2024-0089/findings-001
artifact:inspection-2024-0089/report-draft-v2
artifact:inspection-2024-0089/photo-warehouse-b-001
```

```python
class ArtifactStore:
    """Central artifact storage with mission-scoped access."""

    async def store(
        self,
        mission_id: str,
        artifact_type: str,
        content: bytes,
        metadata: dict
    ) -> str:
        """Store artifact, return reference URI."""

    async def retrieve(
        self,
        artifact_ref: str,
        requesting_agent: str
    ) -> bytes:
        """Retrieve artifact if agent has mission access."""

    async def list_artifacts(
        self,
        mission_id: str
    ) -> list[ArtifactMetadata]:
        """List all artifacts in a mission."""
```

**Rationale:**
- Mission-scoped aligns with sandbox model
- Central store enables operational concerns (backup, retention)
- Access control via mission membership (already defined)
- Clean URI scheme for references in UNI-Q

---

## DP-04: Human Escalation Protocol

**Source:** Scenario Stage 8 (Report signoff)

### Question

How do agents escalate work to humans, and how do human responses return to the agent system?

### Context

- Report needs human approval before transmission
- Human may approve, reject, or request revisions
- Agent needs to wait for and receive human response
- Must track who approved what for audit

### Options

**Option A: Escalation as Message to Human "Agent"**

Treat humans as special agents in the system. Escalation is a message to `Ⓗhuman-role`.

**Option B: Escalation Queue Service**

Dedicated service that manages human work queues. Agents submit to queue, humans work from queue, responses route back.

**Option C: External Ticketing System**

Integrate with external system (Jira, ServiceNow). Escalation creates ticket, resolution closes ticket.

**Option D: Orchestrator Holds Pending Human Action**

Orchestrator maintains escalation state and presents to humans via UI. Orchestrator handles response routing.

### Principle Evaluation

| Principle | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Fractal | ✓ Human as agent | ~ New service | ✗ External pattern | ~ Orch does more |
| Hub-spoke | ✓ Message routing | ✓ | ✗ | ✓ |
| Auditability | ✓ Same trail | ✓ | External trail | ✓ |
| Simplicity | ✓ Unified model | ~ New component | ✗ Integration | ~ |

### Analysis

Option A is elegant: humans are just slow, expensive agents with special capabilities. The fractal model holds.

```
Ⓐohs-orch → Ⓗsignoff-authority: Ⓔescalation·signoff⟨mission:X·artifact:report-ref⟩
Ⓗsignoff-authority → Ⓐohs-orch: Ⓥsignoff·X✓⟨approved-by:jane-doe·timestamp:...⟩
```

This preserves:
- Same message format
- Same routing through orchestrator
- Same audit trail structure
- Same subscription model

The `Ⓗ` symbol already proposed fits this model.

**Implementation:** Human "agents" have a UI that shows their inbox (subscribed messages) and lets them respond. The UI is the human's "runtime."

### Decision

**Option A: Humans as Special Agents**

Humans participate in the message system as agents with the `Ⓗ` symbol. They receive messages based on subscriptions (role-based), and their responses are messages back.

```python
class HumanAgent:
    """Human participant in the agent system."""
    agent_id: str  # e.g., "Ⓗjane-doe" or "Ⓗsignoff-authority"
    role: str
    subscriptions: list[str]  # What messages they see
    inbox: list[Message]  # Pending items

class EscalationMessage:
    """Message to human requiring action."""
    escalation_type: Literal["approval", "decision", "review", "exception"]
    context_summary: str  # Human-readable summary
    artifact_refs: list[str]  # What to review
    allowed_actions: list[str]  # What human can do
    deadline: datetime | None
```

**UI Requirements:**
- Human inbox showing pending escalations
- Artifact viewer (reports, documents)
- Action buttons (approve, reject, revise)
- Response capture with audit trail

**Rationale:**
- Fractal consistency (humans are agents)
- Unified audit trail
- Same routing/subscription model
- Clean conceptual model

---

## DP-05: External Transmission (Outbound)

**Source:** Scenario Stages 9, 11 (Send report, send invoice to client)

### Question

How do agents send communications/documents to external parties (clients, vendors, etc.)?

### Context

- Approved report must be sent to county client
- Invoice must be sent to county client
- May use email, portal upload, API, or other channels
- Delivery confirmation needed
- Audit trail required

### Options

**Option A: External Gateway (Outbound)**

Same Gateway service handles outbound as inbound. Bidirectional external interface.

**Option B: Dedicated Transmission Service**

Separate service for outbound communications with channel adapters (email, portal, etc.).

**Option C: Human-Mediated Transmission**

Agent prepares transmission, human actually sends it (via normal email, portal, etc.).

**Option D: Per-Channel Agents**

Specialized agents for each channel (EmailAgent, PortalAgent, etc.).

### Principle Evaluation

| Principle | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Simplicity | ✓ One boundary | ~ Two services | ~ Manual step | ✗ Many agents |
| Hub-spoke | ✓ Gateway routes out | ✓ | ✓ Human routes | ✓ Orch routes |
| De-scaffolding | Compatible | Compatible | ✓ Start here | Compatible |
| Auditability | ✓ Central | ✓ | ~ Human action logged | ✓ |

### Analysis

Option A (Gateway handles both directions) is clean:
- Single external/internal boundary
- Symmetric design
- One place for external authentication, logging

Like inbound, we might want human-mediated transmission initially (de-scaffolding), then automate.

### Decision

**Option A: Bidirectional External Gateway**

Gateway handles both inbound and outbound. Outbound follows same de-scaffolding pattern.

```python
class ExternalGateway:
    # Inbound (from DP-02)
    async def receive(...) -> str: ...

    # Outbound
    async def transmit(
        self,
        destination_type: Literal["email", "portal", "api"],
        recipient: ExternalRecipient,
        artifact_refs: list[str],
        message_template: str,
        require_human_review: bool = True  # De-scaffolding
    ) -> TransmissionReceipt:
        """
        Send artifacts to external recipient.
        Returns receipt with delivery status.
        """
```

**UNI-Q symbol:** `Ⓖ` for Gateway

```
Ⓐohs-orch → Ⓖgateway: Ⓣtransmit⟨to:county-X·channel:portal·artifact:report-final⟩
Ⓖgateway → Ⓐohs-orch: Ⓥtransmitted✓⟨receipt:TXN-001·delivered:true⟩
```

---

## DP-06: Time-Based Event Handling

**Source:** Scenario Stage 12 (Payment tracking, reminders)

### Question

How does the system handle scheduled events, reminders, deadlines, and time-based triggers?

### Context

- Payment due in 30 days, reminder at 30, escalation at 60
- Deadlines for responses
- Recurring checks (e.g., daily aging report)
- Time-based state transitions

### Options

**Option A: Temporal Trigger Service**

Dedicated service that manages scheduled events. Fires UNI-Q messages when triggers activate.

**Option B: Orchestrator-Managed Timers**

Orchestrators maintain their own timers and fire events when due.

**Option C: External Scheduler**

Use external scheduler (cron, cloud scheduler) to trigger system endpoints.

**Option D: Polling Pattern**

Agents periodically check for time-based conditions.

### Principle Evaluation

| Principle | Option A | Option B | Option C | Option D |
|-----------|----------|----------|----------|----------|
| Simplicity | ~ New service | ~ Orch complexity | ~ External dep | ✗ Inefficient |
| Hub-spoke | ✓ Service → Orch | ✓ | ✓ | ✓ |
| Auditability | ✓ Trigger logged | ✓ | ~ External | ~ |
| Reliability | ✓ Dedicated | ~ Orch restart? | ✓ | ~ |

### Analysis

Time-based events need reliability. If orchestrator restarts, it must remember pending timers. This suggests persistent timer storage.

Option A (dedicated service) is cleaner:
- Single responsibility
- Persistent timer storage
- Clear interface (register timer, cancel timer, timer fires message)

### Decision

**Option A: Temporal Trigger Service**

Dedicated service for time-based events. Timers are persistent. When triggered, sends UNI-Q message to specified recipient.

```python
class TemporalTrigger(BaseModel):
    trigger_id: str
    mission_id: str
    fire_at: datetime
    message: str  # UNI-Q message to send
    target: str  # Recipient (agent/orchestrator)
    repeat: Literal["once", "daily", "weekly"] = "once"
    cancel_on: list[str]  # Message patterns that cancel this trigger

class TemporalService:
    async def schedule(self, trigger: TemporalTrigger) -> str:
        """Schedule a trigger, return trigger_id."""

    async def cancel(self, trigger_id: str) -> bool:
        """Cancel a scheduled trigger."""

    async def cancel_on_event(self, message: str):
        """Check if any triggers should be cancelled by this message."""
```

**Example:**
```python
# When invoice is sent, schedule payment reminders
await temporal.schedule(TemporalTrigger(
    mission_id="inspection-2024-0089",
    fire_at=invoice_date + timedelta(days=30),
    message="Ⓣpayment-reminder⟨mission:inspection-2024-0089·days:30⟩",
    target="Ⓐar-agent",
    cancel_on=["Ⓥpayment-received·inspection-2024-0089*"]
))
```

---

## DP-07: Template Management

**Source:** Scenario Stage 6 (Report template)

### Question

How are document templates (inspection reports, invoices, etc.) stored, versioned, and filled?

### Options

**Option A: Template Registry Service**

Dedicated service managing templates. Stores templates, handles versioning, provides fill/render API.

**Option B: Templates as Artifacts**

Templates stored in Artifact Store like any other artifact. Agents retrieve and fill them.

**Option C: Per-Team Template Management**

Each team manages its own templates. No shared infrastructure.

### Analysis

Templates are a special kind of artifact:
- Versioned (report template v3.2)
- May have client-specific variants
- Filled with data to produce documents
- Need schema (what fields are required)

Option B (templates as artifacts) is simple but doesn't handle:
- Version management
- Field schema
- Fill/render logic

Option A (dedicated service) provides:
- Version management
- Schema validation
- Render engine
- Variant management (client-specific)

### Decision

**Option A: Template Registry Service**

Templates are managed artifacts with version control and rendering capability.

```python
class Template(BaseModel):
    template_id: str
    name: str
    version: str
    content_type: Literal["docx", "html", "pdf"]
    schema: dict  # Required fields
    variants: dict[str, str]  # client_id -> variant_version

class TemplateRegistry:
    async def get_template(
        self,
        template_id: str,
        client_id: str | None = None
    ) -> Template:
        """Get template, using client variant if exists."""

    async def render(
        self,
        template_id: str,
        data: dict,
        output_format: str = "pdf"
    ) -> bytes:
        """Fill template with data, return rendered document."""
```

**Note:** This could be part of Artifact Store rather than separate service. Decision on service boundaries can be deferred.

---

## DP-08: Financial Operations Ownership

**Source:** Scenario Stages 10-15 (Invoice, payment, tax, reconciliation)

### Question

Who handles financial operations - invoicing, payment tracking, tax allocation, account reconciliation? Is this a team or a service?

### Options

**Option A: Finance Team**

Dedicated agent team with specialists: Invoice Agent, AR Agent, Tax Agent, Reconciliation Agent.

**Option B: C-Suite Team Handles Finance**

C-Suite team (management/executive oversight) includes financial operations.

**Option C: Financial Operations as Services**

Not a team - just services that teams call (Invoice Service, Payment Service, etc.).

**Option D: Per-Team Financial Agents**

Each operational team has its own finance-related agents.

### Analysis

Financial operations are:
- Cross-cutting (every team generates revenue)
- Specialized (tax rules, accounting standards)
- Compliance-sensitive (audit requirements)
- Consistent (same invoice format across teams)

Option D (per-team) would duplicate logic and risk inconsistency.

Option C (services only) misses the coordination aspect - who decides when to escalate collections? Who reconciles discrepancies?

Option A (Finance Team) fits our model:
- Team orchestrator coordinates financial workflows
- Specialist agents handle specific tasks
- Cross-team sandbox for mission handoff (OHS → Finance)
- Humans can be in the loop for approvals

Option B (C-Suite handles it) conflates oversight with operations. C-Suite should monitor, not execute.

### Decision

**Option A: Finance Team**

Dedicated Finance Team with:
- Finance Orchestrator
- Invoice Agent (generates invoices)
- AR Agent (tracks receivables, sends reminders)
- Payment Agent (matches payments to invoices)
- Tax Agent (calculates and allocates taxes)
- Reconciliation Agent (updates accounts)

**Team interactions:**
- Operational teams (OHS, Legal) send billing requests to Finance
- Finance processes through to payment
- Finance reports metrics to C-Suite
- C-Suite provides oversight, not execution

```
Ⓐohs-orch → Ⓐdept-orch: Ⓣbilling-request⟨mission:X·scope-ref:Y⟩
Ⓐdept-orch → Ⓐfinance-orch: Ⓣbilling-request⟨from:ohs·mission:X⟩
```

---

## DP-09: Metrics and Analytics

**Source:** Scenario Stage 16 (Compare against projections)

### Question

How are business metrics collected, aggregated, and reported?

### Options

**Option A: Metrics as Events**

All significant events emit metrics. Analytics service aggregates.

**Option B: Periodic Reporting Agents**

Agents periodically generate reports from system state.

**Option C: External Analytics**

Export data to external analytics system (Metabase, Looker, etc.).

### Analysis

Metrics needs:
- Real-time operational metrics (how many missions active)
- Historical trends (revenue by month)
- Goal tracking (retention rate vs target)
- Alerting (anomaly detection)

Option A (events) enables real-time and historical. Events are immutable, can be replayed.

Option C (external) may be needed for visualization but doesn't solve collection.

### Decision

**Option A: Metrics as Events** with optional external export

Significant events emit metric records. Metrics service aggregates. Can export to external visualization.

```python
class MetricEvent(BaseModel):
    event_type: str
    mission_id: str | None
    team_id: str
    dimensions: dict  # Filterable attributes
    measures: dict    # Numeric values
    timestamp: datetime

# Examples
MetricEvent(
    event_type="mission_completed",
    mission_id="inspection-2024-0089",
    team_id="ohs_team",
    dimensions={"mission_type": "facility_inspection", "client": "county-X"},
    measures={"duration_days": 12, "findings_count": 5}
)

MetricEvent(
    event_type="revenue_recognized",
    mission_id="inspection-2024-0089",
    team_id="finance_team",
    dimensions={"revenue_type": "consulting"},
    measures={"gross": 4500, "net": 4050}
)
```

**UNI-Q symbol:** `Ⓜ` for Metric

```
Ⓜmetric·mission-completed⟨team:ohs·type:facility-inspection·duration:12d⟩
```

---

## DP-10: Job Lifecycle State Machine

**Source:** Full scenario workflow

### Question

Should job/mission state be explicit (state machine) or implicit (derived from message history)?

### Options

**Option A: Explicit State Machine**

Mission has explicit `status` field with defined states and transitions.

**Option B: Implicit State (Event Sourcing)**

State is derived from message history. "Current state" is computed, not stored.

**Option C: Hybrid**

Explicit status for high-level state, implicit for details.

### Analysis

Government audit requirements favor explicitness. Auditors want to see "what state was this mission in at time T?"

Event sourcing (Option B) is powerful but complex. Adds cognitive overhead.

Option A (explicit state machine) is:
- Clear for auditors
- Easier to query ("show all missions in PAYMENT_PENDING")
- Simpler to implement
- Can still have event history for detail

### Decision

**Option A: Explicit State Machine**

Missions have explicit status. Transitions are logged. Event history provides detail.

```python
class MissionStatus(str, Enum):
    INTAKE = "intake"
    PROCESSING = "processing"
    PENDING_EXTERNAL = "pending_external"  # Waiting on cross-team
    PENDING_HUMAN = "pending_human"        # Waiting on human
    DELIVERABLE_READY = "deliverable_ready"
    DELIVERED = "delivered"
    INVOICED = "invoiced"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    CLOSED = "closed"
    # Exception states
    BLOCKED = "blocked"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"

class Mission(BaseModel):
    mission_id: str
    status: MissionStatus
    status_detail: str | None  # e.g., "waiting on legal citations"
    status_changed_at: datetime
    # ... other fields
```

---

## Summary of Decisions

| # | Decision | Solution |
|---|----------|----------|
| DP-01 | Cross-team pattern | Parameterized Sandbox (always sandbox, can be "light") |
| DP-02 | External ingestion | Gateway service with de-scaffolding (human review → auto) |
| DP-03 | Artifact storage | Mission-scoped, central backing store |
| DP-04 | Human escalation | Humans as special agents (Ⓗ symbol) |
| DP-05 | External transmission | Bidirectional Gateway (Ⓖ symbol) |
| DP-06 | Time-based events | Temporal Trigger Service |
| DP-07 | Template management | Template Registry (versioned, renderable) |
| DP-08 | Financial operations | Finance Team (not just services) |
| DP-09 | Metrics | Events with Ⓜ symbol, aggregation service |
| DP-10 | Job lifecycle | Explicit state machine |

## New UNI-Q Symbols

| Symbol | Type | Description |
|--------|------|-------------|
| `Ⓗ` | Human | Human agent (escalation target) |
| `Ⓖ` | Gateway | External interface |
| `Ⓜ` | Metric | Analytics event |

## New Infrastructure Components

1. **External Gateway** - Bidirectional external interface
2. **Artifact Store** - Mission-scoped document/file storage
3. **Temporal Service** - Scheduled triggers and timers
4. **Template Registry** - Document template management
5. **Metrics Service** - Event aggregation and analytics

## New Team

- **Finance Team** - Invoice, AR, Payment, Tax, Reconciliation agents

---

*Document created: 2025-01-08*
*Based on: SCENARIO_OHS_INSPECTION.md*
