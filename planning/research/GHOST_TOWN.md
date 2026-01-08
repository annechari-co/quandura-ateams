# Gas Town Research: Multi-Agent Workspace Manager

*Analysis of Steve Yegge's Gas Town framework for Quandura applicability*

## Overview

**Gas Town** is a multi-agent orchestration system for Claude Code with persistent work tracking. Created by Steve Yegge at Annechari, it solves the problem of coordinating 20-30 AI agents across multiple git repositories while maintaining context persistence, attribution, and work tracking.

**Repository:** https://github.com/annechari-co/gastown
**Stack:** Go, tmux, git worktrees, beads (issue tracking)

## Core Problem Statement

| Challenge | Gas Town Solution |
|-----------|-------------------|
| Agents lose context on restart | Work persists in git-backed hooks |
| Manual agent coordination | Built-in mailboxes, identities, handoffs |
| 4-10 agents become chaotic | Scale comfortably to 20-30 agents |
| Work state lost in agent memory | Work state stored in Beads ledger |

---

## The Propulsion Principle

**Core philosophy:**
> "If you find something on your hook, YOU RUN IT."

Gas Town is a steam engine. Agents are pistons. The entire system's throughput depends on one thing: when an agent finds work on their hook, they EXECUTE immediately.

**Key implications:**
- No supervisor polling asking "did you start yet?"
- The hook IS the assignment - placed there deliberately
- Every moment of waiting stalls the engine
- Other agents may be blocked waiting on your output

**Contrast with Quandura:** Our UNI-Q subscription model is similar - subscriptions define what agents respond to, and when a message arrives, they act. The "propulsion" is implicit in the pub/sub pattern.

---

## Agent Taxonomy

### Town-Level Agents (Cross-Project)

| Agent | Role | Persistence |
|-------|------|-------------|
| **Mayor** | Global coordinator, handles cross-rig communication | Persistent |
| **Deacon** | Daemon beacon - heartbeats, plugins, monitoring | Persistent |
| **Dogs** | Long-running workers for infrastructure tasks | Variable |

### Rig-Level Agents (Per-Project)

| Agent | Role | Persistence |
|-------|------|-------------|
| **Witness** | Monitors polecat health, nudges stuck agents | Persistent |
| **Refinery** | Processes merge queue, runs verification | Persistent |
| **Polecats** | Ephemeral workers assigned to specific issues | Ephemeral |
| **Crew** | Persistent human workspaces | Long-lived |

**Quandura mapping:**
- Mayor → Department Head Orchestrator
- Deacon → System Monitor (new consideration)
- Witness → Team Orchestrator (health monitoring aspect)
- Refinery → QA Agent (verification)
- Polecats → Specialist Agents (ephemeral workers)
- Crew → Human Agents (Ⓗ)

---

## Three-Layer Polecat Lifecycle

**Critical insight:** Polecats have three independent lifecycle layers:

| Layer | Component | Lifecycle | Persistence |
|-------|-----------|-----------|-------------|
| **Session** | Claude (tmux pane) | Ephemeral | Cycles per step/handoff |
| **Sandbox** | Git worktree | Persistent | Until nuke |
| **Slot** | Name from pool | Persistent | Until nuke |

### Session Layer
The Claude session is ephemeral. It cycles frequently:
- After each molecule step (via `gt handoff`)
- On context compaction
- On crash/timeout

**Key insight:** Session cycling is normal operation, not failure. The polecat continues working - only the Claude context refreshes.

### Sandbox Layer
The git worktree - the polecat's working directory. Exists from assignment until completion. Survives all session cycles.

### Slot Layer
The name allocation from a pool (Toast, Shadow, Copper, Ash, Storm...). Released only on completion.

**Quandura applicability:** This separation of concerns is valuable:
- **Session** = LLM context window (ephemeral)
- **Sandbox** = Mission workspace (persistent)
- **Slot** = Agent identity/allocation (persistent)

We could adopt similar layering for agent lifecycle management.

---

## Watchdog Chain Architecture

Three-tier autonomous health monitoring:

```
Daemon (Go process)          ← Dumb transport, 3-min heartbeat
    │
    └─► Boot (AI agent)       ← Intelligent triage, fresh each tick
            │
            └─► Deacon (AI agent)  ← Continuous patrol, long-running
                    │
                    └─► Witnesses & Refineries  ← Per-rig agents
```

### Why Two AI Agents?

1. **Daemon can't reason** - Go code can check "is session alive?" but not "is agent stuck?"
2. **Waking costs context** - Each AI spawn consumes tokens. In idle systems, waking constantly wastes resources.
3. **Observation requires intelligence** - Distinguishing "agent composing large artifact" from "agent hung" requires reasoning.

**Boot** is an ephemeral AI that:
- Runs fresh each daemon tick (no context debt)
- Makes a single decision: should Deacon wake?
- Exits immediately after deciding

**Heartbeat freshness:**
| Age | State | Boot Action |
|-----|-------|-------------|
| < 5 min | Fresh | Nothing (Deacon active) |
| 5-15 min | Stale | Nudge if pending mail |
| > 15 min | Very stale | Wake (Deacon may be stuck) |

**Quandura consideration:** We need health monitoring. Options:
1. Simple heartbeat (current implicit assumption)
2. Two-tier (mechanical + intelligent) like Gas Town
3. Peer monitoring (agents watch each other)

---

## Mail Protocol

Structured inter-agent communication using typed messages:

### Message Types

| Type | Route | Purpose |
|------|-------|---------|
| `POLECAT_DONE` | Polecat → Witness | Signal work completion |
| `MERGE_READY` | Witness → Refinery | Branch ready for merge |
| `MERGED` | Refinery → Witness | Confirm merge success |
| `MERGE_FAILED` | Refinery → Witness | Notify merge failure |
| `REWORK_REQUEST` | Refinery → Witness | Request rebase |
| `WITNESS_PING` | Witness → Deacon | Second-order monitoring |
| `HELP` | Any → escalation target | Request intervention |
| `HANDOFF` | Agent → self/successor | Session continuity |

### Message Format

```
Subject: TYPE: brief-description
Body:
  Key: Value
  Key: Value

  ## Freeform markdown content
```

**Comparison with UNI-Q:**
- Gas Town mail is point-to-point with typed messages
- UNI-Q is pub/sub with rich symbols
- Both achieve routing through structure
- UNI-Q is more compact; Gas Town mail is more explicit

**Hybrid opportunity:** UNI-Q for broadcast/subscription, explicit mail for request/response?

---

## Convoy System (Work Tracking)

A **convoy** is a persistent tracking unit for batched work across multiple projects.

```
                 🚚 Convoy (hq-cv-abc)
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
       ┌─────────┐  ┌─────────┐  ┌─────────┐
       │ gt-xyz  │  │ gt-def  │  │ bd-abc  │
       │ project1│  │ project1│  │ project2│
       └────┬────┘  └────┬────┘  └────┬────┘
            │            │            │
            ▼            ▼            ▼
       Polecat 1    Polecat 2    Polecat 3
                    "the swarm"
```

**Convoy vs Swarm:**
| Concept | Persistent? | Description |
|---------|-------------|-------------|
| **Convoy** | Yes | Tracking unit - what you create, track, get notified about |
| **Swarm** | No | Ephemeral - workers currently on convoy's issues |

**Quandura mapping:**
- Convoy → Mission (already have this concept)
- Swarm → The set of agents currently working on a mission

Our Mission concept is similar but less formalized. Convoy's explicit tracking and notification system is worth adopting.

---

## Molecules (Workflow Templates)

Molecules are workflow templates that coordinate multi-step work:

```
Formula (source TOML) ─── "Ice-9"
    │
    ▼ bd cook
Protomolecule (frozen template) ─── Solid
    │
    ├─▶ bd mol pour ──▶ Mol (persistent) ─── Liquid
    │
    └─▶ bd mol wisp ──▶ Wisp (ephemeral) ─── Vapor
```

| Term | Description |
|------|-------------|
| **Formula** | Source TOML template defining workflow steps |
| **Protomolecule** | Frozen template ready for instantiation |
| **Molecule** | Active workflow instance with trackable steps |
| **Wisp** | Ephemeral molecule for patrol cycles |
| **Digest** | Squashed summary of completed molecule |

**Navigation commands:**
```bash
bd mol current              # Where am I?
bd ready                    # What step is next?
bd close <step> --continue  # Close and auto-advance
```

**Quandura applicability:** Our missions could benefit from formalized workflow templates:
- Template Registry (already decided in DECISION_LOG)
- Could adopt molecule-like step tracking
- The `--continue` pattern (close and advance) is elegant

---

## Escalation Protocol

Tiered escalation with severity levels:

| Level | Priority | Examples |
|-------|----------|----------|
| **CRITICAL** | P0 | Data corruption, security breach |
| **HIGH** | P1 | Unresolvable conflict, critical bug |
| **MEDIUM** | P2 | Design decision needed, unclear requirements |

**Escalation categories:**
| Category | Description | Default Route |
|----------|-------------|---------------|
| `decision` | Multiple valid paths | Deacon → Mayor |
| `help` | Need guidance | Deacon → Mayor |
| `blocked` | Unresolvable dependency | Mayor |
| `failed` | Unexpected error | Deacon |
| `emergency` | Security/data integrity | Overseer (direct) |
| `gate_timeout` | Async condition failed | Deacon |
| `lifecycle` | Worker stuck | Witness |

**Tiered flow:**
```
Worker → Deacon → Mayor → Overseer (Human)
```

Each tier can resolve OR forward. The escalation chain is tracked.

**Quandura mapping:** Our human escalation (Ⓗ) is similar but less formalized:
- We have the `Ⓗ` symbol for human involvement
- Gas Town's category-based routing is more structured
- Consider adding escalation tiers to our orchestrators

---

## Key Patterns for Quandura

### 1. Propulsion Principle ✓
Already implicit in UNI-Q subscriptions. When a message matches, act immediately.

### 2. Three-Layer Lifecycle ◐
**Adopt for agents:**
- Session = LLM context (ephemeral, can cycle)
- Sandbox = Mission workspace (persistent during mission)
- Slot = Agent identity (persistent until reassigned)

### 3. Watchdog Chain ◐
**Consider adding:**
- Mechanical heartbeat at infrastructure level
- Intelligent triage for "is agent stuck vs thinking"
- Could be a responsibility of Team Orchestrators

### 4. Convoy/Mission Tracking ◐
**Enhance missions with:**
- Explicit progress tracking (X/Y steps)
- Cross-team mission visibility
- Landing notifications

### 5. Molecules/Workflows ○
**Template Registry is decided, but could add:**
- Step-by-step tracking within templates
- `--continue` auto-advance pattern
- Squash/digest for completed workflows

### 6. Structured Escalation ◐
**Already have Ⓗ, could add:**
- Severity levels (CRITICAL/HIGH/MEDIUM)
- Category-based routing (decision/help/blocked/failed)
- Tiered escalation (Team → Department → Human)

### 7. Mail Protocol ○
**Consider for request/response:**
- UNI-Q handles broadcast well
- Explicit mail for point-to-point requests
- Could be the Ⓡ (Request) pattern

---

## Architecture Comparison

| Aspect | Gas Town | Quandura |
|--------|----------|----------|
| **Communication** | Mail (point-to-point) + Files | UNI-Q pub/sub |
| **Work Tracking** | Beads (git-backed issues) | Passports (JSON state) |
| **Persistence** | Git worktrees | Mission Sandboxes |
| **Orchestration** | Mayor (global) | Fractal (per-level) |
| **Human Interface** | Crew workspaces | Ⓗ human agents |
| **Health Monitoring** | Watchdog chain | TBD |
| **Workflows** | Molecules (TOML) | Templates (Registry) |
| **Escalation** | Tiered (Deacon→Mayor→Overseer) | Ⓗ symbol (flat) |

---

## Recommendations for Quandura

### High Priority (Adopt)

1. **Agent Lifecycle Layers**
   - Separate Session (LLM context) from Sandbox (workspace) from Identity (agent)
   - Allow sessions to cycle while preserving work state
   - This supports context window management

2. **Structured Escalation**
   - Add severity levels to escalations
   - Add categories (decision, help, blocked, failed)
   - Consider tiered routing through orchestrators

3. **Health Monitoring**
   - Add heartbeat infrastructure
   - Consider "intelligent triage" pattern for stuck detection
   - Make this a Team Orchestrator responsibility

### Medium Priority (Consider)

4. **Workflow Step Tracking**
   - Add step-by-step progress to templates
   - Consider `--continue` auto-advance pattern
   - Track molecule state separately from mission state

5. **Request/Response Protocol**
   - Formalize the Ⓡ (Request) pattern
   - Could use UNI-Q with response correlation
   - Or add explicit mail for point-to-point

### Low Priority (Research Further)

6. **Git-Backed State**
   - Gas Town uses git extensively for persistence
   - Our PostgreSQL approach is different but valid
   - Git provides version history; PostgreSQL provides queries

---

## Terminology Mapping

| Gas Town | Quandura | Notes |
|----------|----------|-------|
| Town | Department | Top-level organizational unit |
| Rig | Team | Project/functional grouping |
| Mayor | Head Orchestrator | Global coordinator |
| Deacon | (None) | System-level daemon |
| Witness | Team Orchestrator | Health monitoring aspect |
| Refinery | QA Agent | Verification/quality |
| Polecat | Specialist Agent | Ephemeral worker |
| Crew | Human Agent (Ⓗ) | Persistent human workspace |
| Dog | (None) | Infrastructure helpers |
| Convoy | Mission | Work tracking unit |
| Molecule | Workflow Template | Step-by-step process |
| Hook | Subscription | Assignment mechanism |
| Handoff | Context Transfer | Session continuity |

---

## Open Questions

1. **Do we need a Deacon equivalent?**
   - System-level monitoring separate from business logic
   - Could be infrastructure-level, not agent-level

2. **Should we adopt git worktrees for isolation?**
   - Gas Town uses worktrees heavily
   - We're using mission sandboxes differently
   - Trade-offs: git history vs database queries

3. **How granular should workflow tracking be?**
   - Gas Town tracks every molecule step
   - We track mission states
   - More granularity = more visibility but more overhead

4. **Should escalation be tiered through orchestrators?**
   - Gas Town: Worker → Deacon → Mayor → Overseer
   - We could: Agent → Team Orchestrator → Dept Orchestrator → Human
   - Or keep flat with Ⓗ

---

*Created: 2025-01-08*
*Source: https://github.com/annechari-co/gastown*
*Status: Complete*
