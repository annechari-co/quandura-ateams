# UNI-Q Implementation Examples

Practical reference scenarios for building the multi-resolution memory and subscription-based coordination system.

---

## Example 1: Decision Trace (Resolution Levels)

Demonstrates how the same event is stored at three resolutions and retrieved based on query intent.

### Scenario

Customer service approves a $450 refund for Maria Chen.

### Storage (All Three Resolutions Created)

**MICRO** (~15 tokens) - Hot index, used for routing/monitoring:
```
Ⓥdecision·ref4721✓⟨amt:450⟩⊂Ⓔmaria-chen
```

**SUMMARY** (~80 tokens) - Warm cache, used for reasoning:
```
Decision #4721: Approved $450 refund for VIP customer Maria Chen (C-8842).
Applied Policy 3.2.4.1 (VIP discretionary limit $500). Customer has 6yr
tenure, $34K LTV, 2 complaints in 6mo. Supports retention goal (95% target).
```

**FULL** (~300 tokens) - Cold storage, used for audit:
```
Decision record for customer refund case #4721:

The customer service agent approved a $450 refund for customer Maria Chen
(ID: C-8842).

This decision was made because:
- Maria is a VIP tier customer with 6 years of tenure
- Her lifetime value is $34,000
- The refund policy for VIP customers allows discretionary refunds up to $500
- The specific policy applied was Refund Policy version 3.2, section 4.1

The refund policy 3.2 section 4.1 states:
- VIP customers may receive discretionary refunds up to $500 without manager approval
- This policy exists to support the strategic goal of customer retention
- The customer retention goal has a target of maintaining 95% retention for
  customers with 5+ years tenure

Maria's recent interaction history:
- 3 months ago: product complaint, resolved with replacement
- 6 months ago: shipping delay, $50 credit issued
- 1 year ago: positive feedback survey

The decision factors considered were:
1. Customer tier (VIP)
2. Tenure (6 years, exceeds 5-year threshold)
3. Lifetime value ($34K, high value customer)
4. Recent complaint pattern (2 issues in 6 months, concerning but not excessive)
5. Amount requested ($450, within $500 VIP limit)
```

### Query Intent → Resolution Mapping

| Query | Intent | Resolution | Response |
|-------|--------|------------|----------|
| "Any decisions on Maria?" | ROUTE | MICRO | `Ⓥdecision·ref4721✓⟨amt:450⟩⊂Ⓔmaria-chen` |
| "Show today's decisions" | MONITOR | MICRO | List of micro entries |
| "Why was this approved?" | REASON | SUMMARY | The summary text |
| "Verify policy compliance" | AUDIT | FULL | Complete prose record |

### Dashboard Monitoring Example

Query: "Show me all decisions from today"

```
Ⓥdecision·ref4721✓⟨amt:450⟩⊂Ⓔmaria-chen
Ⓥdecision·ref4718✓⟨amt:125⟩⊂Ⓔjohn-doe
Ⓥdecision·ref4715✗⟨amt:2400⟩⊂Ⓔacme-corp⚑
Ⓥdecision·ref4712✓⟨amt:89⟩⊂Ⓔsarah-kim
```

At a glance: 4 decisions, 3 approved, 1 denied with attention flag.

**Tokens for 4 decisions: ~60** (vs ~1,200 if using full prose)

### Prefetch Example

Query: "Show decisions needing attention"

Prefetch rule triggers: `⚑ → fetch SUMMARY`

```
# Micro for clean ones
Ⓥdecision·ref4721✓⟨amt:450⟩⊂Ⓔmaria-chen
Ⓥdecision·ref4718✓⟨amt:125⟩⊂Ⓔjohn-doe

# Summary auto-fetched for flagged one
Ⓥdecision·ref4715✗⟨amt:2400⟩⊂Ⓔacme-corp⚑
  → Decision #4715: Denied $2,400 refund for Acme Corp. Amount exceeds
    corporate limit ($1,000). Customer disputing, escalation recommended.
    Risk: potential contract review.

Ⓥdecision·ref4712✓⟨amt:89⟩⊂Ⓔsarah-kim
```

**Single round-trip, flagged item comes with context.**

---

## Example 2: Cross-Team Vendor Contract Review (Subscriptions)

Demonstrates subscription-based coordination between Risk, Legal, and Management teams.

### Team Subscription Registry

```python
# Risk Team subscriptions
risk_subscriptions = [
    "Ⓣcontract·*",           # All contract tasks
    "Ⓥdecision·*⟨risk:*⟩",   # Decisions mentioning risk
    "Ⓔvendor·*⚠",            # Any vendor flagged with warning
]

# Legal Team subscriptions
legal_subscriptions = [
    "Ⓣcontract·*",           # All contract tasks
    "Ⓥrisk-assessment·*",    # All risk assessments
    "Ⓔvendor·*⟨compliance:*⟩",  # Vendors with compliance attributes
]

# Management Team subscriptions
mgmt_subscriptions = [
    "Ⓥdecision·*→Ⓐmgmt",     # Decisions routed to them
    "Ⓣcontract·*⟨val:>100K⟩",  # High-value contracts
    "Ⓥ*·*⚠",                  # Anything with warning flag
]
```

### Scenario

Legal team discovers a vendor contract auto-renewed with problematic terms.

---

### Step 1: Legal Discovers and Publishes

Legal publishes discovery to the orchestrator:

**MICRO (published to channel):**
```
Ⓥdiscovery·vendor-nexus-renewal⚠⟨val:280K⟩
  ⊂Ⓔvendor·nexus
  issue:auto-renewed-bad-terms
  →Ⓐrisk?
  →Ⓐmgmt?
```

**SUMMARY (stored with discovery):**
```
Discovery: Nexus Software Auto-Renewal Issue

Vendor Nexus software contract auto-renewed on Jan 1 with new terms.
Problematic changes discovered during routine audit:

1. Data retention: Changed from 1yr to 5yr (was not notified)
2. Price increase: 18% (exceeds our 10% threshold)
3. New arbitration clause: Mandatory binding, vendor-favorable jurisdiction

Contract value: $280K/year
Renewal lock-in: 2 years remaining

Recommendation: Immediate risk assessment, consider termination for cause
```

### Step 2: Orchestrator Routes via Subscriptions

```python
# Orchestrator matching logic
message = "Ⓥdiscovery·vendor-nexus-renewal⚠⟨val:280K⟩"

matches = {
    "risk":  ["Ⓔvendor·*⚠"],           # vendor with warning
    "mgmt":  ["Ⓥ*·*⚠", "Ⓣ*⟨val:>100K⟩"]  # warning + high value
}

# Both teams receive the MICRO in their inbox
```

### Step 3: Risk Team Inbox

```
[NEW] Ⓥdiscovery·vendor-nexus-renewal⚠⟨val:280K⟩⊂Ⓔvendor·nexus
      source:Ⓐlegal
      matched:Ⓔvendor·*⚠
```

Risk queries for context (Intent: REASON), gets Legal's summary, then claims work:

**MICRO (published):**
```
Ⓥdiscovery·vendor-nexus-renewal⚠⟨val:280K⟩
  ⊂Ⓐrisk◐        # Risk is now working on it
  ⊂Ⓐlegal✓       # Legal's discovery complete
  →Ⓐmgmt◐        # Management watching
```

### Step 4: Management Monitors (MICRO only)

Management queries: "What's pending?"

```
Intent: MONITOR → Resolution: MICRO
```

Response:
```
Ⓥdiscovery·vendor-nexus-renewal⚠⟨val:280K⟩
  ⊂Ⓐlegal✓
  ⊂Ⓐrisk◐
  →Ⓐmgmt◐
```

Management knows: "Legal found something, Risk is on it, I'll wait."

**No summary fetched yet - just tracking.**

### Step 5: Risk Completes Assessment

**MICRO (published):**
```
Ⓥrisk-assessment·nexus-renewal⚠⟨score:high⟩✓
  findings:3
  rec:terminate
  →Ⓐlegal
  →Ⓐmgmt
```

**SUMMARY (stored):**
```
Risk Assessment: Nexus Software Renewal

Risk Score: HIGH

Findings:
1. Data retention change: CRITICAL - violates our data policy,
   potential regulatory exposure
2. Price increase: MEDIUM - 18% unbudgeted, $50K annual impact
3. Arbitration clause: HIGH - removes our legal leverage

Recommendation: Terminate for cause (material change without notice)
Fallback: Negotiate removal of all three changes
Timeline: Must act within 30 days of discovery (contractual notice period)
```

**Subscription matching routes to:**
- Legal (matches `Ⓥrisk-assessment·*`)
- Management (matches `Ⓥ*·*⚠`)

### Step 6: Legal Claims Termination Review

```
Ⓣtermination-review·nexus◐
  ⊂Ⓥrisk-assessment·nexus-renewal✓
  ⊂Ⓐlegal◐
  →Ⓐmgmt◐
```

### Step 7: Management Views Full Thread

Query: "What's happening with Nexus?"

```
Intent: MONITOR → Resolution: MICRO
```

Response (full thread context):
```
Ⓔvendor·nexus
  │
  ├─ Ⓥdiscovery·vendor-nexus-renewal⚠✓
  │    source:Ⓐlegal
  │
  ├─ Ⓥrisk-assessment·nexus-renewal⚠⟨score:high⟩✓
  │    rec:terminate
  │    source:Ⓐrisk
  │
  └─ Ⓣtermination-review·nexus◐
       ⊂Ⓐlegal◐
       →Ⓐmgmt◐
```

**Tokens: ~60 for complete thread status**

### Step 8: Management Gets Reasoning

Query: "Why terminate?"

```
Intent: REASON → Resolution: SUMMARY
Prefetch: ⚠ items get summary automatically
```

Response includes both summaries:
- Legal's discovery summary
- Risk's assessment summary

**Tokens: ~250 for complete reasoning**

### Step 9: Management Decides

**MICRO (published):**
```
Ⓥdecision·nexus-termination✓
  ⊂Ⓔvendor·nexus
  ⊂Ⓥrisk-assessment·nexus-renewal
  →Ⓐlegal
  →Ⓐprocurement
```

**SUMMARY:**
```
Decision: APPROVED TERMINATION

Vendor: Nexus Software ($280K/year)
Approved by: J. Martinez, Management Team

Action: Terminate for cause
Basis: Material contract changes without required notice (Risk finding)

Assigned to: Legal (termination notice), Procurement (vendor replacement)
Timeline: Notice within 5 business days
```

**Subscription matching routes to:**
- Legal (decision routed to them)
- Procurement (decision mentioning vendor)

---

## Communication Pattern Summary

```
        ┌─────────────────────────────────────────────────────┐
        │              ORCHESTRATOR (Pub/Sub Router)          │
        │                                                     │
        │   Subscription Registry:                            │
        │   ┌─────────────────────────────────────────────┐   │
        │   │ Ⓐrisk:  Ⓣcontract·*, Ⓔvendor·*⚠           │   │
        │   │ Ⓐlegal: Ⓣcontract·*, Ⓥrisk-assessment·*   │   │
        │   │ Ⓐmgmt:  Ⓥ*·*⚠, Ⓣ*⟨val:>100K⟩, Ⓥdecision·* │   │
        │   └─────────────────────────────────────────────┘   │
        └──────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
       ┌─────────┐       ┌──────────┐       ┌──────────┐
       │  RISK   │       │  LEGAL   │       │   MGMT   │
       │  TEAM   │       │  TEAM    │       │   TEAM   │
       └─────────┘       └──────────┘       └──────────┘
            │                  │                  │
            │   ◄──MICRO───►   │   ◄──MICRO───►   │
            │                  │                  │
       (subscribes)      (publishes)        (subscribes)
       (publishes)       (subscribes)       (decides)
```

### Key Rules

1. **Inter-team messages are always MICRO** - Subscriptions match micro patterns
2. **Resolution is on-demand** - Teams fetch SUMMARY/FULL only when engaging
3. **Work claims are explicit** - `◐` indicates active work, prevents duplicates
4. **Flags propagate** - `⚠⚑⚐` in micro trigger subscription matches and prefetch rules
5. **Thread context via `⊂`** - Relationships show what led to what

---

## Token Efficiency Comparison

### Example 1: Decision Monitoring

| Operation | Full Prose | Multi-Resolution | Savings |
|-----------|------------|------------------|---------|
| Monitor 4 decisions | ~1,200 tokens | ~60 tokens | 95% |
| Check 1 with flag | ~300 tokens | ~120 tokens | 60% |
| Full audit | ~300 tokens | ~300 tokens | 0% |

### Example 2: Cross-Team Workflow

| Operation | Dense UNI-Q | Multi-Resolution | Savings |
|-----------|-------------|------------------|---------|
| Monitor thread status | ~200 tokens | ~60 tokens | 70% |
| Get reasoning (2 teams) | ~400 tokens | ~250 tokens | 38% |
| Full workflow | ~1,800 tokens | ~690 tokens | 62% |

---

## Implementation Checklist

When building these patterns:

- [ ] Subscription registry in orchestrator
- [ ] Micro pattern matching (glob-style with UNI-Q symbols)
- [ ] Three-tier storage (hot/warm/cold)
- [ ] Query intent detection
- [ ] Prefetch rules engine
- [ ] Thread context builder (`⊂` relationship traversal)
- [ ] Inbox per team with subscription source tracking

---

## Example 3: Fractal Architecture Analysis

This section documents the design rationale for using the same UNI-Q pattern at every organizational level.

### The Questions

1. **Should cross-team transactions spin up their own sandbox?**
2. **Should inter-agent (within a team) communications use the same UNI-Q/subscription structure as inter-team communications?**

### Context: Why Sandboxes Exist

From the architecture document, sandboxes serve three purposes:
1. **Cost efficiency** - Minimal tokens per agent
2. **Quality** - Focused context = better reasoning
3. **Security** - Agents can't leak what they don't have

Currently, sandboxes exist for **intra-team** work - when an orchestrator delegates to specialists. But cross-team transactions like contract review create a shared context that spans multiple teams.

---

### Answer 1: Yes, Transactions Need Mission Sandboxes

**Rationale:**

When Legal, Risk, and Management coordinate on a contract review, they create a shared context. Without isolation:
- Context from Contract A could pollute reasoning about Contract B
- Cleanup is messy (what belongs to which transaction?)
- Security is harder (who should see what?)

**The Solution: Mission Sandbox**

Each cross-team transaction spins up its own sandbox:

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

**Benefits:**
1. **Isolation** - Concurrent transactions don't pollute each other's context
2. **Cleanup** - When transaction completes, archive the sandbox (audit trail preserved)
3. **Focus** - Teams only see context relevant to THIS transaction
4. **Security** - Contract A's details can't leak into Contract B's reasoning

---

### Answer 2: Yes, Use the Same Pattern at Every Level (Fractal Design)

**The Intuition:**

> "My intuition is to say the system will be more robust if they are the same (so the structure is almost 'fractal' - you can zoom-in/zoom-out and it is all operating the same way)."

This intuition is correct. Here's the analysis:

**Current State:**
- Inter-team: Orchestrators communicate via Department Head (hub-and-spoke)
- Intra-team: Specialists only talk to their Team Orchestrator (hub-and-spoke)

**The Question:** Should specialists within a team use the same UNI-Q subscription model that teams use with each other?

**The Concern:**

The hub-and-spoke principle exists for:
1. **Control** - Orchestrator manages flow
2. **Auditability** - All communication goes through a single point
3. **Simplicity** - Specialists don't need to know about each other

**The Resolution:**

These goals don't conflict with using UNI-Q format - they conflict with **direct peer communication**. We can have both:

```
Same format + Same mechanism + Hub routing = Fractal with discipline
```

**How It Works:**

```
INTER-TEAM (current UNI-Q design):
─────────────────────────────────
Legal publishes:  Ⓥrisk-assessment·nexus⚠✓
                        │
                        ▼
              Department Orchestrator
                        │
              (routes via subscriptions)
                        │
                        ▼
              Risk, Management receive


INTRA-TEAM (same pattern):
──────────────────────────
Research Agent publishes:  Ⓥresearch·nexus-precedents✓⟨sources:12⟩
                                    │
                                    ▼
                          Team Orchestrator
                                    │
                          (routes via subscriptions)
                                    │
                                    ▼
                          Draft Agent, Review Agent receive
```

**The Key Insight:** The orchestrator is still the hub. But instead of manually routing, it routes based on subscriptions. The pattern is the same at every level:

| Level | Publisher | Hub (Router) | Subscribers |
|-------|-----------|--------------|-------------|
| Department | Team Orchestrators | Dept Head | Other Team Orchestrators |
| Team | Specialist Agents | Team Orchestrator | Other Specialists |
| Agent | Sub-tasks | Agent | Sub-task handlers |

---

### Intra-Team Subscription Example

```python
# Legal Team - Agent Subscriptions
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

**Workflow with Fractal Design:**

```
1. Task arrives at Legal Team Orchestrator
   Ⓣresearch·nexus-contract-legality

2. Orchestrator matches subscriptions → routes to Research Agent

3. Research Agent completes, publishes:
   Ⓥresearch·nexus-precedents✓⟨sources:12⟩

4. Orchestrator matches subscriptions → routes to Draft Agent AND Citation Agent
   (parallel work)

5. Draft Agent completes, publishes:
   Ⓥdraft·nexus-opinion✓μ:high

6. Orchestrator matches → routes to Review Agent

7. Review Agent finds issue, publishes:
   Ⓥreview·nexus-opinion⚐⟨revision:citation-missing⟩

8. Orchestrator matches → routes back to Draft Agent (revision subscription)
```

**The orchestrator still controls** - it can:
- Override routing decisions
- Add checkpoints
- Intervene when flags appear
- Escalate to human

But the *mechanism* is the same as inter-team: publish → match subscriptions → route.

---

### Benefits of Fractal Design

1. **One pattern to implement** - The subscription/routing logic is identical at every level
2. **One pattern to debug** - Same tools work everywhere
3. **Composable** - A team can be treated as an "agent" at the department level
4. **Emergent scaling** - Patterns that work at team level naturally apply if we add sub-teams
5. **Consistent UNI-Q** - Same micro format flows at all levels

---

### The Full Fractal Picture

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

### Cost-Benefit Summary

| Aspect | Cost | Benefit |
|--------|------|---------|
| Mission sandbox | Sandbox lifecycle management | Transaction isolation, clean archives |
| Fractal pub/sub | Slightly more routing logic | One pattern everywhere, composability |
| Intra-team UNI-Q | Agents need to publish in format | Consistent debugging, same tools |

**Recommendation:** Both are worth it. The implementation cost is low (we're building the pub/sub anyway), and the architectural consistency pays dividends in:
- **Debugging** (same patterns everywhere)
- **Testing** (same test harness works at all levels)
- **Scaling** (add levels without new patterns)
- **Understanding** (explain once, applies everywhere)

---

*Reference for Quandura implementation. See UNIQ_SPEC.md for full grammar specification.*
