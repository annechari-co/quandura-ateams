# Quandura Organizational Memory System

## Overview

The organizational memory system provides a structured, multi-layer knowledge graph that enables teams to:

1. **Capture institutional knowledge** across strategic goals, operational policies, persistent entities, and events
2. **Retrieve at appropriate resolution** (micro, summary, full) for context-efficient agent operation
3. **Support precedent-based reasoning** by finding similar past cases with their outcomes and reasoning
4. **Use structured tags** for fast filtering without complex query systems

This is NOT a replacement for RAG - it's a **graph layer on top of embeddings** that adds structure, relationships, and typed retrieval.

---

## Core Concepts

### 1. Four Universal Layers

Every team uses the same 4 semantic layers. The specific **types** within each layer are pluggable per team.

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: STRATEGIC                                             │
│  "Why the organization exists, what it optimizes"              │
│                                                                 │
│  Update frequency: Quarterly/Yearly                             │
│  Examples: Goals, Priorities, KPIs, Values                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ INFORMS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: OPERATIONAL                                           │
│  "Rules, constraints, procedures"                               │
│                                                                 │
│  Update frequency: Monthly/As-needed                            │
│  Examples: Policies, Procedures, Approval Thresholds            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ APPLIES TO
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: ENTITY                                                │
│  "Persistent objects tracked over time"                         │
│                                                                 │
│  Update frequency: Per-interaction                              │
│  Examples: Customers, Products, Cases, Matters                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ INVOLVES
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: EVENT                                                 │
│  "Things that happen, with outcomes"                            │
│                                                                 │
│  Update frequency: Real-time (append-only)                      │
│  Examples: Calls, Decisions, Trades, Research Requests          │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Team-Specific Types

The layer structure is universal, but types within layers are defined per team:

| Layer | Customer Service | Legal Research | Prop Trading |
|-------|-----------------|----------------|--------------|
| **Strategic** | Goal, Priority, KPI | Goal, Jurisdiction_Priority | Goal, Risk_Tolerance, Strategy |
| **Operational** | Policy, Procedure, Escalation_Rule | Research_Protocol, Citation_Standard | Risk_Limit, Trading_Rule, Compliance |
| **Entity** | Customer, Product, Agent | Case, Statute, Matter, Precedent | Trader, Instrument, Position |
| **Event** | Call, Ticket, Decision, Refund | Research_Request, Opinion_Draft | Trade, Signal, Alert, P&L |

### 3. Multi-Resolution Content

Every node has three content representations:

```
┌─────────────────────────────────────────────────────────────────┐
│  MICRO (~10-20 tokens)                                          │
│  Dense, for listing and scanning                                │
│                                                                 │
│  Example: "refund|denied|$450|no-evidence|policy.refund.v3"    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  SUMMARY (~50-100 tokens)                                       │
│  Enough context for reasoning                                   │
│                                                                 │
│  Example: "Customer requested $450 refund for defective item.  │
│           Denied due to no evidence provided. Policy v3        │
│           requires photo documentation for defect claims."      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  FULL (unlimited)                                               │
│  Complete content, loaded on demand                             │
│                                                                 │
│  Example: Full call transcript, complete policy text,           │
│           all metadata and attachments                          │
└─────────────────────────────────────────────────────────────────┘
```

**Why this matters for context efficiency:**

| Scenario | Without Multi-Resolution | With Multi-Resolution |
|----------|--------------------------|----------------------|
| Audit 10,000 refunds | Load 10K full nodes → 5M tokens | Load 10K micro → 150K tokens |
| Find similar cases | Load 500 full matches → 250K tokens | Load 500 micro, expand top 5 → 10K tokens |
| Build agent context | Everything or nothing | Customer summary + Policy full + Precedents micro |

### 4. Structured Tags

Instead of complex query systems, we use simple structured tags for filtering:

```python
# Convention: "key:value" format
tags = [
    "customer:042",
    "policy:refund.v3",
    "outcome:denied",
    "factor:no-evidence",
    "factor:outside-window",
]

# Query: Find all denied refunds for customer 042
query = MemoryQuery(
    tag_filter={"customer": "042", "outcome": "denied"},
    layer=MemoryLayer.EVENT,
)
```

Helper methods on MemoryNode:
```python
node.add_tag("customer", "042")
node.get_tag("customer")  # Returns "042"
node.has_tag("outcome", "denied")  # Returns True
node.get_all_structured_tags()  # Returns {"customer": "042", "outcome": "denied", ...}
```

### 5. Typed Relationships

Relationships are typed, enabling meaningful graph traversal:

```python
# Cross-layer relationships
INVOLVES        # event → entity
APPLIES         # event → operational (which policy was used)
ALIGNED_WITH    # event/operational → strategic
INFORMS         # strategic → operational

# Within-layer relationships
SUPERSEDES      # operational → operational (version history)
CONFLICTS_WITH  # operational → operational
SIMILAR_TO      # event → event (precedents)
ESCALATED_TO    # event → event
CAUSED          # event → decision (the "why")
```

---

## How This Differs from Standard RAG

| Aspect | Pure RAG | Organizational Memory |
|--------|----------|----------------------|
| **Retrieval** | Similarity only | Similarity + exact lookup + graph traversal |
| **Structure** | Flat chunks | Typed nodes in semantic layers |
| **Relationships** | None | Explicit typed edges |
| **Context output** | "Related text blobs" | "Customer + Policy + Precedents" |
| **Reasoning chain** | Implicit in text | Explicit in CAUSED relationships |
| **Addressing** | Opaque chunk IDs | Semantic paths (`event.decision.refund.2024-12-28`) |
| **Resolution** | All or nothing | Micro/summary/full based on need |

---

## Precedent-Based Reasoning

The "why" behind decisions is captured through `CAUSED` relationships:

```
┌─────────────────────────────────────────────────────────────────┐
│  EVENT: interaction.call.2024-12-28-0847                        │
│                                                                 │
│  customer: entity.customer.jane-doe-042                         │
│  topic: "defective product refund"                              │
│  outcome: "resolved"                                            │
│  tags: ["customer:042", "topic:refund", "outcome:resolved"]     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ CAUSED
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  EVENT: decision.refund.2024-12-28-0847-001                     │
│                                                                 │
│  outcome: "approved"                                            │
│  amount: $450                                                   │
│  reason: "Photo evidence confirmed manufacturing defect"        │
│  factors: ["evidence_provided", "within_window", "known_issue"] │
│  policy_applied: "operational.policy.refund.v3.defective"       │
│  tags: ["customer:042", "outcome:approved", "amount:450"]       │
└─────────────────────────────────────────────────────────────────┘
```

When an agent handles a new case, they retrieve:

1. **Customer history** via `entity.customer.*` lookup
2. **Similar cases** via `find_similar()` on the current request
3. **The "why"** by traversing `CAUSED` from similar cases to their decisions
4. **The policy** by traversing `APPLIES` to see which rules were invoked

This enables principled reasoning:
> "Similar cases show that evidence is the key differentiator. This customer has no evidence yet. Ask for photo documentation."

---

## Integration with Passport

The Passport gains memory context fields:

```python
class Passport(BaseModel):
    # Existing fields...

    # Memory integration
    memory_context: list[str] = []           # Symbols loaded for this mission
    memory_resolution: dict[str, str] = {}   # symbol -> resolution loaded
    precedent_context: PrecedentContext | None = None
    emitted_symbols: list[str] = []          # Symbols created during processing
```

### Agent Context Assembly

When an agent receives a Passport, the Librarian assembles context:

```python
async def assemble_agent_context(
    passport: Passport,
    agent_type: str,
    max_tokens: int = 4000,
) -> AgentContext:
    """Build context-efficient memory for an agent."""

    context = AgentContext()

    # 1. Load entity context (customer/matter/etc.)
    if passport.mission.entity_symbol:
        entity = await memory.retrieve(
            [passport.mission.entity_symbol],
            resolution="summary",
        )
        context.entity = entity[0]

    # 2. Load applicable policies
    policies = await memory.query(
        pattern="operational.policy.*",
        tags=["topic:" + passport.mission.matter_type],
        resolution="full",  # Need full policy text
        limit=3,
    )
    context.policies = policies

    # 3. Find similar precedents
    similar = await memory.find_similar(
        passport.mission.objective,
        layer=MemoryLayer.EVENT,
        limit=20,
    )

    # Get micro for all, summary for top 5
    context.precedents_micro = [n.micro for n in similar]
    context.precedents_detail = await memory.retrieve(
        [n.symbol for n in similar[:5]],
        resolution="summary",
    )

    # 4. Traverse to get the "why" for precedents
    for precedent in context.precedents_detail:
        decisions = await memory.traverse(
            precedent.symbol,
            relation_types=[RelationType.CAUSED],
            max_depth=1,
        )
        precedent.decisions = decisions

    return context
```

---

## Salience and Consolidation

Salience determines which memories surface first. It's context-dependent and decays over time.

### Salience Factors

```python
salience = base_salience * (
    time_decay(days_since_access) *
    access_frequency_boost(retrieval_count) *
    relationship_boost(cross_layer_connections) *
    outcome_weight(success_rate_of_related_decisions)
)
```

### Consolidation (Like Sleep)

Periodic consolidation recalculates salience and prunes low-value memories:

```python
async def consolidate(memory: OrganizationalMemory) -> ConsolidationResult:
    """Run consolidation (typically nightly)."""

    updated = 0
    pruned = 0

    # 1. Decay salience for unaccessed nodes
    stale_nodes = await memory.query(
        min_age_days=1,
        accessed_since=None,
    )
    for node in stale_nodes:
        node.salience *= (1 - config.time_decay_rate)
        await memory.update(node)
        updated += 1

    # 2. Boost nodes with cross-layer relationships
    connected_nodes = await memory.query_with_relationships(
        min_relationships=2,
        cross_layer=True,
    )
    for node in connected_nodes:
        node.salience = min(1.0, node.salience + config.cross_layer_boost)
        await memory.update(node)

    # 3. Prune low-salience old nodes
    prune_candidates = await memory.query(
        max_salience=config.prune_threshold,
        min_age_days=config.min_age_days,
    )
    for node in prune_candidates:
        await memory.archive(node)  # Move to cold storage, not delete
        pruned += 1

    return ConsolidationResult(
        nodes_updated=updated,
        nodes_pruned=pruned,
    )
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure

- [x] `MemoryNode` base class with multi-resolution
- [x] Symbol path validation and parsing
- [x] Relationship storage and retrieval
- [x] Structured tag helpers
- [ ] PostgreSQL storage for nodes (JSONB for flexibility)
- [ ] ChromaDB integration for embeddings
- [ ] Basic query interface

### Phase 2: Team Schema System

- [x] `TeamMemorySchema` with pluggable types
- [x] Extension type registration
- [ ] Schema validation on store

### Phase 3: Retrieval Operations

- [ ] Pattern matching (`event.call.*`)
- [ ] Semantic search (embedding similarity)
- [ ] Graph traversal (follow relationships)
- [ ] Tag-based filtering
- [ ] Multi-resolution loading
- [ ] Precedent context assembly

### Phase 4: Librarian Agent

- [ ] Context assembly for agents
- [ ] Query optimization
- [ ] Caching layer
- [ ] Consolidation scheduler

---

## Design Decisions

### Why Not Neo4j (Yet)?

We considered using Neo4j for the relationship layer but decided against it for now:

1. **Operational simplicity** - One less database to manage, backup, secure
2. **Multi-tenancy** - PostgreSQL RLS provides row-level security that's harder in Neo4j
3. **We don't have data yet** - Let's see what queries we actually need
4. **Can add later** - If we find ourselves writing complex recursive CTEs, that's the signal

PostgreSQL with JSONB relationships can handle 2-3 hop traversals. It's not elegant but it works for our current needs.

### Why Structured Tags Instead of Complex Fingerprints?

We started with an elaborate fingerprint system with compression strategies, weighted similarity, and team-specific dimension schemas. We simplified to structured tags because:

1. **80% of the benefit, 20% of the complexity** - `customer:042` works just as well
2. **Database-friendly** - Tags can be indexed and queried directly in PostgreSQL
3. **Debuggable** - Humans can read tags; fingerprints were opaque
4. **Extensible** - Teams can add new tag keys without schema changes

---

## Related Documents

- `QUANDURA_ARCHITECTURE.md` - Overall system architecture
- `backend/app/models/memory.py` - Implementation models
- `planning/teams/LAW_OFFICE_LEGAL_RESEARCH.md` - First team specification

---

*Version: 2.0*
*Created: 2025-01-06*
*Updated: 2025-01-06*
*Status: Design specification for organizational memory system*

**Changelog:**
- v2.0: Simplified from fingerprints to structured tags; removed type evolution; added design decisions section
- v1.1: Added relationship fingerprint system (removed in v2.0)
- v1.0: Initial design with 4-layer architecture
