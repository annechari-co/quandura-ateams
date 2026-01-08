# UNI-Q: Agent Communication Spec

A token-efficient grammar for multi-agent coordination. This document is our implementation reference.

---

## Why This Matters

**Problem**: Agents waste tokens talking to each other in prose.

```
Prose:    "The claims team is actively working on a high-priority task"  (~12 tokens)
UNI-Q:    "Ⓐclaims◉⁺"  (~3-4 tokens)
```

**Benefit**: Fewer tokens = less cost + better attention (model focuses on signal, not filler).

---

## Core Concepts

### 1. Multi-Resolution Memory ("Zoom-In")

Every piece of information exists at 3 levels:

| Level | Size | When to Use |
|-------|------|-------------|
| **micro** | ~20 tokens | Scanning many items |
| **summary** | ~100 tokens | Reasoning about an item |
| **full** | unlimited | Deep dive, drafting, auditing |

**Example - Same information at each level:**

```
micro:   Ⓣ001✓⟨risk:low·μ:0.7⟩⚐

summary: Contract review complete. Approved with 3 redlines.
         Indemnification capped at $500K per vendor request.
         Re-review recommended if contract exceeds this value.

full:    [Complete review document with all tracked changes,
         legal analysis, vendor correspondence, approval chain...]
```

### 2. Symbolic Encoding

Status, relationships, and workflow states as single symbols:

```
◉ active    ○ idle    ⊘ blocked    ✓ complete    ⚠ error
```

### 3. Structured Tags

Fast filtering without embedding search:

```
⟨customer:042·outcome:approved·tier:vip⟩
```

### 4. Typed Relationships

Links between entities that preserve reasoning chains:

```
Ⓥcall·001 ⊂ Ⓔcustomer·042       (call INVOLVES customer)
Ⓥcall·001 ⊃ Ⓞpolicy·refund      (call APPLIES policy)
Ⓞpolicy·refund ∧ Ⓢgoal·retention (policy ALIGNED WITH goal)
```

---

## Symbol Reference

### Layer Prefixes

| Symbol | Layer | What it represents |
|--------|-------|-------------------|
| Ⓢ | Strategic | Goals, values, priorities |
| Ⓞ | Operational | Policies, rules, procedures |
| Ⓔ | Entity | Customers, vendors, facilities |
| Ⓥ | Event | Calls, decisions, inspections |
| Ⓐ | Agent | Teams, individual agents |
| Ⓣ | Task | Work items, reviews, requests |
| Ⓓ | Document | Contracts, reports, files |

### Status Indicators

| Symbol | State |
|--------|-------|
| ◉ | Active |
| ○ | Idle |
| ⊘ | Blocked |
| ⚠ | Error |
| ✓ | Complete |
| ◐ | Pending |
| ⦿ | Critical + Active |
| ⊗ | Critical + Blocked |

### Priority Modifiers

| Symbol | Priority |
|--------|----------|
| ⁺ | High |
| (none) | Normal |
| ⁻ | Low |

### Trend Indicators

| Symbol | Trend |
|--------|-------|
| ↗ | Improving |
| → | Stable |
| ↘ | Degrading |
| ↯ | Volatile |

### Progress (0-100%)

```
⓪ ① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩
0% 10 20 30 40 50 60 70 80 90 100%
```

### Relationship Operators

| Symbol | Meaning | Example |
|--------|---------|---------|
| → | depends-on | Ⓐlegal→Ⓐcompliance |
| ← | blocks | Ⓐcompliance←Ⓐlegal |
| ↔ | mutual dependency | Ⓐteam-a↔Ⓐteam-b |
| ∼ | related-to | Ⓣtask-1∼Ⓣtask-2 |
| ⊂ | involves | Ⓥcall⊂Ⓔcustomer |
| ⊃ | applies | Ⓥcall⊃Ⓞpolicy |
| ∧ | aligned-with | Ⓞpolicy∧Ⓢgoal |

### Caveat Flags

| Symbol | Meaning | When to use |
|--------|---------|-------------|
| ⚑ | attention needed | General "there's more here" |
| ⚐ | conditional | Approval has conditions |
| ⚠ | risk noted | Risk details in full |
| ⁑ | dissent | Not everyone agreed |
| ⧖ | time-sensitive | Timing details matter |

### Delimiters

| Symbol | Use |
|--------|-----|
| │ | Section separator |
| · | Attribute separator |
| ; | Entity separator |
| ⟨⟩ | Tag grouping |

---

## Message Types

For agent-to-agent communication:

| Symbol | Name | Direction | Use |
|--------|------|-----------|-----|
| S | Status | Up/lateral | Report current state |
| Q | Query | Any | Ask for something |
| D | Delegate | Down | Assign work |
| A | Acknowledge | Response | Confirm receipt |
| N | Notify | To subscribers | Push update |
| R | Result | Response | Deliver outcome |
| ⊕ | Subscribe | To orchestrator | Register for updates |
| ⊖ | Unsubscribe | To orchestrator | Stop updates |
| ✓ | Accept | Response | Confirm acceptance |
| ✗ | Reject | Response | Indicate rejection |

### Message Format

```
HEADER│BODY

Header: msg_type:context_id[:flags]
Body:   entity_list | request | response
```

### Example Workflow

**1. Request** - Claims asks Ops for contract review:
```
Q:wc042│Ⓐclaims→Ⓐops│Ⓣrev·ctr│Ⓔmedimg·mri⟨wc:042·pt:JD·need:vendor-agr⟩
```

**2. Acknowledge** - Ops confirms, routing to Legal:
```
A:wc042│Ⓣrev·ctr·001│◐⟨→Ⓐlegal-b·η4h⟩
```

**3. Subscribe** - Claims wants updates:
```
⊕:wc042│Ⓐclaims│Ⓣ001│◉⊘✓✗
```
"Notify me when task 001 becomes: active, blocked, complete, or rejected"

**4. Notify** - Progress updates:
```
N:wc042│Ⓣ001│Ⓐclaims│◉⑤⟨rev-terms⟩
```
"Task 001 at 50%, reviewing terms"

**5. Result** - Work complete:
```
R:wc042│Ⓣ001│✓⟨approved-Δ·risk:low·∆3⟩→Ⓓctr·001·rev
```
"Complete, approved with changes, low risk, 3 redlines, see document"

---

## Smart Resolution System

### Problem: When Should Agents Zoom In?

Three challenges:
1. Agent doesn't know when micro is insufficient
2. Multiple round-trips to zoom in are slow
3. Micro might hide critical caveats

### Solution 1: Query Intent Determines Resolution

The QUESTION determines resolution, not the data:

| Intent | Resolution | Examples |
|--------|------------|----------|
| `route` | micro | "Where should this go?" |
| `monitor` | micro | "Is anything broken?" |
| `reason` | summary | "Why is X blocked?" |
| `decide` | summary | "Should we approve?" |
| `draft` | full | "Write the response" |
| `audit` | full | "Investigate this" |

**In queries:**
```
Q:wc042:route│...     → micro
Q:wc042:decide│...    → summary
Q:wc042:audit│...     → full
```

### Solution 2: Prefetch Rules

Tell the memory system what you'll probably need:

```python
query = MemoryQuery(
    tags=["team:claims"],
    resolution="micro",
    prefetch=[
        {"condition": "⊘", "resolution": "summary"},  # blocked items
        {"condition": "⚑", "resolution": "summary"},  # flagged items
    ]
)
```

**One round-trip returns:**
- All items at micro
- Summaries pre-loaded for blocked/flagged items

### Solution 3: Micro Confidence Tag

The agent creating micro indicates how complete it is:

```
Ⓣ001✓⟨risk:low·μ:0.95⟩     → micro captures 95%, trust it
Ⓣ001✓⟨risk:low·μ:0.6⟩⚑    → micro captures 60%, zoom if important
```

**Rule**: If `μ < 0.7` AND decision is important → zoom in.

### Solution 4: Resolution Contracts

Define what micro MUST include for each node type:

```python
TaskResultContract = {
    "node_type": "task_result",

    # These always appear in micro
    "micro_guarantees": ["outcome", "risk_level", "owner"],

    # If full contains these, micro MUST have ⚑ flag
    "escalation_triggers": [
        "conditional_approval",
        "exceptions_granted",
        "caveats_noted",
        "risk > medium",
        "reviewer_dissent"
    ]
}
```

**Enforcement**: When writing to memory, if full content triggers escalation, micro MUST include the appropriate flag.

---

## Architecture Stack

```
┌─────────────────────────────────────────────────────────┐
│  QUERY LAYER                                            │
│  Intent (route/decide/audit) → base resolution          │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PREFETCH LAYER                                         │
│  Conditional rules → fetch summaries for flagged items  │
│  Result: micro + relevant summaries in one round-trip   │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  CONTRACT LAYER                                         │
│  Resolution contracts → micro never hides critical info │
│  Escalation triggers → force ⚑⚐⚠ flags                 │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  CONFIDENCE LAYER                                       │
│  μ:X tag → micro-generator's self-assessed coverage     │
│  Low confidence + important decision → zoom             │
└─────────────────────────────────────────────────────────┘
```

---

## Domain Extensions

UNI-Q has a universal core + optional domain vocabularies.

### Core (Everyone Understands)
```
Layers:     Ⓢ Ⓞ Ⓔ Ⓥ Ⓐ Ⓣ Ⓓ
Status:     ◉ ○ ⊘ ⚠ ✓ ◐ ⦿ ⊗
Priority:   ⁺ ⁻
Relations:  → ← ↔ ∼ ⊂ ∧ ⊃
Messages:   S Q D A N R ⊕ ⊖ ✓ ✗
```

### Domain Extensions (Optional)

**Manufacturing (mfg/v1):**
```
⚙ producing   ⏸ changeover   🔧 maintenance
η efficiency  Δ defect_rate  τ throughput
```

**Legal (legal/v1):**
```
⚖ in_review   ✎ drafting   ◈ pending_signature
∆ redline_count   κ compliance_score
```

**Safety (safety/v1):**
```
☢ hazard   ⛑ mitigated   ⚡ active_incident
ρ risk_score   ι inspection_due
```

### How Extensions Work

```
Team (knows legal/v1):     Ⓣrev·001⚖∆3κ92
Division (knows core):     Ⓣrev·001◉⟨redlines:3·compliance:92⟩
HQ (knows core only):      Ⓣrev·001◉
```

Higher levels see less detail but still understand status.

---

## Pydantic Models

### Core Types

```python
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum


class Layer(str, Enum):
    STRATEGIC = "Ⓢ"
    OPERATIONAL = "Ⓞ"
    ENTITY = "Ⓔ"
    EVENT = "Ⓥ"
    AGENT = "Ⓐ"
    TASK = "Ⓣ"
    DOCUMENT = "Ⓓ"


class Status(str, Enum):
    ACTIVE = "◉"
    IDLE = "○"
    BLOCKED = "⊘"
    ERROR = "⚠"
    COMPLETE = "✓"
    PENDING = "◐"
    CRITICAL_ACTIVE = "⦿"
    CRITICAL_BLOCKED = "⊗"


class Priority(str, Enum):
    HIGH = "⁺"
    NORMAL = ""
    LOW = "⁻"


class CaveatFlag(str, Enum):
    ATTENTION = "⚑"
    CONDITIONAL = "⚐"
    RISK = "⚠"
    DISSENT = "⁑"
    TIME_SENSITIVE = "⧖"


class RelationType(str, Enum):
    DEPENDS_ON = "→"
    BLOCKS = "←"
    MUTUAL = "↔"
    RELATED = "∼"
    INVOLVES = "⊂"
    APPLIES = "⊃"
    ALIGNED_WITH = "∧"


class QueryIntent(str, Enum):
    ROUTE = "route"
    MONITOR = "monitor"
    REASON = "reason"
    DECIDE = "decide"
    DRAFT = "draft"
    AUDIT = "audit"


class Resolution(str, Enum):
    MICRO = "μ"
    SUMMARY = "Σ"
    FULL = "F"


RESOLUTION_BY_INTENT = {
    QueryIntent.ROUTE: Resolution.MICRO,
    QueryIntent.MONITOR: Resolution.MICRO,
    QueryIntent.REASON: Resolution.SUMMARY,
    QueryIntent.DECIDE: Resolution.SUMMARY,
    QueryIntent.DRAFT: Resolution.FULL,
    QueryIntent.AUDIT: Resolution.FULL,
}
```

### Memory Node with UNI-Q

```python
class MemoryNode(BaseModel):
    """A node with multi-resolution content."""

    symbol: str                    # "Ⓣrev·ctr·001"
    tenant_id: str
    team_id: str

    # Multi-resolution content
    micro: str                     # UNI-Q format
    summary: str                   # Natural language
    full: str                      # Complete content

    # Quality signals
    micro_confidence: float = 1.0  # How complete is micro? (μ tag)
    caveat_flags: list[CaveatFlag] = []

    # Tags for filtering
    tags: list[str] = []

    # Relationships
    relationships: list["Relationship"] = []


class Relationship(BaseModel):
    target_symbol: str
    relation_type: RelationType
    weight: float = 1.0
```

### Query with Prefetch

```python
class PrefetchRule(BaseModel):
    """Condition for pre-fetching higher resolution."""
    condition: str          # UNI-Q pattern: "⊘", "⚑", etc.
    resolution: Resolution


class MemoryQuery(BaseModel):
    """Query with smart resolution."""

    # What to find
    tags: list[str] | None = None
    symbols: list[str] | None = None
    pattern: str | None = None

    # Resolution control
    intent: QueryIntent = QueryIntent.MONITOR
    resolution: Resolution | None = None  # Override intent-based
    prefetch: list[PrefetchRule] = []

    # Limits
    limit: int = 50


class MemoryQueryResult(BaseModel):
    """Result with pre-fetched content."""

    nodes: list[str]                    # Micro representations
    prefetched: dict[str, str] = {}     # symbol → summary/full
    total_count: int
```

### Resolution Contract

```python
class ResolutionContract(BaseModel):
    """Defines what micro guarantees for a node type."""

    node_type: str

    # Fields that MUST appear in micro
    micro_guarantees: list[str]

    # Conditions that force caveat flags
    escalation_triggers: list[str]


# Example contracts
CONTRACTS = {
    "task_result": ResolutionContract(
        node_type="task_result",
        micro_guarantees=["outcome", "risk_level"],
        escalation_triggers=[
            "conditional_approval",
            "exceptions_granted",
            "risk > medium"
        ]
    ),
    "inspection_finding": ResolutionContract(
        node_type="inspection_finding",
        micro_guarantees=["severity", "location", "status"],
        escalation_triggers=[
            "safety_critical",
            "regulatory_violation",
            "repeat_finding"
        ]
    )
}
```

### Subscription

```python
class Subscription(BaseModel):
    """Who gets notified about what."""

    subscriber: str              # "Ⓐteam·claims"
    target: str                  # "Ⓣrev·ctr·001" or "Ⓐteam·legal·*"
    events: list[str]            # ["◉", "⊘", "✓", "✗"]
    min_priority: Priority = Priority.NORMAL
    resolution: Resolution = Resolution.MICRO
    batch_window_seconds: int = 0  # 0 = immediate
```

---

## Implementation Checklist

### Phase 1: Core Grammar
- [ ] Symbol enums (Layer, Status, Priority, etc.)
- [ ] MemoryNode with micro/summary/full
- [ ] Basic parser: string → MemoryNode
- [ ] Basic serializer: MemoryNode → string

### Phase 2: Smart Resolution
- [ ] QueryIntent enum
- [ ] Resolution mapping by intent
- [ ] Micro confidence tag (μ:X)
- [ ] Caveat flags (⚑⚐⚠⁑⧖)

### Phase 3: Prefetch System
- [ ] PrefetchRule model
- [ ] Query with prefetch conditions
- [ ] Memory API batch retrieval
- [ ] Result with prefetched content

### Phase 4: Contracts
- [ ] ResolutionContract model
- [ ] Contract registry per node type
- [ ] Enforcement on write (flag if escalation triggered)
- [ ] Validation on read (warn if low confidence unflagged)

### Phase 5: Messaging
- [ ] Message types (S, Q, D, A, N, R, ⊕, ⊖, ✓, ✗)
- [ ] Message parser
- [ ] Subscription registry
- [ ] Notification routing

### Phase 6: Domain Extensions
- [ ] Extension registry
- [ ] Domain-specific symbol sets
- [ ] Roll-up/translation between extension levels

---

## Fractal Architecture

UNI-Q applies the same patterns at every organizational level. This creates a "fractal" system where the communication model is identical whether you're looking at departments, teams, or individual agents.

### Principle: Same Pattern at Every Level

| Level | Publisher | Hub (Router) | Subscribers |
|-------|-----------|--------------|-------------|
| Department | Team Orchestrators | Dept Head | Other Team Orchestrators |
| Team | Specialist Agents | Team Orchestrator | Other Specialists |
| Agent | Sub-tasks | Agent | Sub-task handlers |

At every level:
- Same UNI-Q micro format for messages
- Same subscription mechanism for routing
- Same resolution system (micro/summary/full)
- Hub-and-spoke discipline maintained (orchestrator routes all messages)

### Why Fractal?

1. **One pattern to implement** - Subscription/routing logic is identical everywhere
2. **One pattern to debug** - Same tools work at every level
3. **Composable** - A team can be treated as an "agent" at department level
4. **Emergent scaling** - Add sub-teams without new patterns

---

## Mission Sandboxes

Cross-team transactions spin up their own sandbox - an isolated context shared only by teams working on that specific transaction.

### What is a Mission Sandbox?

```python
class MissionSandbox(BaseModel):
    """Cross-team sandbox for a specific transaction."""

    mission_id: str
    tenant_id: str

    # Shared context (accessible to all participating teams)
    shared_artifacts: dict[str, str]  # contract doc, etc.
    message_thread: list[str]         # UNI-Q micro messages
    published_findings: dict[str, str]  # team_id -> finding ref

    # Participating teams
    team_subscriptions: dict[str, list[str]]  # team_id -> patterns

    # Lifecycle
    status: Literal["active", "completed", "archived"]
    created_at: datetime
    completed_at: datetime | None
```

### Sandbox Hierarchy

```
Department Level
    │
    ├── Mission Sandbox: contract-nexus-review
    │   │
    │   │   Shared context for this transaction only:
    │   │   - The contract under review
    │   │   - Cross-team message thread (UNI-Q micro)
    │   │   - Published findings from each team
    │   │
    │   ├── Legal Team (working in mission sandbox)
    │   │   └── Agent sandboxes (task-specific)
    │   │
    │   ├── Risk Team (working in mission sandbox)
    │   │   └── Agent sandboxes (task-specific)
    │   │
    │   └── Management Team (working in mission sandbox)
    │       └── Agent sandboxes (task-specific)
    │
    └── Mission Sandbox: contract-dataflow-review
        │   (completely isolated from nexus review)
        ...
```

### Why Mission Sandboxes?

1. **Isolation** - Concurrent transactions don't pollute each other's context
2. **Cleanup** - When transaction completes, archive the sandbox (audit trail preserved)
3. **Focus** - Teams only see context relevant to THIS transaction
4. **Security** - Contract A's details can't leak into Contract B's reasoning

---

## Subscription Model

### Team Subscriptions (Department Level)

Teams register patterns they care about with the department orchestrator:

```python
department_subscriptions = {
    "risk_team": [
        "Ⓣcontract·*",           # All contract tasks
        "Ⓥdecision·*⟨risk:*⟩",   # Decisions mentioning risk
        "Ⓔvendor·*⚠",            # Any vendor with warning flag
    ],
    "legal_team": [
        "Ⓣcontract·*",           # All contract tasks
        "Ⓥrisk-assessment·*",    # All risk assessments
        "Ⓔvendor·*⟨compliance:*⟩",  # Compliance-related vendors
    ],
    "management_team": [
        "Ⓥdecision·*→Ⓐmgmt",     # Decisions routed to them
        "Ⓣcontract·*⟨val:>100K⟩",  # High-value contracts
        "Ⓥ*·*⚠",                  # Anything with warning flag
    ],
}
```

### Agent Subscriptions (Team Level)

Agents within a team register patterns with their team orchestrator:

```python
legal_team_subscriptions = {
    "research_agent": [
        "Ⓣ*·legal-research",      # All legal research tasks
    ],
    "draft_agent": [
        "Ⓥresearch·*✓",           # Completed research
        "Ⓥreview·*⟨revision:*⟩",  # Review feedback requiring revision
    ],
    "review_agent": [
        "Ⓥdraft·*✓",              # Completed drafts
    ],
    "citation_agent": [
        "Ⓥdraft·*◐",              # Drafts in progress (parallel citation check)
    ],
}
```

### Subscription Matching

The orchestrator matches published messages against registered patterns:

```python
def match_subscriptions(message: str, subscriptions: dict) -> list[str]:
    """Return list of subscribers whose patterns match this message."""
    subscribers = []
    for subscriber, patterns in subscriptions.items():
        for pattern in patterns:
            if pattern_matches(message, pattern):
                subscribers.append(subscriber)
                break
    return subscribers
```

### Routing Flow

```
1. Agent publishes:     Ⓥresearch·nexus-precedents✓⟨sources:12⟩

2. Orchestrator matches:
   - draft_agent: ✓ (matches Ⓥresearch·*✓)
   - citation_agent: ✗ (matches ◐, not ✓)

3. Orchestrator routes to draft_agent

4. Orchestrator can also:
   - Override routing decisions
   - Add checkpoints before delivery
   - Intervene when flags appear
   - Escalate to human
```

### The Orchestrator Remains the Hub

The fractal subscription model does NOT mean peer-to-peer communication. The orchestrator:
- Receives all published messages
- Matches against subscriptions
- Decides routing (can override subscription matches)
- Maintains audit trail
- Enforces checkpoints

```
Publisher → Orchestrator → [Subscription Matching] → Subscribers
                ↓
         [Override/Checkpoint/Escalate if needed]
```

---

## Full Fractal Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MISSION SANDBOX                                   │
│                    (transaction scope)                               │
│                                                                      │
│    ┌───────────────────────────────────────────────────────────┐    │
│    │              DEPARTMENT LEVEL                              │    │
│    │              UNI-Q pub/sub via Dept Head                   │    │
│    │                                                            │    │
│    │   ┌─────────────────────────────────────────────────┐     │    │
│    │   │           TEAM LEVEL                             │     │    │
│    │   │           UNI-Q pub/sub via Team Orchestrator    │     │    │
│    │   │                                                  │     │    │
│    │   │   ┌─────────────────────────────────────┐       │     │    │
│    │   │   │        AGENT LEVEL                   │       │     │    │
│    │   │   │        UNI-Q pub/sub via Agent       │       │     │    │
│    │   │   │        (if task decomposition needed)│       │     │    │
│    │   │   └─────────────────────────────────────┘       │     │    │
│    │   │                                                  │     │    │
│    │   └─────────────────────────────────────────────────┘     │    │
│    │                                                            │    │
│    └───────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

At every level:
- Same UNI-Q micro format
- Same subscription matching
- Same resolution system (micro/summary/full)
- Same hub routing (orchestrator at that level)
- Same message thread (within that sandbox)
```

---

## Quick Reference Card

```
LAYERS:  Ⓢtrategic Ⓞperational Ⓔntity Ⓥevent Ⓐgent Ⓣask Ⓓocument

STATUS:  ◉active ○idle ⊘blocked ⚠error ✓done ◐pending ⦿critical ⊗crit-blocked

PRIORITY: ⁺high (none)normal ⁻low

PROGRESS: ⓪①②③④⑤⑥⑦⑧⑨⑩

TREND:   ↗up →stable ↘down ↯volatile

RELATIONS: →depends ←blocks ↔mutual ∼related ⊂involves ⊃applies ∧aligned

FLAGS:   ⚑attention ⚐conditional ⚠risk ⁑dissent ⧖time-sensitive

MESSAGES: S:status Q:query D:delegate A:ack N:notify R:result ⊕sub ⊖unsub ✓ok ✗no

RESOLUTION: μ:micro Σ:summary F:full

DELIMITERS: │section ·attribute ;entity ⟨tags⟩
```

---

*Last updated: 2025-01-08*
