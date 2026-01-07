# Quandura: Core Architecture Specification

## Executive Summary

Quandura is an enterprise AI agent platform targeting local government operations. The initial beachhead is Risk Management departments, with the long-term vision of becoming the "OS for Local Governments" - eventually running entire government operations with minimal human staff.

**Near-term Focus:** Safety Team + Inspection App for consulting firm launch (Martinez Act opportunity in Maryland).

**Deployment Model:** Palantir-style embedded teams that learn workflows and build custom agent teams for each client.

**Service Model:** Safety consulting first (revenue generation), then Risk Management product, then TPA market disruption.

**Development Strategy:**
- Legal Research Team = test harness for team system architecture (not deployment target)
- Safety Team = first real-world deployment (founder has deep domain expertise + testing relationships)

---

## System Vision

### What Quandura Does

1. **Department-Level Agent Teams**: Each government department gets a team of specialized AI agents that handle their workflows
2. **Voice + Email Intake**: Citizens and staff interact via phone (voice AI) or email
3. **Structured Workflows**: Agents follow defined processes with checkpoints and human escalation
4. **Continuous Learning**: Platform intelligence layer identifies improvements and proposes changes (human-approved)
5. **Full Audit Trail**: Complete traceability for government compliance requirements

### Design Principles

1. **Multi-tenant from day one** - Every decision considers tenant isolation
2. **Evidence-based confidence** - Vectors not scalars, tied to historical accuracy
3. **External validation** - Self-correction requires external feedback (Judge agents, execution verification)
4. **Layered organizational memory** - Strategic → Operational → Entity → Event with multi-resolution content
5. **Hub-and-spoke communication** - Orchestrator/Librarian as hubs, specialists talk only to hubs
6. **De-scaffolding** - Start structured, loosen as confidence grows (multi-factor triggers)
7. **Context sandboxing** - Minimal context per agent for cost efficiency and focus
8. **Hybrid symbolic + neural** - Hard rules for compliance/safety, neural reasoning for complex tasks
9. **Double-loop learning** - After Action Review (AAR) + memory injection for continuous improvement
10. **Execution-based verification** - Run generated outputs to verify, don't just review them
11. **Precedent-based reasoning** - Capture the "why" behind decisions via typed relationships
12. **Team-pluggable schemas** - Universal layer structure, domain-specific types per team

---

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PLATFORM INTELLIGENCE LAYER                           │
│                                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────────┐  │
│   │  Housekeeper │←─│   Janitors   │  │      Research Scouts             │  │
│   │  (Aggregate) │  │  (Per-team)  │  │  (Papers, blogs, releases)       │  │
│   └──────────────┘  └──────────────┘  └──────────────────────────────────┘  │
│          │                                          │                        │
│          └──────────────┬───────────────────────────┘                        │
│                         ▼                                                    │
│               ┌──────────────────┐                                           │
│               │ Proposal System  │ → Human Review → Approved Changes         │
│               └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATION LAYER                                  │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │                    Department Head Agent                            │    │
│   │         (Meta-orchestrator with configurable authority)             │    │
│   └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          ▼                         ▼                         ▼              │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│   │   Team A     │         │   Team B     │         │   Team C     │        │
│   │ Orchestrator │         │ Orchestrator │         │ Orchestrator │        │
│   └──────────────┘         └──────────────┘         └──────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXECUTION LAYER                                     │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                     Specialist Agents                                 │  │
│   │                                                                       │  │
│   │   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │  │
│   │   │ Triage  │ │Research │ │ Draft   │ │ Review  │ │Delivery │       │  │
│   │   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘       │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                      Librarians (Per-team)                            │  │
│   │            Knowledge persistence, retrieval, indexing                 │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Zone Architecture

Sensitive data stays isolated. Only summaries and decisions cross boundaries.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SENSITIVE DATA ZONE                                   │
│                    (Customer's environment or encrypted)                     │
│                                                                              │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│   │ Employee PII │  │ Claims Data  │  │  Incident    │                      │
│   │              │  │              │  │  Reports     │                      │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                      │
│          └─────────────────┼─────────────────┘                               │
│                            ▼                                                  │
│                    ┌───────────────┐                                         │
│                    │   PROCESSING  │  Agents work here with full data        │
│                    │    SANDBOX    │  Context-limited, task-specific         │
│                    └───────┬───────┘                                         │
│                            │                                                  │
│                            ▼ Only summaries, decisions, and                   │
│                              structured outputs cross this line               │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────────┐
│                        PLATFORM ZONE                                         │
│                    (Our cloud infrastructure)                                │
│                            ▼                                                  │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                      │
│   │ Orchestration│  │   Platform   │  │    Team      │                      │
│   │    Logic     │  │ Intelligence │  │  Templates   │                      │
│   └──────────────┘  └──────────────┘  └──────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Principle:** Raw PII never leaves the sensitive zone. Agents receive task-specific context and return structured outputs.

---

## Context Sandboxing

Each agent receives minimal, focused context. This serves three purposes:

1. **Cost efficiency** - Don't send 50k tokens to every agent
2. **Quality** - Focused context = better reasoning, fewer hallucinations
3. **Security** - Agents can't leak what they don't have

### Context Extraction Pattern

```python
class ContextSandbox:
    """
    Creates minimal, focused context for specialist agents.

    The orchestrator has full context. Specialists get only what they need.
    """

    def __init__(self, passport: Passport, librarian: "Librarian"):
        self.passport = passport
        self.librarian = librarian

    async def create_context(
        self,
        agent_type: str,
        task_description: str,
        max_tokens: int = 4000,
    ) -> "SandboxedContext":
        """
        Extract minimal context for a specialist agent.

        Args:
            agent_type: Type of agent that will receive this context
            task_description: What the agent needs to accomplish
            max_tokens: Token budget for this context
        """
        # Start with task-specific info from passport
        context = SandboxedContext(
            task=task_description,
            constraints=self.passport.mission.constraints,
            success_criteria=self._extract_relevant_criteria(agent_type),
        )

        # Query librarian for relevant prior knowledge
        relevant_knowledge = await self.librarian.query(
            query=task_description,
            limit=5,
            max_tokens=max_tokens // 2,
        )
        context.prior_knowledge = relevant_knowledge

        # Add only the artifacts this agent needs
        context.input_artifacts = self._select_artifacts(agent_type)

        # Define expected output schema
        context.output_schema = self._get_output_schema(agent_type)

        return context

    def _extract_relevant_criteria(self, agent_type: str) -> List[str]:
        """Only include success criteria relevant to this agent's task."""
        # Filter based on agent type
        pass

    def _select_artifacts(self, agent_type: str) -> Dict[str, str]:
        """Only include artifacts this agent needs to reference."""
        # Map agent types to required artifacts
        pass

    def _get_output_schema(self, agent_type: str) -> Dict[str, Any]:
        """Define what output structure is expected."""
        # Pydantic schema serialized
        pass


class SandboxedContext(BaseModel):
    """Minimal context provided to a specialist agent."""

    # What to do
    task: str
    constraints: List[str]
    success_criteria: List[str]

    # What to know
    prior_knowledge: List[str]  # Relevant excerpts, not full documents
    input_artifacts: Dict[str, str]  # Only what's needed

    # What to produce
    output_schema: Dict[str, Any]  # Expected output structure

    # Boundaries
    tools_available: List[str]  # Only tools this agent can use
    escalation_conditions: List[str]  # When to stop and escalate
```

### Flow: Orchestrator → Sandboxed Specialist

```
Full Context (Orchestrator)
         │
         │ ContextSandbox.create_context()
         ▼
┌─────────────────────────────┐
│    Sandboxed Context        │  ← Minimal, focused
│                             │
│    task: "Draft the legal   │
│           opinion intro"    │
│                             │
│    prior_knowledge:         │
│    - [3 relevant excerpts]  │
│                             │
│    input_artifacts:         │
│    - research_memo (ref)    │
│                             │
│    output_schema:           │
│    - DraftIntroSection      │
│                             │
│    tools_available:         │
│    - citation_formatter     │
│    - style_checker          │
└─────────────────────────────┘
         │
         │ Specialist works in isolation
         │ (Cannot access full passport)
         ▼
    DraftIntroSection
         │
         │ Only structured output returns
         ▼
Full Context (Orchestrator)
    - Validates output
    - Updates passport
    - Routes to next agent
```

---

## Dual-Loop Orchestration (Magentic-One Pattern)

Based on the Magentic-One paper: separate planning from execution.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           OUTER LOOP (Planning)                              │
│                                                                              │
│   Team Orchestrator analyzes mission and creates execution plan              │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  1. Decompose mission into sub-tasks                                 │   │
│   │  2. Identify which specialists are needed                            │   │
│   │  3. Determine execution order and dependencies                       │   │
│   │  4. Set checkpoints for re-planning                                  │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────────────────┐
│                           INNER LOOP (Execution)                             │
│                                    ▼                                         │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐                 │
│   │  Task 1 │───▶│  Task 2 │───▶│  Task 3 │───▶│  Task 4 │                 │
│   │Specialist│    │Specialist│    │Specialist│    │Specialist│               │
│   └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘                 │
│        │              │              │              │                        │
│        └──────────────┴──────────────┴──────────────┘                        │
│                              │                                               │
│                              ▼                                               │
│                    ┌──────────────────┐                                      │
│                    │ Checkpoint Check │                                      │
│                    │ Progress OK?     │                                      │
│                    └────────┬─────────┘                                      │
│                             │                                                │
│              ┌──────────────┼──────────────┐                                │
│              ▼              │              ▼                                │
│         Continue        Re-plan       Escalate                              │
│        (inner loop)   (outer loop)    (human)                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Re-Planning Triggers

```python
class ReplanningTrigger(BaseModel):
    """Conditions that trigger return to outer loop."""

    # Automatic triggers
    task_failed: bool = False
    confidence_below_threshold: bool = False  # < 0.7
    unexpected_output: bool = False
    dependency_changed: bool = False

    # Checkpoint triggers
    checkpoint_reached: bool = False
    time_budget_exceeded: bool = False

    # External triggers
    new_information_received: bool = False
    human_intervention: bool = False

    def should_replan(self) -> bool:
        return any([
            self.task_failed,
            self.confidence_below_threshold,
            self.unexpected_output,
            self.dependency_changed,
            self.checkpoint_reached and self._checkpoint_requires_replan(),
            self.new_information_received,
            self.human_intervention,
        ])
```

---

## Hybrid Symbolic + Neural Architecture

For high-stakes government work, we combine hard rules with neural reasoning.

```python
class SymbolicRuleEngine:
    """
    Hard rules that CANNOT be overridden by neural reasoning.

    Used for: compliance, safety, legal requirements, data handling.
    """

    def __init__(self):
        self.rules: List[Rule] = []

    def add_rule(self, rule: "Rule") -> None:
        """Add an immutable rule."""
        self.rules.append(rule)

    def check(self, action: "ProposedAction") -> "RuleCheckResult":
        """
        Check a proposed action against all rules.

        Returns BLOCK if any rule is violated (no neural override possible).
        """
        violations = []
        for rule in self.rules:
            if rule.applies_to(action) and not rule.permits(action):
                violations.append(RuleViolation(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    reason=rule.explain_violation(action),
                ))

        if violations:
            return RuleCheckResult(
                permitted=False,
                violations=violations,
                override_possible=False,  # NEVER for symbolic rules
            )
        return RuleCheckResult(permitted=True)


class Rule(BaseModel):
    """An immutable compliance/safety rule."""

    id: str
    name: str
    category: Literal["compliance", "safety", "legal", "data_handling"]
    description: str

    # Rule logic (simplified - real implementation would be more complex)
    condition: str  # When this rule applies
    requirement: str  # What must be true

    def applies_to(self, action: "ProposedAction") -> bool:
        """Check if this rule applies to the proposed action."""
        # Evaluate condition against action
        pass

    def permits(self, action: "ProposedAction") -> bool:
        """Check if the action satisfies the requirement."""
        # Evaluate requirement against action
        pass

    def explain_violation(self, action: "ProposedAction") -> str:
        """Explain why the action violates this rule."""
        pass


# Example rules for government context
GOVERNMENT_RULES = [
    Rule(
        id="pii-no-external",
        name="PII Cannot Leave Secure Zone",
        category="data_handling",
        description="PII must never be sent to external APIs or logged in plain text",
        condition="action.involves_pii == True",
        requirement="action.destination in ['secure_zone', 'encrypted_storage']",
    ),
    Rule(
        id="high-stakes-human-review",
        name="High Stakes Actions Require Human Review",
        category="safety",
        description="Actions affecting budget, personnel, or legal matters require human approval",
        condition="action.stakes_level == 'high'",
        requirement="action.has_human_approval == True",
    ),
    Rule(
        id="audit-all-decisions",
        name="All Decisions Must Be Logged",
        category="compliance",
        description="Every decision must be recorded in the audit trail",
        condition="action.is_decision == True",
        requirement="action.audit_entry_created == True",
    ),
]
```

### Integration: Neural Proposes, Symbolic Validates

```
Neural Agent (Claude)
    │
    │ Proposes action
    ▼
┌─────────────────────┐
│  Symbolic Rule      │
│     Engine          │
│                     │
│  - PII rules        │
│  - Safety rules     │
│  - Compliance       │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  PERMIT      BLOCK
     │           │
     ▼           ▼
  Execute    Return to
  Action     Agent with
             violation
             explanation
```

---

## Core State Schema: The Passport

The Passport is the JSON state object that travels between agents. It is the single source of truth for any work item.

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4


class ConfidenceVector(BaseModel):
    """Evidence-based confidence with historical calibration."""

    value: float = Field(ge=0.0, le=1.0, description="Current confidence 0-1")
    evidence_count: int = Field(default=0, description="Number of supporting sources")
    evidence_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    historical_accuracy: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How accurate this agent has been on similar tasks"
    )
    failure_modes: List[str] = Field(
        default_factory=list,
        description="Known failure patterns for this type of task"
    )
    calibration_samples: int = Field(default=0, description="Training samples for this pattern")


class LedgerEntry(BaseModel):
    """Immutable record of an agent action."""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    action: str
    inputs_summary: str
    outputs_summary: str
    duration_ms: int
    tokens_used: int = 0
    cost_usd: float = 0.0
    confidence: ConfidenceVector
    tool_calls: List[str] = Field(default_factory=list)
    notes: str = ""


class RoutingInfo(BaseModel):
    """Where the passport should go next."""

    next_agent: Optional[str] = None
    fallback_agent: Optional[str] = None
    escalation_required: bool = False
    escalation_reason: Optional[str] = None
    priority: Literal["low", "normal", "high", "urgent"] = "normal"
    deadline: Optional[datetime] = None


class Mission(BaseModel):
    """What we're trying to accomplish."""

    objective: str
    constraints: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    requester_id: str
    requester_department: str
    matter_type: str
    sub_tasks: List[str] = Field(default_factory=list)


class Passport(BaseModel):
    """
    Core state object that travels between agents.

    This is the single source of truth for any work item in the system.
    """

    # Identity
    id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    team_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Mission
    mission: Mission

    # State
    status: Literal["pending", "in_progress", "blocked", "completed", "failed", "escalated"] = "pending"
    current_agent: Optional[str] = None
    checkpoint_id: Optional[str] = None  # LangGraph checkpoint reference

    # Routing
    routing: RoutingInfo = Field(default_factory=RoutingInfo)

    # Audit trail (append-only)
    ledger: List[LedgerEntry] = Field(default_factory=list)

    # Working memory (mutable, agent-specific)
    context: Dict[str, Any] = Field(default_factory=dict)

    # Artifacts produced
    artifacts: Dict[str, str] = Field(default_factory=dict)  # name -> storage_ref

    # Quality tracking
    overall_confidence: ConfidenceVector = Field(default_factory=ConfidenceVector)
    revision_count: int = 0

    def add_ledger_entry(
        self,
        agent_id: str,
        action: str,
        inputs_summary: str,
        outputs_summary: str,
        duration_ms: int,
        confidence: ConfidenceVector,
        **kwargs
    ) -> None:
        """Append a new entry to the immutable ledger."""
        entry = LedgerEntry(
            agent_id=agent_id,
            action=action,
            inputs_summary=inputs_summary,
            outputs_summary=outputs_summary,
            duration_ms=duration_ms,
            confidence=confidence,
            **kwargs
        )
        self.ledger.append(entry)
        self.updated_at = datetime.utcnow()
```

### Extended Passport for Legal Research Team

```python
class Citation(BaseModel):
    """Legal citation with metadata."""

    citation_text: str  # e.g., "Cal. Gov. Code § 12345"
    source_type: Literal["statute", "case", "regulation", "ag_opinion", "prior_opinion"]
    jurisdiction: str
    date: Optional[str] = None
    url: Optional[str] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    excerpt: Optional[str] = None


class LegalResearchPassport(Passport):
    """Extended Passport for legal research workflows."""

    # Legal-specific fields
    matter_type: str  # employment, contracts, liability, etc.
    requesting_department: str

    # Research state
    sources_searched: List[str] = Field(default_factory=list)
    key_authorities: List[Citation] = Field(default_factory=list)
    conflicts_found: List[str] = Field(default_factory=list)

    # Draft state
    draft_version: int = 0
    review_status: Literal["pending", "in_review", "approved", "revision_needed"] = "pending"

    # Quality metrics
    citation_accuracy: Optional[float] = None
    reasoning_confidence: Optional[float] = None
    consistency_with_prior: Optional[float] = None

    # SLA tracking
    sla_deadline: Optional[datetime] = None
    days_in_progress: int = 0
```

---

## Agent Lifecycle

### Agent Base Class

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T', bound=Passport)


class BaseAgent(ABC, Generic[T]):
    """Base class for all agents in the system."""

    def __init__(
        self,
        agent_id: str,
        team_id: str,
        tenant_id: str,
        llm_client: Any,  # Claude client
        tools: List[Any],
        memory: "MemoryStore",
    ):
        self.agent_id = agent_id
        self.team_id = team_id
        self.tenant_id = tenant_id
        self.llm = llm_client
        self.tools = tools
        self.memory = memory
        self._calibration_data: Dict[str, float] = {}

    @abstractmethod
    async def process(self, passport: T) -> T:
        """
        Process the passport and return updated version.

        This is the main entry point for agent work.
        """
        pass

    @abstractmethod
    def can_handle(self, passport: T) -> bool:
        """Check if this agent can handle the given passport."""
        pass

    def calculate_confidence(
        self,
        evidence_count: int,
        evidence_quality: float,
        task_type: str,
    ) -> ConfidenceVector:
        """Calculate evidence-based confidence for current work."""
        historical = self._calibration_data.get(task_type, 0.5)
        failure_modes = self._get_failure_modes(task_type)

        return ConfidenceVector(
            value=min(evidence_quality, historical),
            evidence_count=evidence_count,
            evidence_quality=evidence_quality,
            historical_accuracy=historical,
            failure_modes=failure_modes,
            calibration_samples=self._get_sample_count(task_type),
        )

    def _get_failure_modes(self, task_type: str) -> List[str]:
        """Return known failure modes for this task type."""
        # Populated from historical data
        return []

    def _get_sample_count(self, task_type: str) -> int:
        """Return number of calibration samples."""
        return 0

    async def escalate(
        self,
        passport: T,
        reason: str,
        suggested_handler: Optional[str] = None,
    ) -> T:
        """Escalate to human or higher-authority agent."""
        passport.status = "escalated"
        passport.routing.escalation_required = True
        passport.routing.escalation_reason = reason
        passport.routing.next_agent = suggested_handler
        return passport
```

### Agent Communication Pattern

```
Hub-and-Spoke Model:

                    ┌───────────────────┐
                    │   Department Head │
                    │   (Meta-Hub)      │
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌───────────┐       ┌───────────┐       ┌───────────┐
    │  Team A   │       │  Team B   │       │  Team C   │
    │   Hub     │       │   Hub     │       │   Hub     │
    └─────┬─────┘       └───────────┘       └───────────┘
          │
    ┌─────┼─────┬─────────────┐
    ▼     ▼     ▼             ▼
  ┌───┐ ┌───┐ ┌───┐     ┌──────────┐
  │ A │ │ B │ │ C │     │ Librarian│
  └───┘ └───┘ └───┘     │  (Hub)   │
   Specialists          └──────────┘

Rules:
- Specialists ONLY talk to their Team Orchestrator
- Specialists can query their Team Librarian
- Team Orchestrators report to Department Head
- Cross-team communication goes through Department Head
- Librarians share knowledge through Platform Intelligence layer
```

---

## Memory Architecture

> **Full specification:** See `planning/MEMORY_SYSTEM.md` for complete details.

The memory system uses a **4-layer organizational architecture** with **multi-resolution content** to enable context-efficient agent operation and precedent-based reasoning.

### Four Universal Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  STRATEGIC    - Why: Goals, values, optimization targets        │
│  Update: Quarterly    Examples: Goals, Priorities, KPIs         │
├─────────────────────────────────────────────────────────────────┤
│  OPERATIONAL  - How: Rules, constraints, procedures             │
│  Update: Monthly      Examples: Policies, Thresholds, Templates │
├─────────────────────────────────────────────────────────────────┤
│  ENTITY       - What: Persistent objects tracked over time      │
│  Update: Per-event    Examples: Customers, Cases, Matters       │
├─────────────────────────────────────────────────────────────────┤
│  EVENT        - When: Things that happen, with outcomes         │
│  Update: Real-time    Examples: Calls, Decisions, Trades        │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight:** Layer structure is universal. Types within layers are pluggable per team.

### Multi-Resolution Content

Every memory node has three representations for context efficiency:

| Resolution | Tokens | Use Case |
|------------|--------|----------|
| **Micro** | ~10-20 | Listing, scanning, audit views |
| **Summary** | ~50-100 | Reasoning, context building |
| **Full** | Unlimited | Deep dive, complete content |

```python
# Example: Query 10,000 refund decisions for audit
# Without multi-resolution: 5,000,000 tokens (impossible)
# With micro resolution: 150,000 tokens (feasible)
# Filter to 200 → expand top 5: 8,000 tokens (efficient)
```

### Typed Relationships

Relationships enable graph traversal for precedent-based reasoning:

```python
class RelationType(str, Enum):
    # Cross-layer
    INVOLVES = "involves"           # event → entity
    APPLIES = "applies"             # event → operational (policy used)
    ALIGNED_WITH = "aligned_with"   # → strategic

    # Within-layer
    SUPERSEDES = "supersedes"       # policy versioning
    SIMILAR_TO = "similar_to"       # precedent matching
    CAUSED = "caused"               # event → decision (the "why")
```

### Precedent-Based Reasoning

The "why" behind decisions is captured through `CAUSED` relationships:

```
┌─────────────────────────────────────────┐
│  EVENT: interaction.call.2024-12-28    │
│  customer: jane-doe-042                │
│  topic: "defective product refund"     │
└─────────────────┬───────────────────────┘
                  │ CAUSED
                  ▼
┌─────────────────────────────────────────┐
│  EVENT: decision.refund.2024-12-28     │
│  outcome: "approved"                   │
│  reason: "Photo evidence confirmed"    │
│  factors: [evidence, within_window]    │
│  policy: operational.policy.refund.v3  │
└─────────────────────────────────────────┘
```

Agents find similar cases and understand WHY decisions were made, not just what was decided.

### Extension Types

Teams can add new node types at runtime:

```
EXPERIMENTAL → STABLE → PROMOTED
   (added)    (patterns)  (full schema)
```

Extension types with consistent usage patterns (100+ nodes, 500+ retrievals, 80%+ property consistency) are flagged for promotion to full typed schemas.

### Integration with Passport

```python
class Passport(BaseModel):
    # Existing fields...

    # Memory integration
    memory_context: list[str] = []           # Symbols loaded
    precedent_context: PrecedentContext | None = None
    emitted_symbols: list[str] = []          # Created during processing
```

### Key Differences from Standard RAG

| Aspect | Pure RAG | Organizational Memory |
|--------|----------|----------------------|
| Retrieval | Similarity only | Similarity + exact + traversal |
| Structure | Flat chunks | Typed nodes in layers |
| Relationships | None | Explicit typed edges |
| "Why" | Implicit in text | Explicit in CAUSED |
| Resolution | All or nothing | Micro/summary/full |

### Implementation

See `backend/app/models/memory.py` for:
- `MemoryNode` base class
- `MemoryLayer` enum
- `RelationType` typed relationships
- `TeamMemorySchema` for pluggable types
- `ExtensionNode` for runtime-defined types
- `TypeEvolution` for promotion tracking

---

## Double-Loop Learning: After Action Review (AAR)

After each task completion, an AAR agent reviews what happened and injects learnings into memory.

```python
class AARAgent:
    """
    After Action Review agent.

    Runs after every task completion to extract learnings and update memory.
    This is how the platform continuously improves.
    """

    def __init__(self, memory: MemoryStore, team_id: str):
        self.memory = memory
        self.team_id = team_id

    async def review(self, passport: Passport) -> AARResult:
        """
        Review a completed task and extract learnings.

        Called automatically when a passport reaches 'completed' or 'failed' status.
        """
        # Analyze what happened
        analysis = await self._analyze_execution(passport)

        # Extract learnings
        learnings = await self._extract_learnings(passport, analysis)

        # Create episode for episodic memory
        episode = Episode(
            tenant_id=passport.tenant_id,
            team_id=self.team_id,
            task_type=passport.mission.matter_type,
            mission_summary=passport.mission.objective,
            outcome=self._determine_outcome(passport),
            key_decisions=learnings.key_decisions,
            mistakes_made=learnings.mistakes,
            successful_patterns=learnings.successful_patterns,
            passport_id=passport.id,
        )

        # Store in episodic memory
        await self.memory.store_episodic(episode)

        # Update confidence calibration for involved agents
        await self._update_calibration(passport, analysis)

        # Flag anything for Janitor attention
        observations = self._generate_observations(passport, analysis)

        return AARResult(
            episode_id=episode.id,
            learnings=learnings,
            observations=observations,
            calibration_updates=analysis.calibration_updates,
        )

    async def _analyze_execution(self, passport: Passport) -> ExecutionAnalysis:
        """Analyze the execution trace from the ledger."""
        ledger = passport.ledger

        return ExecutionAnalysis(
            total_duration_ms=sum(e.duration_ms for e in ledger),
            total_tokens=sum(e.tokens_used for e in ledger),
            total_cost=sum(e.cost_usd for e in ledger),
            agent_performance={
                agent_id: self._analyze_agent_performance(
                    [e for e in ledger if e.agent_id == agent_id]
                )
                for agent_id in set(e.agent_id for e in ledger)
            },
            confidence_accuracy=self._measure_confidence_accuracy(ledger),
            bottlenecks=self._identify_bottlenecks(ledger),
            failure_points=self._identify_failures(ledger),
        )

    async def _extract_learnings(
        self,
        passport: Passport,
        analysis: ExecutionAnalysis,
    ) -> Learnings:
        """Use LLM to extract structured learnings from the execution."""
        # This is where neural reasoning extracts patterns
        prompt = f"""
        Analyze this task execution and extract learnings:

        Mission: {passport.mission.objective}
        Outcome: {passport.status}
        Execution Analysis: {analysis.model_dump_json()}

        Extract:
        1. Key decisions that affected the outcome
        2. Mistakes or inefficiencies (if any)
        3. Successful patterns worth repeating
        4. Recommendations for similar future tasks
        """
        # Call LLM for analysis
        pass

    async def _update_calibration(
        self,
        passport: Passport,
        analysis: ExecutionAnalysis,
    ) -> None:
        """Update confidence calibration based on actual outcomes."""
        for agent_id, perf in analysis.agent_performance.items():
            # Compare predicted confidence to actual accuracy
            # Update calibration data for future confidence calculations
            pass


class AARResult(BaseModel):
    """Result of After Action Review."""

    episode_id: UUID
    learnings: "Learnings"
    observations: List["Observation"]  # For Janitor
    calibration_updates: Dict[str, float]  # agent_id -> calibration adjustment


class Learnings(BaseModel):
    """Structured learnings from a task."""

    key_decisions: List[str]
    mistakes: List[str]
    successful_patterns: List[str]
    recommendations: List[str]


class ExecutionAnalysis(BaseModel):
    """Analysis of task execution."""

    total_duration_ms: int
    total_tokens: int
    total_cost: float
    agent_performance: Dict[str, "AgentPerformance"]
    confidence_accuracy: float  # How well confidence predicted outcomes
    bottlenecks: List[str]
    failure_points: List[str]
    calibration_updates: Dict[str, float] = Field(default_factory=dict)
```

### Memory Injection Flow

```
Task Completed
      │
      ▼
┌─────────────┐
│  AAR Agent  │
│             │
│  1. Analyze │
│  2. Extract │
│  3. Store   │
└──────┬──────┘
       │
       ├────────────────┬────────────────┐
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Episodic   │  │ Calibration │  │  Janitor    │
│   Memory    │  │   Updates   │  │ Observations│
│             │  │             │  │             │
│ "What       │  │ "How        │  │ "Issues to  │
│  happened"  │  │  accurate   │  │  flag"      │
│             │  │  were we?"  │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
       │
       ▼ (Later, via Platform Intelligence)
┌─────────────┐
│  Semantic   │
│   Memory    │
│             │
│ "Distilled  │
│  patterns"  │
└─────────────┘
```

---

## Judge Agent: External Validation

Based on the SCoRe paper: self-correction without external feedback fails. Judge agents provide that feedback.

```python
class JudgeAgent:
    """
    External validator that checks agent outputs.

    Separate from the agents doing the work - provides independent verification.
    """

    def __init__(
        self,
        llm_client: Any,
        rule_engine: SymbolicRuleEngine,
        verification_tools: List[Any],
    ):
        self.llm = llm_client
        self.rules = rule_engine
        self.tools = verification_tools

    async def judge(
        self,
        output: Any,
        expected_schema: type[BaseModel],
        context: SandboxedContext,
        verification_level: Literal["basic", "standard", "thorough"] = "standard",
    ) -> JudgmentResult:
        """
        Judge an agent's output.

        Args:
            output: The output to judge
            expected_schema: Pydantic model the output should conform to
            context: The context the agent was given
            verification_level: How thorough to be
        """
        checks = []

        # 1. Schema validation (always)
        schema_check = self._check_schema(output, expected_schema)
        checks.append(schema_check)

        # 2. Symbolic rule check (always)
        rule_check = self.rules.check(ProposedAction(output=output))
        checks.append(RuleCheckResult(
            check_type="symbolic_rules",
            passed=rule_check.permitted,
            details=rule_check.violations if not rule_check.permitted else None,
        ))

        # 3. Execution-based verification (if applicable)
        if verification_level in ["standard", "thorough"]:
            if self._can_execute_verify(output):
                exec_check = await self._execute_and_verify(output)
                checks.append(exec_check)

        # 4. Semantic verification via LLM (if thorough)
        if verification_level == "thorough":
            semantic_check = await self._semantic_verify(output, context)
            checks.append(semantic_check)

        # 5. Fact verification (if output contains claims)
        if self._contains_verifiable_claims(output):
            fact_check = await self._verify_facts(output)
            checks.append(fact_check)

        # Aggregate results
        all_passed = all(c.passed for c in checks)
        confidence = self._calculate_judgment_confidence(checks)

        return JudgmentResult(
            approved=all_passed,
            checks=checks,
            confidence=confidence,
            feedback=self._generate_feedback(checks) if not all_passed else None,
            revision_suggestions=self._suggest_revisions(checks) if not all_passed else None,
        )

    async def _execute_and_verify(self, output: Any) -> CheckResult:
        """
        Execute the output to verify it works.

        For code: run it.
        For documents: check formatting renders.
        For calculations: verify math.
        """
        pass

    async def _semantic_verify(
        self,
        output: Any,
        context: SandboxedContext,
    ) -> CheckResult:
        """Use LLM to check semantic correctness against context."""
        prompt = f"""
        Verify this output is correct given the context:

        Context:
        - Task: {context.task}
        - Constraints: {context.constraints}
        - Success criteria: {context.success_criteria}

        Output to verify:
        {output}

        Check:
        1. Does the output address the task?
        2. Are all constraints satisfied?
        3. Does it meet the success criteria?
        4. Are there any logical errors or inconsistencies?
        """
        pass

    async def _verify_facts(self, output: Any) -> CheckResult:
        """
        Verify factual claims in the output.

        Uses tools to check citations, dates, calculations, etc.
        Based on FacTool paper pattern.
        """
        pass


class JudgmentResult(BaseModel):
    """Result of Judge agent evaluation."""

    approved: bool
    checks: List["CheckResult"]
    confidence: ConfidenceVector
    feedback: Optional[str] = None
    revision_suggestions: Optional[List[str]] = None


class CheckResult(BaseModel):
    """Result of a single verification check."""

    check_type: str
    passed: bool
    details: Optional[Any] = None
    evidence: Optional[str] = None
```

### Integration: Actor → Judge → Approval/Revision

```
Specialist Agent
      │
      │ Produces output
      ▼
┌─────────────────────┐
│     Judge Agent     │
│                     │
│  1. Schema check    │
│  2. Rule check      │
│  3. Execute verify  │
│  4. Semantic check  │
│  5. Fact check      │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  APPROVED    REJECTED
     │           │
     ▼           ▼
  Continue   Return to
  Pipeline   Specialist
             with feedback
             (max 3 retries)
```

---

## Platform Intelligence Layer

Based on GPT 5.2's insight: split detection from proposal. Observers detect issues, Proposers suggest fixes. This separation prevents conflation of "what's wrong" with "how to fix it."

### Architecture: Observer/Proposer Split

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PLATFORM INTELLIGENCE                                 │
│                                                                              │
│   OBSERVATION (Detection)                  PROPOSAL (Suggestion)            │
│   ─────────────────────                    ──────────────────────            │
│                                                                              │
│   ┌─────────────┐                          ┌─────────────┐                  │
│   │  Observer   │──┐                    ┌──│  Proposer   │                  │
│   │  (Team A)   │  │                    │  │             │                  │
│   └─────────────┘  │                    │  └─────────────┘                  │
│                    │  ┌─────────────┐   │         │                         │
│   ┌─────────────┐  ├─▶│ Housekeeper │───┤         │                         │
│   │  Observer   │──┤  │ (Aggregate) │   │         ▼                         │
│   │  (Team B)   │  │  └─────────────┘   │  ┌─────────────┐                  │
│   └─────────────┘  │         │          │  │  Research   │                  │
│                    │         ▼          │  │   Scouts    │                  │
│   ┌─────────────┐  │  ┌─────────────┐   │  └──────┬──────┘                  │
│   │  Observer   │──┘  │  Pattern    │───┘         │                         │
│   │  (Team C)   │     │  Analysis   │             │                         │
│   └─────────────┘     └─────────────┘             │                         │
│                              │                     │                         │
│                              └──────────┬──────────┘                         │
│                                         ▼                                    │
│                              ┌─────────────────┐                             │
│                              │  Proposal Queue │                             │
│                              └────────┬────────┘                             │
│                                       ▼                                      │
│                              ┌─────────────────┐                             │
│                              │  Human Review   │                             │
│                              └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Observer (Per-Team) - Detection Only

```python
class Observer:
    """
    Per-team observer that ONLY detects issues.

    Does NOT suggest fixes - that's the Proposer's job.
    This separation ensures objective issue detection.
    """

    def __init__(self, team_id: str, tenant_id: str):
        self.team_id = team_id
        self.tenant_id = tenant_id
        self.observations: List[Observation] = []

    async def observe(self, passport: Passport) -> None:
        """Record observations from completed passport."""
        pass

    async def analyze(self) -> List[Observation]:
        """Analyze accumulated observations for patterns."""
        pass

    async def report_to_housekeeper(self, observations: List[Observation]) -> None:
        """Send flagged observations to platform-level housekeeper."""
        pass

    # Detection patterns
    async def detect_repeated_failures(self) -> List[Observation]:
        """Detect when same failure occurs multiple times."""
        pass

    async def detect_confidence_drift(self) -> List[Observation]:
        """Detect when confidence scores become miscalibrated."""
        pass

    async def detect_inefficiencies(self) -> List[Observation]:
        """Detect tool usage or workflow inefficiencies."""
        pass

    async def detect_escalation_patterns(self) -> List[Observation]:
        """Detect patterns in what gets escalated to humans."""
        pass


class Observation(BaseModel):
    """Something the Janitor noticed."""

    id: UUID = Field(default_factory=uuid4)
    team_id: str
    tenant_id: str
    observation_type: Literal[
        "repeated_failure",
        "confidence_drift",
        "new_pattern",
        "tool_inefficiency",
        "escalation_pattern",
    ]
    description: str
    evidence: List[str]  # Passport IDs or ledger entries
    suggested_action: Optional[str] = None
    priority: Literal["low", "medium", "high"] = "medium"
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Housekeeper (Platform-Level)

```python
class Housekeeper:
    """
    Platform-level aggregator of Janitor reports.

    Coordinates with Research Scouts to propose improvements.
    All proposals require human approval before implementation.
    """

    def __init__(self):
        self.observations: Dict[str, List[Observation]] = {}  # tenant_id -> observations
        self.proposals: List[Proposal] = []

    async def receive_observation(self, observation: Observation) -> None:
        """Receive observation from a Janitor."""
        pass

    async def analyze_cross_team(self) -> List[Proposal]:
        """Find patterns across teams that suggest improvements."""
        pass

    async def consult_research_scouts(self, topic: str) -> List[ResearchFinding]:
        """Ask Research Scouts for relevant external knowledge."""
        pass

    async def create_proposal(
        self,
        observation: Observation,
        research: List[ResearchFinding],
    ) -> Proposal:
        """Create human-reviewable improvement proposal."""
        pass


class Proposal(BaseModel):
    """Improvement proposal requiring human approval."""

    id: UUID = Field(default_factory=uuid4)

    # What we observed
    observations: List[UUID]  # Observation IDs

    # What we propose
    title: str
    description: str
    proposed_change: str
    expected_benefit: str
    risk_assessment: str

    # Research backing
    research_findings: List[UUID]  # ResearchFinding IDs

    # Approval workflow
    status: Literal["draft", "pending_review", "approved", "rejected", "implemented"] = "draft"
    reviewer: Optional[str] = None
    review_notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
```

### Research Scouts

```python
class ResearchScout:
    """
    Continuously monitors external sources for relevant knowledge.

    Sources:
    - Academic papers (arxiv, semantic scholar)
    - Technical blogs
    - Framework releases
    - Industry reports
    """

    def __init__(self, focus_areas: List[str]):
        self.focus_areas = focus_areas
        self.findings: List[ResearchFinding] = []

    async def scan(self) -> List[ResearchFinding]:
        """Scan sources for relevant new information."""
        pass

    async def summarize(self, source_url: str) -> ResearchFinding:
        """Create structured summary of a source."""
        pass

    async def assess_relevance(
        self,
        finding: ResearchFinding,
        observation: Observation,
    ) -> float:
        """Score how relevant a finding is to an observation."""
        pass


class ResearchFinding(BaseModel):
    """Structured summary of external research."""

    id: UUID = Field(default_factory=uuid4)

    # Source
    source_url: str
    source_type: Literal["paper", "blog", "release", "report"]
    source_date: datetime

    # Content
    title: str
    summary: str
    key_insights: List[str]

    # Relevance
    focus_areas: List[str]
    relevance_scores: Dict[str, float]  # focus_area -> score

    # For retrieval
    embedding: Optional[List[float]] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Proposer - Suggestion Only

```python
class Proposer:
    """
    Creates improvement proposals based on observations and research.

    Does NOT detect issues - that's the Observer's job.
    Consults Research Scouts to back proposals with evidence.
    """

    def __init__(
        self,
        llm_client: Any,
        research_scouts: List[ResearchScout],
    ):
        self.llm = llm_client
        self.scouts = research_scouts

    async def create_proposal(
        self,
        observations: List[Observation],
        pattern_analysis: "PatternAnalysis",
    ) -> Proposal:
        """
        Create a proposal to address observed issues.

        Steps:
        1. Understand the pattern/problem from observations
        2. Consult Research Scouts for relevant solutions
        3. Draft proposal with evidence
        4. Assess risks and benefits
        5. Submit for human review
        """
        # Research phase
        research = await self._gather_research(observations)

        # Draft proposal
        proposal = await self._draft_proposal(
            observations=observations,
            research=research,
            pattern_analysis=pattern_analysis,
        )

        # Risk assessment
        proposal.risk_assessment = await self._assess_risks(proposal)

        return proposal

    async def _gather_research(
        self,
        observations: List[Observation],
    ) -> List[ResearchFinding]:
        """Query Research Scouts for relevant external knowledge."""
        findings = []
        for obs in observations:
            topic = self._extract_topic(obs)
            for scout in self.scouts:
                relevant = await scout.search(topic)
                findings.extend(relevant)
        return self._deduplicate_and_rank(findings)

    async def _draft_proposal(
        self,
        observations: List[Observation],
        research: List[ResearchFinding],
        pattern_analysis: "PatternAnalysis",
    ) -> Proposal:
        """Use LLM to draft a proposal based on observations and research."""
        pass

    async def _assess_risks(self, proposal: Proposal) -> str:
        """Assess potential risks of implementing the proposal."""
        pass
```

---

## MCP Tool Compatibility

All agent tools follow the Model Context Protocol (MCP) for interoperability and validation.

```python
class MCPToolSchema(BaseModel):
    """Tool definition following MCP specification."""

    name: str
    description: str
    input_schema: Dict[str, Any]  # JSON Schema
    output_schema: Optional[Dict[str, Any]] = None

    # Quandura extensions
    requires_sandbox: bool = False
    max_execution_time_ms: int = 30000
    allowed_autonomy_levels: List[int] = [1, 2, 3, 4, 5]
    audit_level: Literal["none", "summary", "full"] = "summary"


class MCPToolRegistry:
    """
    Central registry of all available tools.

    Validates tool calls before execution.
    """

    def __init__(self):
        self.tools: Dict[str, MCPToolSchema] = {}

    def register(self, tool: MCPToolSchema) -> None:
        """Register a tool in the registry."""
        self.tools[tool.name] = tool

    def validate_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        caller_autonomy_level: int,
    ) -> "ValidationResult":
        """
        Validate a tool call before execution.

        Checks:
        1. Tool exists
        2. Arguments match schema
        3. Caller has sufficient autonomy level
        """
        if tool_name not in self.tools:
            return ValidationResult(
                valid=False,
                error=f"Unknown tool: {tool_name}",
            )

        tool = self.tools[tool_name]

        # Check autonomy level
        if caller_autonomy_level not in tool.allowed_autonomy_levels:
            return ValidationResult(
                valid=False,
                error=f"Insufficient autonomy level for tool {tool_name}",
            )

        # Validate arguments against schema
        try:
            # Use jsonschema to validate
            import jsonschema
            jsonschema.validate(arguments, tool.input_schema)
        except jsonschema.ValidationError as e:
            return ValidationResult(
                valid=False,
                error=f"Invalid arguments: {e.message}",
            )

        return ValidationResult(valid=True)

    def get_tools_for_agent(
        self,
        agent_type: str,
        autonomy_level: int,
    ) -> List[MCPToolSchema]:
        """Get tools available to an agent based on type and autonomy."""
        # Filter based on agent type and autonomy level
        pass


class ValidationResult(BaseModel):
    """Result of tool call validation."""

    valid: bool
    error: Optional[str] = None
```

---

## Security Hardening

### Prompt Injection Defense

```python
class PromptGuard:
    """
    Defends against prompt injection attacks.

    Applied to all external inputs before they reach agents.
    """

    def __init__(self):
        self.patterns: List[str] = self._load_injection_patterns()

    def sanitize(self, input_text: str) -> "SanitizedInput":
        """
        Sanitize input text for prompt injection.

        Returns sanitized text and any detected threats.
        """
        threats = []

        # Check for known injection patterns
        for pattern in self.patterns:
            if self._matches_pattern(input_text, pattern):
                threats.append(ThreatDetection(
                    type="pattern_match",
                    pattern=pattern,
                    severity="high",
                ))

        # Check for instruction-like content
        if self._contains_instructions(input_text):
            threats.append(ThreatDetection(
                type="instruction_injection",
                severity="medium",
            ))

        # Check for delimiter manipulation
        if self._has_delimiter_manipulation(input_text):
            threats.append(ThreatDetection(
                type="delimiter_manipulation",
                severity="high",
            ))

        # Sanitize if threats detected
        if threats:
            sanitized = self._sanitize_text(input_text)
            return SanitizedInput(
                original=input_text,
                sanitized=sanitized,
                threats=threats,
                was_modified=True,
            )

        return SanitizedInput(
            original=input_text,
            sanitized=input_text,
            threats=[],
            was_modified=False,
        )

    def _contains_instructions(self, text: str) -> bool:
        """Detect if text contains instruction-like patterns."""
        instruction_markers = [
            "ignore previous",
            "disregard above",
            "new instructions",
            "system prompt",
            "you are now",
            "act as",
        ]
        text_lower = text.lower()
        return any(marker in text_lower for marker in instruction_markers)


class SanitizedInput(BaseModel):
    """Result of input sanitization."""

    original: str
    sanitized: str
    threats: List["ThreatDetection"]
    was_modified: bool


class ThreatDetection(BaseModel):
    """Detected security threat."""

    type: str
    pattern: Optional[str] = None
    severity: Literal["low", "medium", "high", "critical"]
```

### Input/Output Boundaries

```
External Input                              Agent Processing
─────────────────                           ────────────────

User Input ────┐
               │
Email Content ─┼──▶ PromptGuard ──▶ SandboxedContext ──▶ Agent
               │     (Sanitize)      (Minimal context)
Phone Speech ──┘

                                                    │
                                                    ▼

                                            Agent Output
                                                    │
                                                    ▼

                                            SymbolicRuleEngine ──▶ JudgeAgent
                                            (Hard rules)          (Verification)
                                                    │
                                                    ▼

                                            OutputSanitizer ──▶ External
                                            (PII redaction)     Delivery
```

### Audit Security Events

```python
class SecurityAuditLog:
    """Log all security-relevant events."""

    async def log_threat(
        self,
        threat: ThreatDetection,
        input_source: str,
        action_taken: str,
    ) -> None:
        """Log a detected threat."""
        pass

    async def log_rule_violation(
        self,
        violation: "RuleViolation",
        agent_id: str,
        action_blocked: str,
    ) -> None:
        """Log a symbolic rule violation."""
        pass

    async def log_access(
        self,
        resource: str,
        accessor: str,
        action: str,
        permitted: bool,
    ) -> None:
        """Log access attempts to sensitive resources."""
        pass
```

---

## De-Scaffolding System

Agents start with tight constraints and earn autonomy through demonstrated reliability.

```python
class AutonomyLevel(BaseModel):
    """Current autonomy level for an agent or team."""

    level: int = Field(ge=1, le=5, default=1)

    # What this level allows
    can_skip_review: bool = False
    can_auto_approve_low_risk: bool = False
    can_modify_own_prompts: bool = False
    can_create_sub_agents: bool = False
    can_access_external_apis: bool = False

    # Thresholds for this level
    min_completed_tasks: int = 0
    min_accuracy_rate: float = 0.0
    max_escalation_rate: float = 1.0
    min_confidence_calibration: float = 0.0


class DeScaffoldingEngine:
    """
    Manages autonomy progression based on demonstrated performance.

    Multi-factor triggers prevent gaming single metrics.
    """

    LEVELS = {
        1: AutonomyLevel(
            level=1,
            min_completed_tasks=0,
            min_accuracy_rate=0.0,
            max_escalation_rate=1.0,
        ),
        2: AutonomyLevel(
            level=2,
            can_skip_review=True,  # For low-complexity tasks
            min_completed_tasks=50,
            min_accuracy_rate=0.85,
            max_escalation_rate=0.3,
            min_confidence_calibration=0.7,
        ),
        3: AutonomyLevel(
            level=3,
            can_skip_review=True,
            can_auto_approve_low_risk=True,
            min_completed_tasks=200,
            min_accuracy_rate=0.92,
            max_escalation_rate=0.15,
            min_confidence_calibration=0.8,
        ),
        4: AutonomyLevel(
            level=4,
            can_skip_review=True,
            can_auto_approve_low_risk=True,
            can_modify_own_prompts=True,  # With human review
            min_completed_tasks=500,
            min_accuracy_rate=0.95,
            max_escalation_rate=0.1,
            min_confidence_calibration=0.85,
        ),
        5: AutonomyLevel(
            level=5,
            can_skip_review=True,
            can_auto_approve_low_risk=True,
            can_modify_own_prompts=True,
            can_create_sub_agents=True,  # With human review
            can_access_external_apis=True,
            min_completed_tasks=1000,
            min_accuracy_rate=0.98,
            max_escalation_rate=0.05,
            min_confidence_calibration=0.9,
        ),
    }

    def evaluate(self, agent_id: str, metrics: "AgentMetrics") -> int:
        """Evaluate which autonomy level an agent qualifies for."""
        for level in range(5, 0, -1):
            requirements = self.LEVELS[level]
            if self._meets_requirements(metrics, requirements):
                return level
        return 1

    def _meets_requirements(
        self,
        metrics: "AgentMetrics",
        requirements: AutonomyLevel,
    ) -> bool:
        """Check if metrics meet all requirements."""
        return (
            metrics.completed_tasks >= requirements.min_completed_tasks
            and metrics.accuracy_rate >= requirements.min_accuracy_rate
            and metrics.escalation_rate <= requirements.max_escalation_rate
            and metrics.confidence_calibration >= requirements.min_confidence_calibration
        )
```

---

## Multi-Tenancy Architecture

### Database Layer: PostgreSQL with RLS

```sql
-- Enable RLS on all tables
ALTER TABLE passports ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policy
CREATE POLICY tenant_isolation ON passports
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Connection setup (done by application)
-- SET app.tenant_id = 'tenant-uuid-here';
```

### Application Layer: Tenant Context

```python
from contextvars import ContextVar
from contextlib import asynccontextmanager

tenant_context: ContextVar[str] = ContextVar('tenant_id')


@asynccontextmanager
async def tenant_scope(tenant_id: str):
    """Set tenant context for the current async scope."""
    token = tenant_context.set(tenant_id)
    try:
        yield
    finally:
        tenant_context.reset(token)


def get_current_tenant() -> str:
    """Get current tenant ID or raise."""
    try:
        return tenant_context.get()
    except LookupError:
        raise RuntimeError("No tenant context set")
```

### Compute Layer: Kubernetes Namespaces

```yaml
# Each tenant gets isolated namespace
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-{tenant_id}
  labels:
    tenant: {tenant_id}
---
# Network policy: deny all by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: tenant-{tenant_id}
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### Sandbox Layer: gVisor for Code Execution

```python
class SandboxConfig(BaseModel):
    """Configuration for sandboxed code execution."""

    runtime: Literal["gvisor", "firecracker", "e2b"] = "gvisor"
    memory_limit_mb: int = 512
    cpu_limit: float = 0.5
    timeout_seconds: int = 30
    network_access: bool = False
    filesystem_access: Literal["none", "readonly", "workspace"] = "workspace"
```

---

## Voice Interface Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              VOICE PIPELINE                                   │
│                                                                               │
│   Caller                                                                      │
│     │                                                                         │
│     ▼                                                                         │
│   ┌─────────┐    ┌───────────────┐    ┌─────────────┐    ┌──────────────┐   │
│   │ Twilio  │───▶│  WebSocket    │───▶│  Deepgram   │───▶│    Agent     │   │
│   │ (PSTN)  │    │   Handler     │    │  STT        │    │ Orchestrator │   │
│   └─────────┘    └───────────────┘    │  (streaming)│    └──────────────┘   │
│                                        └─────────────┘           │            │
│                                                                  ▼            │
│                                                           ┌──────────────┐   │
│                                                           │   Claude     │   │
│                                                           │  (streaming) │   │
│                                                           └──────────────┘   │
│                                                                  │            │
│   ┌─────────┐    ┌───────────────┐    ┌─────────────┐           ▼            │
│   │  Audio  │◀───│   Audio       │◀───│ ElevenLabs  │◀──────────┘            │
│   │  Back   │    │   Stream      │    │    TTS      │                        │
│   └─────────┘    └───────────────┘    │  (streaming)│                        │
│                                        └─────────────┘                        │
└──────────────────────────────────────────────────────────────────────────────┘

Latency Budget: <1000ms total
- Network (in):   50-150ms
- STT:           300-500ms
- LLM:           200-500ms
- TTS:           200-400ms
- Network (out):  50-150ms

Cost: $0.06-0.12/minute
```

---

## Technology Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Backend** | Python 3.12+ | LangGraph ecosystem, type hints |
| **Framework** | FastAPI | Async, OpenAPI, production-ready |
| **Agent Orchestration** | LangGraph | Checkpointing, state management |
| **Primary LLM** | Claude 3.5 Sonnet | Reasoning, streaming, tool use |
| **Database** | PostgreSQL | RLS, JSONB, mature |
| **Cache** | Redis | Rate limiting, working memory |
| **Vector DB** | ChromaDB → Pinecone | Start simple, scale later |
| **Knowledge Graph** | Neo4j | Semantic memory, relationships |
| **Task Queue** | Celery + Redis | Background jobs, scheduling |
| **Containers** | Kubernetes | Industry standard |
| **Sandbox** | gVisor (prod) / E2B (dev) | Security + convenience |
| **Telephony** | Twilio | FedRAMP, reliable |
| **STT** | Deepgram Nova-2 | Lowest latency |
| **TTS** | ElevenLabs Turbo | Natural, low latency |
| **Frontend** | React + TypeScript | Type safety, ecosystem |
| **UI Framework** | Tailwind + shadcn/ui | Professional, accessible |
| **Auth** | Keycloak | OIDC, multi-tenant |
| **Secrets** | HashiCorp Vault | Per-tenant encryption |
| **Observability** | OpenTelemetry + Datadog | Distributed tracing |

---

## Compliance Requirements

### Baseline (Required)

| Certification | Cost (Year 1) | Timeline |
|--------------|---------------|----------|
| SOC 2 Type 2 | $40K-$80K | 6-12 months |
| Cyber Insurance ($2M+) | $15K-$50K | Immediate |
| E&O Insurance ($2M+) | $10K-$50K | Immediate |

### Conditional

| Certification | Trigger | Cost |
|--------------|---------|------|
| CJIS | Law enforcement data | $50K-$200K |
| HIPAA | Employee medical records | $20K-$50K |
| StateRAMP | Multi-state deployment | $100K-$300K |

### Technical Requirements

- US-based data centers
- AES-256 encryption at rest
- TLS 1.3 in transit
- Complete audit logging
- PII redaction in transcripts
- Role-based access control

---

## UI Design Direction

### Aesthetic: Professional Hybrid

- Clean, modern interface with subtle warmth
- Dark mode default with light mode option
- Accessible (WCAG 2.1 AA minimum)
- Government-appropriate but not sterile

### Patterns to Port from A-Teams

1. **Agent chat interface** - Conversation threading, message streaming
2. **Team visualization** - Agent relationship diagrams
3. **Passport viewer** - State inspection for debugging
4. **Task list** - Queue visualization

### Patterns to NOT Port

1. Retro/pixel aesthetic
2. Playful animations
3. Casual language in UI copy
4. Gaming metaphors

### New Patterns Needed

1. **Tenant management dashboard**
2. **Team builder wizard**
3. **Compliance status indicators**
4. **Cost tracking dashboards**
5. **Human escalation queue**
6. **Proposal review interface** (for Platform Intelligence)
7. **Voice call monitoring**

---

## Implementation Roadmap

### Phase 1: Core Foundation + Legal Research Test (8-10 weeks)

**Goal:** Working team system validated with Legal Research test harness

- [ ] Project scaffolding (FastAPI, PostgreSQL, Redis)
- [ ] Passport schema and persistence
- [ ] LangGraph checkpointing integration
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

## Project Structure

```
quandura/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   ├── core/             # Config, security, deps
│   │   ├── models/           # Pydantic schemas
│   │   ├── agents/           # Agent implementations
│   │   │   ├── base.py
│   │   │   ├── orchestrator.py
│   │   │   ├── librarian.py
│   │   │   └── teams/
│   │   │       └── legal_research/
│   │   ├── memory/           # Memory stores
│   │   ├── platform/         # Janitor, Housekeeper, Scouts
│   │   ├── voice/            # Telephony integration
│   │   ├── tools/            # Agent tools
│   │   └── db/               # Database models
│   ├── tests/
│   ├── alembic/              # Migrations
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── api/
│   ├── public/
│   └── package.json
├── infrastructure/
│   ├── kubernetes/
│   ├── terraform/
│   └── docker/
├── docs/
└── README.md
```

---

## Handoff Checklist

For the new Claude instance taking over implementation:

1. **Read this document thoroughly** - It contains all architectural decisions
2. **Read the team specification** - `planning/teams/LAW_OFFICE_LEGAL_RESEARCH.md`
3. **Read the research** - `research/*.md` for compliance, architecture, voice details
4. **Read the enterprise plan** - `planning/ENTERPRISE_PLAN.md` for business context
5. **Start with Phase 1** - Foundation must be solid before building teams
6. **Validate incrementally** - Each phase has validation criteria
7. **Maintain this document** - Update as decisions evolve

---

## Key Research Papers Referenced

| Paper | Concept Used |
|-------|--------------|
| SCoRe (Self-Correction via RL) | External validation required - Judge agents |
| Magentic-One | Dual-loop orchestration (outer planning, inner execution) |
| HippoRAG | Knowledge graphs + PPR for associative memory |
| Mem0 | Memory with decay and consolidation |
| FacTool | Fact verification via tool calls |
| DSPy | Prompt optimization (future consideration) |
| AutoAgents | Dynamic agent spawning from templates |

---

*Version: 2.2*
*Created: 2025-01-05*
*Updated: 2025-01-06*
*Status: Complete architecture specification for implementation handoff*

## Changes in v2.2

- Updated Executive Summary with Development Strategy (Legal Research = test harness, Safety Team = first deployment)
- Added near-term focus: Safety Team + Inspection App for Martinez Act opportunity
- Rewrote Implementation Roadmap to 6 phases prioritizing Safety Team
- Phase 1 now validates team system with Legal Research test harness
- Phase 2 focuses on Safety Team + Inspection App for real-world deployment
- Added Phase 3: Consulting Firm Launch (revenue generation)
- Deferred Platform Intelligence to Phase 5 (when needed)
- Added Phase 6: TPA Market Entry (Year 2+)

## Changes in v2.1

- Replaced 3-tier memory with 4-layer organizational memory architecture
- Added multi-resolution content (micro, summary, full) for context efficiency
- Added typed relationships for graph traversal and precedent reasoning
- Added extension types with evolution/promotion lifecycle
- Added `planning/MEMORY_SYSTEM.md` detailed specification
- Added `backend/app/models/memory.py` implementation models
- Memory now supports team-pluggable type schemas

## Changes in v2.0

- Added Design Principles 7-10 (context sandboxing, hybrid architecture, AAR, execution verification)
- Added Data Zone Architecture (sensitive vs platform zones)
- Added Context Sandboxing pattern with full code examples
- Added Dual-Loop Orchestration (Magentic-One pattern)
- Added Hybrid Symbolic + Neural architecture with rule engine
- Added After Action Review (AAR) agent for double-loop learning
- Added Judge Agent for external validation (SCoRe paper)
- Updated Platform Intelligence with Observer/Proposer split (GPT 5.2)
- Added MCP Tool Compatibility for tool schema validation
- Added Security Hardening (prompt injection defense, input/output boundaries)
- Added Research Papers reference table
