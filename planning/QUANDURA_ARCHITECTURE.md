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
13. **Fractal architecture** - Same communication pattern at every level (department, team, agent)
14. **Humans as agents** - Humans participate in the system via the same message/subscription model

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

### Agent Lifecycle Layers

Agents have three independent lifecycle layers (adapted from Gas Town patterns):

| Layer | Component | Lifecycle | What It Holds |
|-------|-----------|-----------|---------------|
| **Session** | LLM context window | Ephemeral | Current reasoning, conversation |
| **Sandbox** | Mission workspace | Persistent (per mission) | Work state, artifacts, progress |
| **Identity** | Agent registration | Persistent | Role, subscriptions, history |

```python
class AgentLifecycle(BaseModel):
    """Three-layer agent lifecycle management."""

    # Identity Layer (persistent)
    agent_id: str
    role_definition: str           # Reference to role template
    subscriptions: list[str]       # UNI-Q patterns this agent handles
    historical_accuracy: float     # Calibration data
    created_at: datetime

    # Sandbox Layer (per-mission)
    current_mission_id: str | None
    sandbox_path: str | None       # Workspace location
    sandbox_created_at: datetime | None
    work_state: dict               # Checkpointed state

    # Session Layer (ephemeral)
    session_id: str | None
    session_started_at: datetime | None
    context_tokens_used: int = 0


class SessionCycleReason(str, Enum):
    """Why a session ended."""

    HANDOFF = "handoff"             # Voluntary handoff between steps
    CONTEXT_LIMIT = "context_limit" # Hit token limit
    TIMEOUT = "timeout"             # Inactivity timeout
    CRASH = "crash"                 # Error/failure
    COMPLETION = "completion"       # Work done


async def cycle_session(agent: AgentLifecycle, reason: SessionCycleReason) -> None:
    """
    Cycle the session layer while preserving sandbox and identity.

    Session cycling is NORMAL OPERATION - the agent continues working
    with a fresh context while sandbox state persists.
    """
    # Checkpoint current state to sandbox
    await checkpoint_to_sandbox(agent)

    # End session
    agent.session_id = None
    agent.session_started_at = None
    agent.context_tokens_used = 0

    # If not completion, spawn new session
    if reason != SessionCycleReason.COMPLETION:
        await spawn_new_session(agent)
```

**Key insight:** Session cycling (LLM restarts) is normal. The sandbox preserves work state. This allows long-running tasks to span multiple LLM context windows.

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

## Team Template Schema

Teams are defined declaratively via YAML templates. This allows teams to be **configured** rather than coded.

```yaml
# team_templates/legal_research.yaml
name: "Legal Research Team"
version: "1.0"
description: "Research legal questions and provide citations"

# Role definitions (externalized from code)
roles:
  orchestrator:
    type: orchestrator
    description: "Coordinates team work, handles escalations"
    subscriptions:
      - "Ⓠ{team}·*"           # All queries to this team
      - "Ⓔ{team}·*"           # All escalations
    capabilities:
      - task_decomposition
      - work_assignment
      - progress_tracking

  researcher:
    type: specialist
    description: "Searches databases, gathers relevant cases"
    subscriptions:
      - "Ⓣresearcher·*"       # Tasks assigned to this role
    capabilities:
      - legal_database_search
      - case_citation
      - statute_lookup
    tools:
      - westlaw_search
      - lexis_search
      - court_records

  reviewer:
    type: specialist
    description: "Verifies citations, checks quality"
    subscriptions:
      - "Ⓥresearcher·*·pending-review"
    capabilities:
      - citation_verification
      - quality_check
      - cross_reference

  drafter:
    type: specialist
    description: "Generates opinion documents"
    subscriptions:
      - "Ⓥreviewer·*·approved"
    capabilities:
      - document_generation
      - memo_formatting
      - citation_integration
    templates:
      - legal_opinion
      - research_memo
      - case_brief

  librarian:
    type: librarian
    description: "Team knowledge persistence and retrieval"
    subscriptions:
      - "Ⓠlibrarian·*"
    memory_layers:
      - precedents
      - research_history
      - citation_patterns

# Workflow definitions (molecule-style step tracking)
workflows:
  legal_opinion:
    description: "Full legal opinion workflow"
    steps:
      - id: intake
        role: orchestrator
        description: "Parse request, identify research questions"
        outputs: [research_questions, scope_definition]

      - id: research
        role: researcher
        needs: [intake]
        description: "Search databases, gather relevant cases"
        outputs: [case_findings, statute_references]

      - id: review
        role: reviewer
        needs: [research]
        description: "Verify citations, check quality"
        outputs: [verified_citations, quality_score]
        gate:
          condition: "quality_score >= 0.8"
          on_fail: "return_to_research"

      - id: draft
        role: drafter
        needs: [review]
        description: "Generate opinion document"
        outputs: [draft_document]
        template: legal_opinion

      - id: signoff
        type: human
        role: "Ⓗattorney"
        needs: [draft]
        description: "Attorney approval"
        actions: [approve, revise, reject]

# Escalation routing
escalation:
  decision:
    route: orchestrator
    description: "Multiple valid paths, need choice"
  help:
    route: orchestrator
    description: "Need guidance or expertise"
  blocked:
    route: department_head
    description: "Waiting on external dependency"
  failed:
    route: orchestrator
    description: "Unexpected error, can't proceed"
  emergency:
    route: human
    description: "Security or data integrity issue"
  gate_timeout:
    route: orchestrator
    description: "Workflow gate didn't resolve"
  lifecycle:
    route: orchestrator
    description: "Agent stuck or needs intervention"

# Health monitoring thresholds
health:
  heartbeat_interval_seconds: 60
  stale_threshold_seconds: 300      # 5 min - nudge if work pending
  intervention_threshold_seconds: 900  # 15 min - intervene

# De-scaffolding progression
autonomy:
  initial_level: 1
  progression:
    level_2:
      requires:
        completed_tasks: 50
        accuracy_rate: 0.85
      grants:
        can_skip_low_risk_review: true
    level_3:
      requires:
        completed_tasks: 200
        accuracy_rate: 0.90
      grants:
        can_auto_approve_routine: true
```

### Team Instantiation

```python
class TeamTemplate(BaseModel):
    """Parsed team template."""

    name: str
    version: str
    description: str
    roles: dict[str, RoleDefinition]
    workflows: dict[str, WorkflowDefinition]
    escalation: dict[str, EscalationRoute]
    health: HealthConfig
    autonomy: AutonomyConfig


class TeamFactory:
    """Create team instances from templates."""

    async def create_team(
        self,
        template_name: str,
        tenant_id: str,
        team_id: str,
        config_overrides: dict | None = None,
    ) -> "Team":
        """
        Instantiate a team from a template.

        Args:
            template_name: Name of template (e.g., "legal_research")
            tenant_id: Tenant this team belongs to
            team_id: Unique ID for this team instance
            config_overrides: Optional overrides for template values
        """
        template = await self.load_template(template_name)

        # Apply overrides
        if config_overrides:
            template = self.apply_overrides(template, config_overrides)

        # Create orchestrator
        orchestrator = await self.create_agent(
            template.roles["orchestrator"],
            team_id=team_id,
            tenant_id=tenant_id,
        )

        # Create specialists
        specialists = {}
        for role_name, role_def in template.roles.items():
            if role_def.type == "specialist":
                specialists[role_name] = await self.create_agent(
                    role_def,
                    team_id=team_id,
                    tenant_id=tenant_id,
                )

        # Create librarian
        librarian = await self.create_librarian(
            template.roles["librarian"],
            team_id=team_id,
            tenant_id=tenant_id,
        )

        return Team(
            team_id=team_id,
            tenant_id=tenant_id,
            template=template,
            orchestrator=orchestrator,
            specialists=specialists,
            librarian=librarian,
        )
```

---

## UNI-Q: Agent Communication Grammar

> **Full specification:** See `planning/research/UNIQ_SPEC.md` for complete grammar and implementation details.
> **Examples:** See `planning/research/UNIQ_EXAMPLES.md` for practical scenarios.

UNI-Q is a token-efficient grammar for agent-to-agent communication. It provides consistent message formatting across all levels of the system (fractal architecture).

### Core Symbols

| Symbol | Type | Description |
|--------|------|-------------|
| `Ⓐ` | Agent | Agent identifier (e.g., `Ⓐlegal-orch`) |
| `Ⓣ` | Task | Task assignment |
| `Ⓥ` | Verdict/Value | Decision or result |
| `Ⓔ` | Entity | Domain object reference |
| `Ⓞ` | Operational | Policy or rule reference |
| `Ⓢ` | Strategic | Goal or priority reference |
| `Ⓡ` | Request | Cross-team consultation request |
| `Ⓗ` | Human | Human agent (escalation target) |
| `Ⓖ` | Gateway | External system interface |
| `Ⓜ` | Metric | Analytics/business event |

### Status Modifiers

| Modifier | Meaning |
|----------|---------|
| `✓` | Completed/approved |
| `✗` | Failed/rejected |
| `◐` | In progress |
| `⚠` | Warning/attention needed |
| `⊘` | Blocked |

### Message Examples

```
# Task assignment
Ⓐohs-orch → Ⓐparser: Ⓣparse·inspection-2024-0089⟨artifacts:ref-001⟩

# Task completion
Ⓐparser → Ⓐohs-orch: Ⓥparsed-data·inspection-2024-0089✓⟨findings:12⟩

# Cross-team request
Ⓐohs-orch → Ⓐdept-orch: Ⓡcitation-request⟨to:legal·findings:5⟩

# Human escalation
Ⓐohs-orch → Ⓗsignoff-authority: Ⓔescalation·signoff⟨mission:X·artifact:report-ref⟩

# External transmission
Ⓐfinance-orch → Ⓖgateway: Ⓣtransmit⟨to:client·artifact:invoice-ref⟩

# Metric event
Ⓜmetric·revenue⟨team:ohs·amount:4050·mission:inspection-2024-0089⟩
```

### Standard Message Types

Common message patterns for team coordination:

| Message Type | Pattern | Use Case |
|--------------|---------|----------|
| **Task Assignment** | `Ⓣ{role}·{task}⟨mission:{id}⟩` | Assign work to specialist |
| **Task Complete** | `Ⓥ{agent}·{task}·done✓` | Signal task completion |
| **Query** | `Ⓠ{target}·{topic}?` | Request information |
| **Response** | `Ⓐ{agent}·{topic}·response` | Provide requested info |
| **Escalation** | `Ⓔ{agent}·{category}·{severity}` | Escalate issue |
| **Human Action** | `Ⓗ{role}·{action}` | Human involvement needed |
| **External** | `Ⓖ{direction}·{source/dest}` | Gateway message |
| **Metric** | `Ⓜmetric·{type}⟨data⟩` | Analytics event |
| **Handoff** | `↻{agent}·context-transfer` | Session continuity |
| **Progress** | `Ⓥ{agent}·progress⟨step:{n}·total:{m}⟩` | Workflow progress |

**Workflow Messages:**

```
# Step completion with auto-advance
Ⓥresearcher·step-2·done✓⟨workflow:legal_opinion·next:review⟩

# Gate check
Ⓥreviewer·gate-check⟨condition:quality_score·value:0.85·passed:true⟩

# Workflow complete
Ⓥorchestrator·workflow·complete✓⟨workflow:legal_opinion·mission:m-123⟩
```

**Lifecycle Messages:**

```
# Agent health
Ⓥ{agent}·heartbeat⟨ts:1704567890·status:active⟩

# Session cycle
↻{agent}·session-cycle⟨reason:context_limit·state:checkpointed⟩

# Stuck detection
Ⓔwitness·lifecycle·medium⟨agent:{id}·idle_seconds:600⟩
```

### Multi-Resolution Content

Every memory node has three representations:

| Resolution | Tokens | Use Case |
|------------|--------|----------|
| **Micro** | ~10-20 | Routing, monitoring, dashboards |
| **Summary** | ~50-100 | Reasoning, decision context |
| **Full** | Unlimited | Audit, deep analysis |

**Query intent determines resolution:**
- `ROUTE`, `MONITOR` → micro
- `REASON`, `DECIDE` → summary
- `DRAFT`, `AUDIT` → full

---

## Fractal Architecture

The same UNI-Q pub/sub pattern applies at every level of the hierarchy:

```
┌─────────────────────────────────────────────────────────────────────┐
│  DEPARTMENT LEVEL                                                    │
│  ┌─────────────────┐                                                │
│  │ Dept Orchestrator│ ← Routes between teams via subscriptions      │
│  └────────┬────────┘                                                │
│           │                                                          │
│  ┌────────┼────────┬────────────┬────────────┐                      │
│  ▼        ▼        ▼            ▼            ▼                      │
│  OHS    Legal    Finance    C-Suite      Gateway                    │
│  Team    Team     Team       Team        (External)                 │
└─────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  TEAM LEVEL (e.g., OHS Team)                                        │
│  ┌─────────────────┐                                                │
│  │ Team Orchestrator│ ← Routes between agents via subscriptions     │
│  └────────┬────────┘                                                │
│           │                                                          │
│  ┌────────┼────────┬────────────┬────────────┐                      │
│  ▼        ▼        ▼            ▼            ▼                      │
│ Parser  Analyst  Drafter    Reviewer    Librarian                   │
│ Agent   Agent    Agent      Agent                                   │
└─────────────────────────────────────────────────────────────────────┘
```

**Key insight:** Hub-and-spoke is maintained at each level. Orchestrators route based on subscriptions, but agents don't talk directly to each other.

### Subscription Model

Teams and agents subscribe to message patterns they care about:

```python
# Department-level subscriptions
department_subscriptions = {
    "ohs_team": [
        "Ⓣinspection·*",           # All inspection tasks
        "Ⓥcitations·*✓",           # Citation responses from legal
    ],
    "legal_team": [
        "Ⓡcitation-request·*",     # Citation requests from any team
        "Ⓣcontract-review·*",      # Contract review tasks
    ],
    "finance_team": [
        "Ⓣbilling-request·*",      # Billing requests from any team
        "Ⓥpayment-received·*",     # Payment notifications
    ],
}

# Team-level subscriptions (within OHS team)
ohs_agent_subscriptions = {
    "parser_agent": ["Ⓣparse·*"],
    "analyst_agent": ["Ⓥparsed-data·*✓"],
    "drafter_agent": ["Ⓥfindings·*✓", "Ⓥcitations·*✓"],
    "reviewer_agent": ["Ⓥdraft·*✓"],
}
```

---

## Mission Sandboxes

Cross-team and intra-team work happens in isolated sandboxes with shared context.

### Sandbox Types

| Type | Use Case | Lifecycle |
|------|----------|-----------|
| **Light** | Quick request/response (e.g., citation lookup) | Auto-close on response |
| **Standard** | Multi-step collaboration (e.g., contract review) | Manual close |

```python
class MissionSandbox(BaseModel):
    """Isolated workspace for a mission."""

    mission_id: str
    tenant_id: str
    complexity: Literal["light", "standard"] = "light"

    # Shared workspace
    shared_artifacts: dict[str, str]      # Artifact references
    message_thread: list[str]             # UNI-Q message history
    published_findings: dict[str, str]    # team_id -> finding reference

    # Subscriptions for this mission
    team_subscriptions: dict[str, list[str]]  # team_id -> patterns

    # Lifecycle
    status: Literal["active", "completed", "archived"]
    auto_close_on: str | None = None      # Pattern that triggers auto-close
    created_at: datetime
    completed_at: datetime | None
```

**Key decision:** All cross-boundary interactions use sandboxes. No separate "consultation" pattern. Light sandboxes are cheap; consistency is valuable.

---

## Human-in-Loop Protocol

Humans participate in the agent system as special agents with the `Ⓗ` symbol.

```python
class HumanAgent(BaseModel):
    """Human participant in the agent system."""

    agent_id: str              # e.g., "Ⓗjane-doe" or "Ⓗsignoff-authority"
    role: str                  # e.g., "inspector", "attorney", "manager"
    subscriptions: list[str]   # Message patterns they see
    inbox: list[PendingAction] # Work items awaiting human action


class PendingAction(BaseModel):
    """Action awaiting human decision."""

    action_id: str
    mission_id: str
    action_type: Literal["approval", "decision", "review", "exception"]
    context_summary: str       # Human-readable summary
    artifact_refs: list[str]   # What to review
    allowed_actions: list[str] # e.g., ["approve", "reject", "revise"]
    deadline: datetime | None
    claimed_by: str | None
    status: Literal["pending", "claimed", "completed"]
```

### Human Escalation Flow

```
Agent identifies need for human action
         │
         ▼
┌─────────────────────────────────────┐
│  Ⓐagent → Ⓗrole: Ⓔescalation·...   │  Same message format
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│        Human Inbox (UI)             │
│  - View pending escalations         │
│  - Review artifacts                 │
│  - Take action (approve/reject/etc) │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Ⓗhuman → Ⓐagent: Ⓥaction·...✓     │  Response as message
└─────────────────────────────────────┘
```

**Key insight:** Humans are slow, expensive agents. Same routing, same audit trail.

### Escalation Categories

Structured escalation with categories for routing and severity (adapted from Gas Town):

```python
class EscalationCategory(str, Enum):
    """Categories for structured escalation routing."""

    DECISION = "decision"       # Multiple valid paths, need choice
    HELP = "help"               # Need guidance or expertise
    BLOCKED = "blocked"         # Waiting on unresolvable dependency
    FAILED = "failed"           # Unexpected error, can't proceed
    EMERGENCY = "emergency"     # Security or data integrity issue
    GATE_TIMEOUT = "gate_timeout"  # Workflow gate didn't resolve
    LIFECYCLE = "lifecycle"     # Agent stuck or needs intervention


class EscalationSeverity(str, Enum):
    """Severity levels for prioritization."""

    CRITICAL = "critical"  # P0 - System-threatening, immediate attention
    HIGH = "high"          # P1 - Important blocker, needs human soon
    MEDIUM = "medium"      # P2 - Standard escalation, human at convenience


class Escalation(BaseModel):
    """Structured escalation request."""

    escalation_id: str
    mission_id: str
    category: EscalationCategory
    severity: EscalationSeverity
    source_agent: str
    description: str
    context: dict                  # Relevant state for decision
    created_at: datetime

    # For decision category
    options: list[str] | None = None
    recommendation: str | None = None

    # Routing
    routed_to: str | None = None   # Agent/human that should handle
    forwarded_from: str | None = None  # If escalated up the chain


class EscalationRouter:
    """Route escalations based on category and team config."""

    def route(
        self,
        escalation: Escalation,
        team_config: "TeamTemplate",
    ) -> str:
        """
        Determine escalation target based on category.

        Returns agent_id or human role to handle escalation.
        """
        routing = team_config.escalation.get(escalation.category.value)

        if routing:
            return routing.route

        # Default routing by category
        defaults = {
            EscalationCategory.DECISION: "orchestrator",
            EscalationCategory.HELP: "orchestrator",
            EscalationCategory.BLOCKED: "department_head",
            EscalationCategory.FAILED: "orchestrator",
            EscalationCategory.EMERGENCY: "Ⓗemergency-contact",
            EscalationCategory.GATE_TIMEOUT: "orchestrator",
            EscalationCategory.LIFECYCLE: "orchestrator",
        }
        return defaults[escalation.category]
```

### Tiered Escalation Flow

```
Agent encounters issue
         │
         ▼
┌─────────────────────────────────────┐
│  Escalate with category + severity  │
└─────────────────┬───────────────────┘
                  │
                  ▼
         ┌───────────────┐
         │  Team         │  Can resolve?
         │  Orchestrator │──────────────────► Resolution
         └───────┬───────┘       yes
                 │ no
                 ▼
         ┌───────────────┐
         │  Department   │  Can resolve?
         │  Head         │──────────────────► Resolution
         └───────┬───────┘       yes
                 │ no
                 ▼
         ┌───────────────┐
         │  Ⓗ Human      │  Resolution
         │  (Final tier) │
         └───────────────┘
```

Each tier can resolve OR forward. The escalation chain is tracked for audit.

---

## External Gateway

Single bidirectional interface between the agent system and external world.

```python
class ExternalGateway:
    """Bridge between external world and agent system."""

    # Inbound: External → System
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
        Unverified sources go to human review queue (de-scaffolding).
        Returns intake_id for tracking.
        """

    # Outbound: System → External
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

### Gateway Message Flow

```
# Inbound
External App → Ⓖgateway: (raw data)
Ⓖgateway → Ⓐdept-orch: Ⓣintake·mission-001⟨source:inspection-app⟩

# Outbound
Ⓐteam-orch → Ⓖgateway: Ⓣtransmit⟨to:client·channel:email·artifact:report⟩
Ⓖgateway → Ⓐteam-orch: Ⓥtransmitted✓⟨receipt:TXN-001⟩
```

---

## Artifact Store

Mission-scoped storage for documents, photos, and other artifacts.

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
        # Returns: artifact:mission-001/findings-v2

    async def retrieve(
        self,
        artifact_ref: str,
        requesting_agent: str
    ) -> bytes:
        """Retrieve artifact if agent has mission access."""

    async def list_artifacts(self, mission_id: str) -> list[ArtifactMetadata]:
        """List all artifacts in a mission."""
```

**URI scheme:** `artifact:{mission_id}/{artifact_name}`

UNI-Q messages reference artifacts, not contain them:
```
Ⓥfindings·inspection-001✓⟨artifact:inspection-001/findings-v2⟩
```

---

## Temporal Service

Time-based triggers for reminders, deadlines, and scheduled events.

```python
class TemporalTrigger(BaseModel):
    """Scheduled event that fires a UNI-Q message."""

    trigger_id: str
    mission_id: str
    fire_at: datetime
    message: str              # UNI-Q message to send
    target: str               # Recipient agent
    repeat: Literal["once", "daily", "weekly"] = "once"
    cancel_on: list[str]      # Message patterns that cancel this trigger


class TemporalService:
    async def schedule(self, trigger: TemporalTrigger) -> str:
        """Schedule a trigger, return trigger_id."""

    async def cancel(self, trigger_id: str) -> bool:
        """Cancel a scheduled trigger."""
```

**Example: Payment tracking**
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

## Template Registry

Versioned document templates with rendering capability.

```python
class Template(BaseModel):
    """Document template definition."""

    template_id: str
    name: str
    version: str
    content_type: Literal["docx", "html", "pdf"]
    schema: dict              # Required fields for filling
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

---

## Metrics Service

Event-based analytics for business intelligence.

```python
class MetricEvent(BaseModel):
    """Business event for analytics."""

    event_type: str
    mission_id: str | None
    team_id: str
    dimensions: dict          # Filterable attributes
    measures: dict            # Numeric values
    timestamp: datetime


# Example events
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

**UNI-Q format:**
```
Ⓜmetric·mission-completed⟨team:ohs·type:inspection·duration:12d⟩
```

---

## Health Monitoring

Agent health monitoring with intelligent triage (adapted from Gas Town watchdog patterns).

### Heartbeat System

```python
class AgentHeartbeat(BaseModel):
    """Agent health signal."""

    agent_id: str
    team_id: str
    timestamp: datetime
    status: Literal["active", "idle", "processing"]
    current_mission_id: str | None
    current_step: str | None
    context_tokens_used: int
    session_duration_seconds: int


class HeartbeatConfig(BaseModel):
    """Health monitoring thresholds."""

    heartbeat_interval_seconds: int = 60
    stale_threshold_seconds: int = 300      # 5 min
    intervention_threshold_seconds: int = 900  # 15 min


class AgentHealthStatus(str, Enum):
    """Derived health status from heartbeat age."""

    FRESH = "fresh"        # < stale_threshold - healthy
    STALE = "stale"        # >= stale, < intervention - nudge if work pending
    UNRESPONSIVE = "unresponsive"  # >= intervention - intervene
```

### Health Check Logic

```python
class HealthMonitor:
    """Monitor agent health and trigger interventions."""

    def __init__(self, config: HeartbeatConfig):
        self.config = config

    def assess_health(
        self,
        heartbeat: AgentHeartbeat | None,
        current_time: datetime,
    ) -> AgentHealthStatus:
        """Assess agent health from heartbeat."""
        if heartbeat is None:
            return AgentHealthStatus.UNRESPONSIVE

        age_seconds = (current_time - heartbeat.timestamp).total_seconds()

        if age_seconds < self.config.stale_threshold_seconds:
            return AgentHealthStatus.FRESH
        elif age_seconds < self.config.intervention_threshold_seconds:
            return AgentHealthStatus.STALE
        else:
            return AgentHealthStatus.UNRESPONSIVE

    async def handle_stale_agent(
        self,
        agent_id: str,
        has_pending_work: bool,
    ) -> None:
        """Handle stale agent - nudge if work pending."""
        if has_pending_work:
            await self.send_nudge(agent_id, "Health check: work pending")

    async def handle_unresponsive_agent(
        self,
        agent_id: str,
    ) -> None:
        """Handle unresponsive agent - escalate to orchestrator."""
        escalation = Escalation(
            escalation_id=generate_id(),
            mission_id=None,
            category=EscalationCategory.LIFECYCLE,
            severity=EscalationSeverity.HIGH,
            source_agent="health_monitor",
            description=f"Agent {agent_id} unresponsive for >{self.config.intervention_threshold_seconds}s",
            context={"agent_id": agent_id},
            created_at=datetime.utcnow(),
        )
        await self.escalate(escalation)
```

### Orchestrator Health Responsibilities

Team Orchestrators are responsible for monitoring their specialists:

```python
class OrchestratorHealthDuties:
    """Health monitoring performed by team orchestrators."""

    async def patrol_cycle(self) -> None:
        """Periodic health check of team agents."""
        for agent_id in self.team_agents:
            heartbeat = await self.get_latest_heartbeat(agent_id)
            status = self.health_monitor.assess_health(heartbeat, datetime.utcnow())

            match status:
                case AgentHealthStatus.FRESH:
                    pass  # Healthy
                case AgentHealthStatus.STALE:
                    pending = await self.has_pending_work(agent_id)
                    await self.health_monitor.handle_stale_agent(agent_id, pending)
                case AgentHealthStatus.UNRESPONSIVE:
                    await self.health_monitor.handle_unresponsive_agent(agent_id)

    async def handle_session_cycle(
        self,
        agent_id: str,
        reason: SessionCycleReason,
    ) -> None:
        """Handle agent session cycling."""
        if reason == SessionCycleReason.CRASH:
            # Log crash, consider intervention
            await self.log_agent_crash(agent_id)

        if reason != SessionCycleReason.COMPLETION:
            # Respawn session with checkpointed state
            await self.respawn_agent_session(agent_id)
```

**Key insight:** Health monitoring is an orchestrator responsibility, not a separate daemon. This keeps the fractal pattern consistent.

---

## Mission Lifecycle State Machine

Explicit states with defined transitions for auditability.

```python
class MissionStatus(str, Enum):
    # Normal flow
    INTAKE = "intake"
    PROCESSING = "processing"
    PENDING_EXTERNAL = "pending_external"    # Waiting on cross-team
    PENDING_HUMAN = "pending_human"          # Waiting on human
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
```

**State transition diagram:**
```
INTAKE → PROCESSING → PENDING_EXTERNAL → PROCESSING → DELIVERABLE_READY
                   └→ PENDING_HUMAN ────┘
                              ↓
         DELIVERABLE_READY → DELIVERED → INVOICED → PAYMENT_PENDING → PAID → CLOSED

Exception paths:
- Any → BLOCKED (waiting on dependency)
- Any → ESCALATED (needs human intervention)
- DELIVERABLE_READY → PROCESSING (revision needed)
- PAYMENT_PENDING → ESCALATED (collections)
```

---

## Finance Team

Dedicated team for financial operations.

```
┌─────────────────────────────────────────────────────────────────────┐
│  FINANCE TEAM                                                        │
│                                                                      │
│  ┌─────────────────┐                                                │
│  │Finance Orchestrator│                                              │
│  └────────┬────────┘                                                │
│           │                                                          │
│  ┌────────┼────────┬────────────┬────────────┬──────────┐          │
│  ▼        ▼        ▼            ▼            ▼          ▼          │
│ Invoice  AR      Payment      Tax       Reconcil-  Librarian       │
│ Agent   Agent    Agent       Agent      iation                      │
│                                          Agent                       │
└─────────────────────────────────────────────────────────────────────┘

Responsibilities:
- Invoice Agent: Generate invoices from billing requests
- AR Agent: Track receivables, send reminders, manage collections
- Payment Agent: Match payments to invoices, record receipts
- Tax Agent: Calculate and allocate taxes (federal/state/local)
- Reconciliation Agent: Update accounts, generate financial reports
```

**Integration pattern:**
```
Ⓐohs-orch → Ⓐdept-orch: Ⓣbilling-request⟨mission:X·scope-ref:Y⟩
Ⓐdept-orch → Ⓐfinance-orch: Ⓣbilling-request⟨from:ohs·mission:X⟩
Ⓐfinance-orch → Ⓐinvoice-agent: Ⓣgenerate-invoice⟨...⟩
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

*Version: 2.4*
*Created: 2025-01-05*
*Updated: 2025-01-08*
*Status: Complete architecture specification for implementation handoff*

## Changes in v2.4

- Added Team Template Schema (YAML-based team configuration)
- Added Agent Lifecycle Layers (Session/Sandbox/Identity separation from Gas Town)
- Added Escalation Categories (decision, help, blocked, failed, emergency, gate_timeout, lifecycle)
- Added Tiered Escalation Flow (Team Orchestrator → Department Head → Human)
- Added Standard Message Types catalog for UNI-Q
- Added Workflow step tracking with gates and auto-advance
- Added Health Monitoring section with heartbeat system
- Added Orchestrator Health Responsibilities
- Referenced Gas Town framework analysis in `planning/research/GHOST_TOWN.md`

## Changes in v2.3

- Added UNI-Q communication grammar with full symbol reference
- Added new symbols: `Ⓡ` (Request), `Ⓗ` (Human), `Ⓖ` (Gateway), `Ⓜ` (Metric)
- Added Fractal Architecture section (same pattern at every level)
- Added Mission Sandboxes (light vs standard, parameterized)
- Added Human-in-Loop Protocol (humans as special agents)
- Added External Gateway (bidirectional external interface with de-scaffolding)
- Added Artifact Store (mission-scoped document storage)
- Added Temporal Service (time-based triggers and reminders)
- Added Template Registry (versioned document templates)
- Added Metrics Service (event-based analytics)
- Added Mission Lifecycle State Machine (explicit states)
- Added Finance Team specification
- Added Design Principles 13-14 (fractal architecture, humans as agents)
- Referenced UNIQ_SPEC.md and UNIQ_EXAMPLES.md for detailed specifications
- Referenced SCENARIO_OHS_INSPECTION.md and DECISION_LOG.md for design rationale

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
