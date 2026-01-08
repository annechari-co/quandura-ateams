# Quandura: An Enterprise AI Agent Platform

**A Technical Whitepaper for Founders and Partners**

*Version 1.0 | January 2025*

---

## How to Use This Document

This whitepaper serves three purposes:

1. **Introduction** - Understand what Quandura is and why it matters
2. **Reference** - Look up technical concepts during development
3. **Conversation guide** - Know what questions to ask when something isn't clear

Each section includes a "Questions to Ask" box. If you're reading something and don't understand it, start there.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [The Problem We're Solving](#2-the-problem-were-solving)
3. [The Solution: AI Agent Teams](#3-the-solution-ai-agent-teams)
4. [What Makes Quandura Different](#4-what-makes-quandura-different)
5. [How It Works (Without Jargon)](#5-how-it-works-without-jargon)
6. [Technical Architecture](#6-technical-architecture)
7. [The Business Model](#7-the-business-model)
8. [Development Roadmap](#8-development-roadmap)
9. [Risks and Mitigations](#9-risks-and-mitigations)
10. [Glossary](#10-glossary)
11. [Appendix: Metrics and Benchmarks](#11-appendix-metrics-and-benchmarks)

---

## 1. Executive Summary

### What Is Quandura?

Quandura is a platform for building and running teams of AI agents that perform real work for organizations. Think of it as an "operating system" for deploying AI workers.

**In plain English:**

Instead of using AI as a chatbot that answers questions, Quandura creates specialized AI workers that:
- Have defined roles (researcher, analyst, reviewer, etc.)
- Work together as a team
- Follow structured processes
- Know when to ask humans for help
- Remember what they've learned
- Leave a complete audit trail

### The Vision

**Near-term (1-2 years):** Build a profitable safety consulting business using AI-assisted inspections.

**Medium-term (3-5 years):** Become the AI-powered Risk Management department for small counties that can't afford full staffing.

**Long-term (10+ years):** The "Operating System for Local Governments" - AI teams running entire department operations.

### Why Now?

Three factors make this the right moment:

1. **AI capability** - Large language models (like Claude) can now reason, research, and write at a professional level
2. **Market demand** - The Martinez Act in Maryland requires local governments to implement safety inspection programs they're not staffed for
3. **Founder advantage** - Deep county government experience, existing relationships for testing, and intimate knowledge of Risk Management operations

---

## 2. The Problem We're Solving

### The Staffing Crisis in Local Government

County governments are drowning. They face:

- **Chronic understaffing** - Budget constraints prevent hiring enough people
- **High turnover** - Knowledge walks out the door when employees leave
- **Data overload** - Incident reports, claims, compliance requirements pile up
- **Reactive operations** - No time for proactive analysis or improvement

The result: Injury rates in county governments are **far above private sector rates**. Claims costs are high. Compliance suffers.

### Why Current AI Approaches Don't Work

**Chatbots** answer questions but don't do work. A county Risk Manager doesn't need another thing to chat with - they need help processing the 200 incident reports sitting in their inbox.

**Single-task AI tools** (like document summarizers) help with fragments but don't handle complete workflows. Real work involves multiple steps, multiple people, and judgment calls.

**Generic automation** requires expensive custom development for each workflow. Counties can't afford six-figure implementations.

### What's Actually Needed

Organizations need AI that can:

1. Take ownership of complete workflows, not just individual tasks
2. Coordinate multiple steps and hand off work appropriately
3. Know its limitations and escalate to humans when needed
4. Learn from experience and get better over time
5. Leave audit trails that satisfy government compliance requirements

This is what Quandura provides.

> **Questions to Ask:**
> - "What specific workflows are you targeting first?"
> - "How does this compare to [specific competitor]?"
> - "What happens when the AI makes a mistake?"

---

## 3. The Solution: AI Agent Teams

### What Is an "Agent Team"?

An agent team is a group of specialized AI workers that collaborate to complete a workflow.

**Example: Legal Research Team**

When a county department needs a legal opinion:

```
1. Triage Agent    → Reads the email, understands the question
2. Research Agent  → Searches legal databases, finds relevant cases/statutes
3. Drafting Agent  → Writes the formal legal opinion
4. Review Agent    → Checks citations, logic, and completeness
5. Delivery Agent  → Formats, archives, and sends to requester
```

Each agent has a specific role. They pass work to each other in sequence. An "Orchestrator" agent supervises the process, intervening when things go wrong.

### How This Differs from a Single AI

A single AI trying to do everything would:
- Lose track of where it is in a complex process
- Have no quality checks on its own work
- Struggle with long workflows that exceed its context window
- Have no structure for human oversight

With agent teams:
- Each agent focuses on one thing and does it well
- Work is reviewed by different agents (external validation)
- State is preserved between steps (the "Passport")
- Humans can intervene at defined checkpoints

### The Three Layers

Quandura has three architectural layers:

```
PLATFORM INTELLIGENCE
    The system that improves Quandura itself over time
    (Not built yet - future phase)
                ↓
ORCHESTRATION
    Department heads and team coordinators
    Routes work between teams, handles exceptions
                ↓
EXECUTION
    Individual agent teams doing the actual work
    (Legal Research Team, Safety Team, Claims Team, etc.)
```

> **Questions to Ask:**
> - "Show me the actual workflow for [specific use case]"
> - "What happens if an agent gets stuck?"
> - "How does the Orchestrator decide when to escalate?"

---

## 4. What Makes Quandura Different

### Novel Element #1: Token-Efficient Communication (UNI-Q)

**The problem:** AI models are expensive. Every word they process costs money. When agents talk to each other in prose, it wastes tokens (and money).

**Our solution:** A symbolic grammar called UNI-Q that lets agents communicate in 3-4 tokens instead of 12+.

```
Prose:    "The claims team is actively working on a high-priority task"
UNI-Q:    "Ⓐclaims◉⁺"
```

**Why this matters:**
- Lower API costs (roughly 70% reduction in inter-agent communication)
- Better focus - models pay attention to signal, not filler
- Faster processing

### Novel Element #2: Multi-Resolution Memory ("Zoom-In")

**The problem:** AI can't hold everything in memory at once. Current systems either show too much detail (overwhelming) or too little (missing critical information).

**Our solution:** Every piece of information exists at three levels:

| Level | Size | When Used |
|-------|------|-----------|
| **Micro** | ~20 tokens | Scanning many items quickly |
| **Summary** | ~100 tokens | Reasoning about something |
| **Full** | Unlimited | Deep analysis, drafting, auditing |

The system automatically "zooms in" based on what the agent is trying to do.

**Example:** An orchestrator checking team status sees micros:
```
Ⓣ001✓⟨risk:low⟩  Ⓣ002◉⑤  Ⓣ003⊘⚠
```
(Task 1 complete low-risk, Task 2 active 50%, Task 3 blocked with warning)

If Task 3 needs attention, the system automatically fetches the summary or full content.

### Novel Element #3: Fractal Architecture

**The problem:** Most multi-agent systems have different patterns at different levels, making them complex to understand and debug.

**Our solution:** The same communication pattern at every level.

```
Department Level:  Teams → Department Head → Other Teams
Team Level:        Agents → Team Orchestrator → Other Agents
Agent Level:       Sub-tasks → Agent → Other Sub-tasks
```

Same message format. Same subscription mechanism. Same routing logic. If you understand one level, you understand them all.

### Novel Element #4: Evidence-Based Confidence

**The problem:** Most AI systems report confidence as a single number (like "85% confident"). This is meaningless without context.

**Our solution:** Confidence is a vector with multiple dimensions:

```python
ConfidenceVector:
  score: 0.85           # The headline number
  evidence_count: 12    # How many facts support this?
  evidence_quality: "verified"  # Are they checked or assumed?
  historical_accuracy: 0.92     # When this agent said 85%, how often was it right?
  failure_modes: ["data gap", "unusual situation"]  # What could make this wrong?
```

**Why this matters:** Humans reviewing AI work need to know not just "how confident" but "why confident" and "what could go wrong."

### Novel Element #5: De-Scaffolding (Earned Autonomy)

**The problem:** AI systems either require too much human oversight (inefficient) or too little (risky).

**Our solution:** Agents start with heavy supervision and earn more autonomy based on track record.

An agent can operate with less oversight when ALL of these are true:
- Confidence > 0.95 averaged over 10+ runs
- Error rate < 5% (execution-verified)
- External audit passed (judge agent approval)
- Human override rate < 2% (users rarely correct)

**This is automatic.** Good agents get more freedom. Struggling agents get more checkpoints.

### Novel Element #6: Humans as First-Class Agents

**The problem:** Most AI systems treat humans as external supervisors who interrupt the system.

**Our solution:** Humans are agents in the same system. They have subscriptions, receive messages, and respond using the same patterns.

```
Agent needs help → Sends escalation with category (decision/help/blocked/failed)
                 → Routed to human via same pub/sub system
                 → Human responds (same message format)
                 → Work continues
```

This means the system doesn't have special-case "human override" logic. Humans are just another participant type.

### Novel Element #7: Team Templates

**The problem:** Building each agent team from scratch is expensive and error-prone.

**Our solution:** Teams are defined declaratively in YAML files:

```yaml
team:
  id: legal-research
  name: Legal Research Team

roles:
  - id: triage
    subscriptions: ["Ⓜ:*:legal:*"]
    capabilities: [classify, extract]

workflows:
  - id: standard-research
    steps:
      - id: intake
        agent: triage
        next: research

escalation:
  categories: [decision, help, blocked, failed]
  tiers:
    - level: 1
      target: team_orchestrator
    - level: 2
      target: human
```

Domain experts can define new teams by editing configuration, not writing code.

> **Questions to Ask:**
> - "How much do tokens actually cost? What's the business impact of UNI-Q?"
> - "What if the micro hides something important?"
> - "How do you test that de-scaffolding works correctly?"

---

## 5. How It Works (Without Jargon)

### The Journey of a Work Request

Let's trace what happens when a county department emails the legal team asking for a legal opinion.

**Step 1: Email Arrives**

```
From: HR Director
To: Legal Team Inbox
Subject: Question about remote work policy

Can employees in our department work remotely if they handle
confidential records? Need to know before next week's meeting.
```

**Step 2: Triage Agent Reads the Email**

The Triage Agent parses the email and creates a structured understanding:

- **Question:** Can employees handling confidential records work remotely?
- **Department:** HR
- **Urgency:** Priority (meeting deadline mentioned)
- **Complexity:** Moderate (needs policy review + maybe case law)

It creates a "Passport" - a document that will travel with this work through the entire process.

**Step 3: Research Agent Investigates**

The Research Agent searches:
- State employment laws
- County policies on remote work
- County policies on confidential records
- Past legal opinions from this office

It finds relevant sources and creates a research memo.

**Step 4: Drafting Agent Writes the Opinion**

Using the research memo, the Drafting Agent writes a formal legal opinion:
- Question Presented
- Brief Answer
- Facts (as understood)
- Analysis (with citations)
- Conclusion

**Step 5: Review Agent Checks the Work**

This is critical. The Review Agent:
- Verifies every citation actually says what we claim
- Checks that the logic follows from the sources
- Ensures the question is actually answered
- Compares with past opinions for consistency

If there are problems, it sends back for revision.

**Step 6: Delivery Agent Sends the Opinion**

Once approved:
- Formats the document with office letterhead
- Writes a cover email
- Archives in the knowledge base (for future reference)
- Sends to the HR Director

**Step 7: Passport Updated and Stored**

The Passport now contains the complete record:
- Original request
- Research conducted
- Sources found
- Draft versions
- Review results
- Final output
- Time taken at each step

This is the audit trail.

### What the Human Attorney Sees

The human attorney (if they're overseeing) can:
- View status of all active requests
- See confidence scores for pending items
- Get alerts when escalation is needed
- Review and approve before sending
- Drill into any item's full history

They're not reading every opinion. They're supervising a team.

### When Things Go Wrong

**Scenario: Research Agent Can't Find Relevant Law**

The Research Agent hits a dead end. It escalates with category "help" and includes:
- What it searched
- What it found (nothing relevant)
- Its confidence: 0.4 (too low to proceed)

The Orchestrator routes this to the human attorney, who either:
- Provides guidance on where to look
- Takes over the research
- Decides the question can't be answered and informs the requester

The system doesn't guess. It knows its limits.

> **Questions to Ask:**
> - "Walk me through what happens with [specific scenario]"
> - "What does the human dashboard actually look like?"
> - "How long does this take compared to a human doing it manually?"

---

## 6. Technical Architecture

This section goes deeper for those who want to understand implementation details.

### Core Data Structure: The Passport

Every piece of work has a "Passport" - a structured document that travels with the work:

```python
class Passport:
    # Identity
    mission_id: str       # Unique identifier
    team_id: str          # Which team owns this
    created_at: datetime

    # Mission
    objective: str        # What we're trying to accomplish
    success_criteria: list[str]   # How we know we're done
    constraints: list[str]        # What we can't do

    # State
    current_phase: str    # Where in the workflow
    ledger: list[LedgerEntry]     # Append-only log of all work
    artifacts: list[Artifact]     # Documents, files produced

    # Routing
    next_agent: str | None        # Who works on this next
    escalation_required: bool     # Needs human attention?

    # Confidence
    confidence: ConfidenceVector  # How sure are we?
    evidence: list[Evidence]      # What backs this up?
    failure_risks: list[FailureRisk]  # What could go wrong?

    # Audit
    decision_log: list[Decision]  # Every choice made
    checkpoint_id: str            # For recovery
```

The Passport is the "source of truth." Any agent can read it. Only the current agent can write to it. Everything is logged.

### Agent Lifecycle: Three Layers

Each agent has three independent lifecycles:

| Layer | What It Is | Lifespan |
|-------|-----------|----------|
| **Identity** | Who the agent is (role, permissions, history) | Persistent |
| **Sandbox** | Current workspace (mission-specific files, state) | Per-mission |
| **Session** | LLM context window (what the AI is "thinking about") | Ephemeral |

**Why this matters:**

The AI's "session" can be cycled (to manage context window limits) without losing the agent's identity or the work in progress. The system can restart an agent's session while preserving everything important.

### Memory Architecture

Memory is stored in four layers:

| Layer | What It Stores | Example |
|-------|---------------|---------|
| **Strategic** | Goals, values, priorities | "Reduce claims costs by 15%" |
| **Operational** | Policies, rules, procedures | "All contracts over $50K require legal review" |
| **Entity** | People, places, things | "ABC Company - vendor since 2019, good history" |
| **Event** | Things that happened | "Contract review completed 2025-01-08, approved with 3 redlines" |

Each item has the three resolution levels (micro/summary/full) described earlier.

Memory is stored in:
- **PostgreSQL** - Structured data, relationships, metadata
- **ChromaDB** - Vector embeddings for semantic search ("find similar items")

### Communication Protocol

Agents communicate using UNI-Q messages through their orchestrator (hub-and-spoke):

```
Agent A → Orchestrator → Agent B
              ↓
        (logged, routed,
         possibly intercepted)
```

Message types:
- **S** (Status) - "Here's my current state"
- **Q** (Query) - "I need information"
- **D** (Delegate) - "Do this work"
- **A** (Acknowledge) - "Got it"
- **N** (Notify) - "FYI update"
- **R** (Result) - "Here's what I produced"

### Escalation System

When agents need help, they escalate with a category:

| Category | Meaning | Example |
|----------|---------|---------|
| **decision** | Multiple valid paths, need guidance | "Should we use strict or lenient interpretation?" |
| **help** | Need information or advice | "Can't find relevant case law" |
| **blocked** | Can't proceed, dependency issue | "Waiting for client response" |
| **failed** | Something broke | "Legal database API returned error" |
| **emergency** | Security or data integrity issue | "Detected possible data breach" |

Escalations route through tiers:
```
Agent → Team Orchestrator → Department Head → Human
```

Each tier can resolve the issue or forward it up.

### Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| Orchestration | LangGraph | State machines with checkpointing |
| LLM | Claude (Anthropic) | Best reasoning, safety features |
| Database | PostgreSQL | Relational data, row-level security |
| Vector Store | ChromaDB | Semantic search, embeddings |
| Cache | Redis | Fast state access, pub/sub |
| API | FastAPI | Modern Python, async |
| Frontend | React + TypeScript | Type safety, component model |

> **Questions to Ask:**
> - "What happens if PostgreSQL goes down mid-workflow?"
> - "How do you handle LLM rate limits?"
> - "What's the latency for a typical agent handoff?"

---

## 7. The Business Model

### Phase 1: Safety Consulting (Revenue Generation)

**The Opportunity:** Maryland's Martinez Act requires all local governments to implement safety inspection programs. Most aren't ready. They need help.

**Our Model:**
1. Launch a consulting firm offering safety inspection services
2. Human inspectors use our AI-assisted Inspection App
3. Safety Agent Team processes findings, generates reports
4. We deliver faster, cheaper, higher-quality inspections than competitors
5. Each engagement is a touchpoint for upselling

**Unit Economics:**
- Traditional consulting: Human does everything, high labor cost
- Our model: AI handles 60-80% of work, human focuses on judgment calls
- Result: Same quality, lower cost, or same cost, higher volume

### Phase 2: Agentic Risk Management Department

**The Opportunity:** Small counties can't afford to stand up full Risk Management departments. They need the capability without the headcount.

**Our Model:**
- License or sell an "AI Risk Management Department"
- Teams handle: Incident investigation, claims processing, compliance monitoring, analytics
- County gets department-level capability without department-level staffing

**Pricing Potential:**
- Full-time Risk Manager: $80-150K/year + benefits + overhead
- Our solution: Fraction of that cost
- Clear ROI: Reduced claims = reduced spending (self-insured counties feel this directly)

### Phase 3: Agentic TPA (Third-Party Administrator)

**The Opportunity:** Most US counties are self-insured but use TPAs to manage claims. These TPAs are terrible:
- High turnover of claims managers
- Overloaded workloads
- Bad scheduling
- Poor communication

**Our Model:**
- Become the AI-powered TPA
- Or license our system to existing TPAs
- All bidding information is public - we can precisely calculate how much to underbid while remaining profitable

**Why We Win:**
- Agents don't burn out
- Consistent quality (no "good adjuster vs bad adjuster")
- 24/7 availability
- Perfect audit trails

### Revenue Projections

We're not including specific numbers because they depend on execution. The key insight:

**Consulting revenue comes first.** We don't need investment to get started. Profitable operations validate the model before we seek funding.

> **Questions to Ask:**
> - "What's the pricing strategy for consulting vs licensing?"
> - "How do you compete with established TPAs?"
> - "What's the customer acquisition cost?"

---

## 8. Development Roadmap

### Current Status

**Built:**
- Core backend structure (FastAPI, PostgreSQL, Redis)
- Passport schema and confidence tracking
- LangGraph orchestration with checkpointing
- Base agent class
- Basic 2-agent team wiring
- REST API for missions

**In Progress:**
- Memory storage layer
- Vector embeddings (ChromaDB)
- Librarian agent
- Team templates (YAML-based)

### Phase 1: Core Engine Completion

**Goal:** Working team system validated with Legal Research test harness

| Component | Status |
|-----------|--------|
| Memory Storage | Building |
| Embeddings (ChromaDB) | Building |
| Librarian Agent | Planned |
| Judge Agent | Planned |
| Team Templates | Planned |
| Agent Lifecycle | Planned |
| Health Monitoring | Planned |
| Escalation System | Planned |
| Legal Research Team | Planned |
| Tests (>80% coverage) | Planned |

**Validation Milestone:** Legal Research Team processes test request end-to-end

### Phase 2: Safety Team + Inspection App

**Goal:** Real-world deployable product

| Component | Status |
|-----------|--------|
| Inspection App Backend | Planned |
| Safety Team Agents | Planned |
| Memory Integration | Planned |
| Field App (Mobile PWA) | Planned |
| PDF Report Generation | Planned |

**Validation Milestone:** Real inspectors use it in the field

### Phase 3: Consulting Launch

**Goal:** Profitable operations

- Consulting firm legal setup
- Initial client engagements
- Iteration based on field feedback
- Case studies and performance data

### Phase 4: Risk Management Product

**Goal:** Sellable department-as-a-service

- Full Risk Management Team suite
- Cross-team orchestration
- Customer deployment tooling

### Phase 5: Platform Intelligence

**Goal:** Self-improving system

- Janitor agents (per-team observation)
- Housekeeper (platform-wide optimization)
- Research scouts (external knowledge intake)
- Proposal queue with human approval

**Timing:** When manual monitoring becomes burdensome (multiple teams in production)

> **Questions to Ask:**
> - "What's the critical path? What blocks what?"
> - "How do we know Phase 1 is actually done?"
> - "What could push the timeline right?"

---

## 9. Risks and Mitigations

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM costs higher than expected | Margin squeeze | UNI-Q reduces tokens; monitor closely |
| LLM quality degrades with updates | Quality issues | Pin model versions; regression testing |
| Complex workflows exceed context | Failures | Session cycling; checkpoint/resume |
| Integration with legacy systems | Delays | Start with email-based integration |

### Business Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Consulting competes with product | Distraction | Clear separation; consulting funds product |
| Government procurement cycles slow | Cash flow | Start with consulting (faster sales) |
| Competitor with similar approach | Market share | Move fast; deep domain expertise |
| Key person dependency | Continuity | Document everything; train partner early |

### Regulatory/Compliance Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI decisions create liability | Legal exposure | Human approval for high-stakes; insurance |
| Data breach | Reputation, fines | SOC 2 compliance; encryption; access controls |
| Government AI restrictions | Market access | Stay ahead of regulations; adaptable architecture |

### The Biggest Risk

**Scope creep.** The vision is huge. The temptation to build everything at once is real.

**Mitigation:** Ruthless prioritization. Phase 1 is core engine. Phase 2 is Safety Team (revenue). Everything else waits.

> **Questions to Ask:**
> - "What's the single biggest risk you're most worried about?"
> - "What's the fallback if [specific component] doesn't work?"
> - "How do you decide what NOT to build?"

---

## 10. Glossary

**Agent** - An AI worker with a specific role. Has access to tools, memory, and can communicate with other agents.

**Checkpoint** - A saved state of work in progress. Allows recovery if something fails.

**Confidence Vector** - A multi-dimensional measure of how sure an agent is about its work, including what could go wrong.

**De-scaffolding** - The process by which agents earn more autonomy based on track record.

**Escalation** - When an agent needs human help or decision-making.

**Fractal Architecture** - The same patterns repeated at every level (department, team, agent).

**Judge Agent** - An agent that reviews other agents' work for quality and correctness.

**LangGraph** - The framework we use for orchestrating agent workflows with state management.

**Librarian** - An agent that manages knowledge retrieval and memory for a team.

**LLM (Large Language Model)** - The AI model (like Claude) that powers agent reasoning.

**Memory Layer** - One of four levels of information storage (Strategic, Operational, Entity, Event).

**Micro/Summary/Full** - The three resolution levels for any piece of information.

**Mission** - A unit of work being processed by an agent team.

**Orchestrator** - An agent that coordinates other agents, routes work, and handles exceptions.

**Passport** - The structured document that travels with work through a workflow, containing all state and history.

**Resolution** - The level of detail retrieved (micro, summary, or full).

**Sandbox** - An isolated workspace for a specific mission.

**Session** - The active context window of an LLM (ephemeral, can be cycled).

**Subscription** - A pattern that an agent registers to receive notifications about.

**Token** - The unit of text that LLMs process. More tokens = more cost.

**UNI-Q** - Our token-efficient grammar for agent communication.

---

## 11. Appendix: Metrics and Benchmarks

### Token Efficiency (UNI-Q)

| Message Type | Prose | UNI-Q | Savings |
|--------------|-------|-------|---------|
| Status update | ~15 tokens | ~4 tokens | 73% |
| Task assignment | ~25 tokens | ~8 tokens | 68% |
| Query | ~20 tokens | ~6 tokens | 70% |

### Quality Targets (Legal Research Team)

| Metric | Target | Why |
|--------|--------|-----|
| Response Time (routine) | < 5 days | Matches human performance |
| Response Time (priority) | < 2 days | Emergency capability |
| Citation Accuracy | > 99% | Legal requirement |
| Escalation Rate | < 20% | Efficiency measure |
| Revision Rate | < 15% | Quality measure |

### De-Scaffolding Thresholds

For an agent to earn more autonomy, ALL must be true:

| Criterion | Threshold |
|-----------|-----------|
| Confidence score | > 0.95 (averaged over 10+ runs) |
| Error rate | < 5% (execution-verified) |
| External audit | Passed (judge agent approval) |
| Human override rate | < 2% |

### Health Monitoring Thresholds

| Heartbeat Age | State | System Action |
|---------------|-------|---------------|
| < 5 minutes | Fresh | None |
| 5-15 minutes | Stale | Check for pending work |
| > 15 minutes | Very Stale | Alert orchestrator |

### Cost Projections (Illustrative)

Based on Claude API pricing (subject to change):

| Activity | Tokens/Operation | Cost Estimate |
|----------|------------------|---------------|
| Simple triage | ~500 | $0.01-0.02 |
| Research query | ~2,000 | $0.04-0.06 |
| Draft review | ~3,000 | $0.06-0.09 |
| Full legal opinion | ~10,000 | $0.20-0.30 |

**Note:** These are rough estimates. Actual costs depend on model choice, complexity, and optimization.

---

## Final Notes

### What This Document Doesn't Cover

- Detailed API specifications (see Architecture doc)
- Specific implementation code (see codebase)
- Financial projections (see business plan)
- Compliance certifications (see compliance research)

### How to Get Deeper

| Topic | Reference Document |
|-------|-------------------|
| Full technical spec | `QUANDURA_ARCHITECTURE.md` |
| Build sequence | `BUILD_PLAN.md` |
| Business context | `ENTERPRISE_PLAN.md` |
| Legal Research Team spec | `teams/LAW_OFFICE_LEGAL_RESEARCH.md` |
| Safety Team spec | `teams/SAFETY_TEAM.md` |
| UNI-Q grammar | `research/UNIQ_SPEC.md` |
| Field App spec | `field-app/FIELD_APP_SPEC.md` |

### Contact Points

When you have questions during development:

1. **Technical questions** → Check Architecture doc first, then ask
2. **Business questions** → Check Enterprise Plan first, then ask
3. **"Why did we decide X?"** → Check Decision Log or ask for context
4. **"What should we build next?"** → Check Build Plan

---

*This whitepaper is a living document. It will be updated as the project evolves.*

*Last Updated: 2025-01-08*
*Document Version: 1.0*
