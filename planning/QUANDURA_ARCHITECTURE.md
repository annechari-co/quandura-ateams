# Quandura: Core Architecture Specification

## Executive Summary

Quandura is an enterprise AI agent platform targeting local government operations. The initial beachhead is Risk Management departments, with the long-term vision of becoming the "OS for Local Governments" - eventually running entire government operations with minimal human staff.

**Deployment Model:** Palantir-style embedded teams that learn workflows and build custom agent teams for each client.

**Service Model:** Setup + ongoing support, with potential evolution toward managed service for end-state clients.

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
3. **External validation** - Self-correction requires external feedback
4. **Hierarchical memory** - Working, episodic, semantic tiers
5. **Hub-and-spoke communication** - Orchestrator/Librarian as hubs, specialists talk only to hubs
6. **De-scaffolding** - Start structured, loosen as confidence grows

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

### Three-Tier Hierarchical Memory

```python
from enum import Enum


class MemoryTier(str, Enum):
    WORKING = "working"      # Current task context
    EPISODIC = "episodic"    # Past task experiences
    SEMANTIC = "semantic"    # Distilled knowledge


class MemoryStore:
    """
    Hierarchical memory with automatic promotion.

    Working → Episodic (on task completion)
    Episodic → Semantic (via Platform Intelligence analysis)
    """

    def __init__(
        self,
        tenant_id: str,
        team_id: str,
        vector_db: "ChromaDB",
        knowledge_graph: "Neo4j",
    ):
        self.tenant_id = tenant_id
        self.team_id = team_id
        self.vector_db = vector_db
        self.kg = knowledge_graph

    async def store_working(
        self,
        passport_id: str,
        key: str,
        value: Any,
        ttl_seconds: int = 3600,
    ) -> None:
        """Store in working memory (Redis-backed, short TTL)."""
        pass

    async def retrieve_working(
        self,
        passport_id: str,
        key: str,
    ) -> Optional[Any]:
        """Retrieve from working memory."""
        pass

    async def store_episodic(
        self,
        episode: "Episode",
    ) -> str:
        """
        Store completed task as episode.

        Creates vector embedding for similarity search.
        """
        pass

    async def query_episodic(
        self,
        query: str,
        task_type: Optional[str] = None,
        limit: int = 5,
    ) -> List["Episode"]:
        """Find similar past episodes."""
        pass

    async def store_semantic(
        self,
        fact: "SemanticFact",
    ) -> str:
        """
        Store distilled knowledge in knowledge graph.

        Links to source episodes for provenance.
        """
        pass

    async def query_semantic(
        self,
        query: str,
        fact_types: Optional[List[str]] = None,
    ) -> List["SemanticFact"]:
        """Query knowledge graph for relevant facts."""
        pass


class Episode(BaseModel):
    """A completed task stored in episodic memory."""

    id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    team_id: str
    task_type: str

    # What happened
    mission_summary: str
    outcome: Literal["success", "partial", "failure", "escalated"]

    # What we learned
    key_decisions: List[str]
    mistakes_made: List[str]
    successful_patterns: List[str]

    # For retrieval
    embedding: Optional[List[float]] = None
    tags: List[str] = Field(default_factory=list)

    # Provenance
    passport_id: UUID
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SemanticFact(BaseModel):
    """Distilled knowledge in the knowledge graph."""

    id: UUID = Field(default_factory=uuid4)
    tenant_id: str
    team_id: str

    # The fact
    statement: str
    fact_type: str  # rule, pattern, exception, definition
    confidence: float

    # Graph connections
    related_facts: List[UUID] = Field(default_factory=list)
    source_episodes: List[UUID] = Field(default_factory=list)

    # Validity
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
    superseded_by: Optional[UUID] = None
```

---

## Platform Intelligence Layer

### Janitor (Per-Team)

```python
class Janitor:
    """
    Per-team observer that identifies issues and patterns.

    Runs continuously, watching team activity and flagging:
    - Repeated failures
    - Confidence calibration drift
    - New patterns worth learning
    - Tool usage inefficiencies
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

### Phase 1: Core Foundation (8-10 weeks)

**Goal:** Passport system, basic agents, LangGraph integration

- [ ] Project scaffolding (FastAPI, PostgreSQL, Redis)
- [ ] Passport schema and persistence
- [ ] LangGraph checkpointing integration
- [ ] Base agent class with confidence tracking
- [ ] Single-team orchestrator
- [ ] Basic Librarian (ChromaDB)
- [ ] Simple web UI (team viewer, chat)
- [ ] Authentication (Keycloak)

**Validation:** Run a 3-agent pipeline (Triage → Draft → Review) on test inputs

### Phase 2: Legal Research Team (6-8 weeks)

**Goal:** Complete County Law Office implementation

- [ ] Triage agent
- [ ] Research agent with legal database tools
- [ ] Drafting agent with citation formatting
- [ ] Review agent with verification
- [ ] Delivery agent with email
- [ ] Email intake integration
- [ ] Opinion knowledge base
- [ ] Team-specific UI

**Validation:** Process real legal research requests from test data

### Phase 3: Voice Interface (6-8 weeks)

**Goal:** Phone-based intake working

- [ ] Twilio WebSocket handler
- [ ] Deepgram streaming integration
- [ ] ElevenLabs streaming integration
- [ ] Latency optimization
- [ ] Interrupt detection
- [ ] Recording and transcription storage
- [ ] Consent flow
- [ ] Voice-specific agents

**Validation:** Complete intake call with <1.5s perceived latency

### Phase 4: Platform Intelligence (6-8 weeks)

**Goal:** Janitor, Housekeeper, Research Scouts operational

- [ ] Janitor per-team observers
- [ ] Observation aggregation
- [ ] Housekeeper analysis
- [ ] Research Scout framework
- [ ] Proposal system
- [ ] Human review interface
- [ ] De-scaffolding engine
- [ ] Cross-team knowledge sharing

**Validation:** Platform proposes at least one valid improvement from observations

### Phase 5: Production Hardening (8-10 weeks)

**Goal:** Enterprise-ready for pilot deployment

- [ ] Multi-tenant isolation audit
- [ ] SOC 2 preparation
- [ ] Performance optimization
- [ ] Disaster recovery
- [ ] Cost tracking and billing
- [ ] Admin dashboards
- [ ] Documentation
- [ ] Pilot deployment

**Validation:** Successful pilot with real government client

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

*Version: 1.0*
*Created: 2025-01-05*
*Status: Ready for implementation handoff*
