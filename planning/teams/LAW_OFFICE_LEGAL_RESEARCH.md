# County Law Office: Legal Research & Opinions Team

## Purpose

Handle legal research requests from county departments. Departments submit questions via email, the team researches, and delivers written legal opinions with citations.

## Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTAKE                                   │
│  Email arrives → Parsed → Ticket created                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TRIAGE AGENT                                │
│                                                                  │
│  • Parse the request - what are they actually asking?           │
│  • Identify requesting department and context                    │
│  • Categorize: simple lookup vs. complex analysis               │
│  • Determine if clarification needed                            │
│  • Assign priority based on urgency signals                     │
│                                                                  │
│  Outputs:                                                        │
│  → Clarification request (back to requester) OR                 │
│  → Research assignment (to Research Agent)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RESEARCH AGENT                               │
│                                                                  │
│  • Search relevant legal sources:                                │
│    - State statutes and codes                                   │
│    - Case law (state and federal)                               │
│    - County ordinances and policies                             │
│    - Attorney General opinions                                   │
│    - Prior opinions from this office                            │
│  • Synthesize findings                                          │
│  • Identify applicable precedents                               │
│  • Note any conflicts or ambiguities                            │
│                                                                  │
│  Outputs:                                                        │
│  → Research memo with citations                                  │
│  → Key sources identified                                        │
│  → Recommended conclusion                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DRAFTING AGENT                               │
│                                                                  │
│  • Write formal legal opinion document                          │
│  • Structure:                                                    │
│    1. Question Presented                                        │
│    2. Brief Answer                                              │
│    3. Facts (as understood)                                     │
│    4. Analysis                                                  │
│    5. Conclusion                                                │
│  • Integrate citations properly                                 │
│  • Match office's style and format                              │
│  • Flag any caveats or limitations                              │
│                                                                  │
│  Outputs:                                                        │
│  → Draft opinion document                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      REVIEW AGENT                                │
│                                                                  │
│  • Verify all citations are accurate                            │
│  • Check reasoning follows from sources                         │
│  • Identify logical gaps or weak points                         │
│  • Ensure question is fully answered                            │
│  • Check for consistency with prior opinions                    │
│  • Grade confidence in conclusion                               │
│                                                                  │
│  Outputs:                                                        │
│  → Approval OR                                                   │
│  → Revision requests (back to Drafting or Research)             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DELIVERY AGENT                                │
│                                                                  │
│  • Format final document                                        │
│  • Generate cover email                                         │
│  • Archive opinion in knowledge base                            │
│  • Update topic index                                           │
│  • Send to requester                                            │
│  • Log for metrics                                              │
│                                                                  │
│  Outputs:                                                        │
│  → Email with attached opinion                                   │
│  → Archived copy with metadata                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

### Orchestrator: Legal Research Manager

**Role:** Coordinates the team, monitors progress, handles exceptions

**Responsibilities:**
- Route work through the pipeline
- Intervene when agents get stuck
- Escalate to human attorney when needed
- Track SLAs and workload
- Answer status queries from department head agent

**Authority Level:** Soft intervention (can pause, request clarification, escalate)

**Escalation Triggers:**
- Novel legal question with no precedent
- Conflicting authority (statutes vs. case law)
- High-stakes matter (litigation risk, policy change)
- Request from elected official
- Confidence score below threshold

---

### Agent: Triage

**Purpose:** Understand incoming requests and prepare for research

**Inputs:**
- Raw email content
- Sender information
- Any attachments

**Outputs:**
```python
class TriageResult(BaseModel):
    request_id: str
    requester: RequesterInfo

    # Parsed question
    core_question: str
    sub_questions: List[str]

    # Context
    department: str
    urgency: Literal["routine", "priority", "urgent"]
    matter_type: str  # employment, contracts, liability, etc.

    # Routing
    needs_clarification: bool
    clarification_questions: List[str]

    # Assignment
    complexity: Literal["simple", "moderate", "complex"]
    estimated_research_hours: float
    relevant_prior_opinions: List[str]  # IDs of related past work
```

**Tools:**
- Email parser
- Department directory lookup
- Prior opinions search
- Urgency classifier

---

### Agent: Research

**Purpose:** Find and synthesize relevant legal authority

**Inputs:**
- Triage result
- Any clarifications received

**Outputs:**
```python
class ResearchMemo(BaseModel):
    request_id: str

    # Sources found
    statutes: List[StatuteCitation]
    cases: List[CaseCitation]
    regulations: List[RegulationCitation]
    ag_opinions: List[AGOpinionCitation]
    prior_opinions: List[PriorOpinionCitation]

    # Synthesis
    key_findings: List[Finding]
    applicable_rules: List[str]

    # Analysis
    conflicts: List[Conflict]  # Where sources disagree
    gaps: List[Gap]  # What we couldn't find

    # Recommendation
    recommended_conclusion: str
    confidence: ConfidenceVector
    alternative_conclusions: List[AlternativeConclusion]
```

**Tools:**
- Legal database search (Westlaw, LexisNexis, or free alternatives)
- State code lookup
- Case law search
- County ordinance database
- Prior opinions database (internal)
- Web search for secondary sources

**Key Behaviors:**
- Always cite primary sources over secondary
- Note the date and current validity of each source
- Identify controlling vs. persuasive authority
- Flag if research is incomplete

---

### Agent: Drafting

**Purpose:** Write the formal legal opinion

**Inputs:**
- Original request
- Research memo

**Outputs:**
```python
class DraftOpinion(BaseModel):
    request_id: str

    # Document sections
    header: OpinionHeader  # To, From, Date, Re
    question_presented: str
    brief_answer: str
    facts: str
    analysis: str  # Main body with citations
    conclusion: str

    # Metadata
    citations_used: List[Citation]
    word_count: int
    draft_version: int

    # Caveats
    limitations: List[str]
    assumptions: List[str]
```

**Style Guidelines:**
- Clear, plain language where possible
- Formal legal structure
- Citations in Bluebook format (or local convention)
- Conclusion answers the exact question asked
- Analysis follows IRAC (Issue, Rule, Application, Conclusion)

---

### Agent: Review

**Purpose:** Quality assurance before delivery

**Inputs:**
- Draft opinion
- Research memo
- Original request

**Outputs:**
```python
class ReviewResult(BaseModel):
    request_id: str
    draft_version: int

    # Verification
    citations_verified: List[CitationCheck]
    reasoning_sound: bool
    question_answered: bool

    # Issues found
    issues: List[ReviewIssue]
    severity: Literal["none", "minor", "major", "critical"]

    # Decision
    approved: bool
    revision_instructions: Optional[str]

    # Quality metrics
    confidence_assessment: ConfidenceVector
    consistency_with_prior: float  # 0-1, how well it aligns with past opinions
```

**Checks Performed:**
1. **Citation accuracy** - Does each citation exist and say what we claim?
2. **Logic flow** - Does conclusion follow from analysis?
3. **Completeness** - Are all sub-questions addressed?
4. **Consistency** - Conflicts with prior opinions?
5. **Clarity** - Will requester understand this?
6. **Risk** - Any statements that could create liability?

---

### Agent: Delivery

**Purpose:** Format, archive, and send

**Inputs:**
- Approved opinion
- Original request

**Outputs:**
- Formatted PDF/Word document
- Cover email
- Archive entry

**Actions:**
1. Apply office letterhead/template
2. Generate cover email summarizing the opinion
3. Store in knowledge base with full metadata
4. Update topic index for future searchability
5. Send to requester (and CC appropriate parties)
6. Log completion metrics

---

### Librarian: Legal Knowledge Base

**Purpose:** Maintain searchable repository of all opinions and sources

**Responsibilities:**
- Index all opinions by topic, statute, date
- Track citation relationships
- Identify when new law might affect old opinions
- Answer queries about prior work
- Suggest relevant precedents for new matters

**Knowledge Stored:**
- All prior opinions (full text + metadata)
- Frequently cited statutes and cases
- Department-specific guidance history
- Topic taxonomy

---

## Data Sources Required

| Source | Type | Access Method |
|--------|------|---------------|
| State Statutes | Legal authority | API or scraping |
| Case Law | Legal authority | Westlaw/Lexis API or CourtListener |
| County Code | Local authority | County website or database |
| AG Opinions | Guidance | State AG website |
| Prior Opinions | Internal | Knowledge base |
| Department Directory | Context | HR system or manual |

---

## Passport Schema for This Team

```python
class LegalResearchPassport(Passport):
    # Extend base Passport

    # Legal-specific fields
    matter_type: str
    requesting_department: str

    # Research state
    sources_searched: List[str]
    sources_found: int
    key_authorities: List[Citation]

    # Draft state
    draft_version: int
    review_status: Literal["pending", "in_review", "approved", "revision_needed"]

    # Quality
    citation_accuracy: float
    reasoning_confidence: float

    # Tracking
    sla_deadline: datetime
    days_in_progress: int
```

---

## Metrics to Track

| Metric | Description | Target |
|--------|-------------|--------|
| Response Time | Request to delivery | < 5 days routine, < 2 days priority |
| Citation Accuracy | % of citations verified correct | > 99% |
| Requester Satisfaction | Follow-up survey | > 4.5/5 |
| Escalation Rate | % requiring human attorney | < 20% |
| Revision Rate | % needing revision after review | < 15% |

---

## Human Escalation Criteria

The team MUST escalate to a human attorney when:

1. **Novel question** - No precedent found in research
2. **High stakes** - Litigation risk, policy change, elected official request
3. **Conflicting authority** - Cannot reconcile different sources
4. **Low confidence** - Confidence score below 0.7
5. **Sensitive topic** - Employment termination, civil rights, criminal matters
6. **Time pressure** - Cannot meet deadline with quality

---

## Integration Points

### Inbound
- Email inbox monitoring
- (Future) Phone intake via voice agent
- (Future) Web form submission
- (Future) Integration with case management system

### Outbound
- Email delivery
- Document storage (SharePoint, Drive, etc.)
- (Future) Case management system update
- (Future) Billing/time tracking system

---

## What This Validates

Building this team tests:

| Architecture Element | How It's Tested |
|---------------------|-----------------|
| Multi-agent coordination | 5 agents working in sequence |
| Passport state passing | Research → Draft → Review flow |
| External tool integration | Legal database searches |
| Document generation | Opinion drafting |
| Quality assurance pattern | Review agent checking work |
| Knowledge persistence | Librarian maintaining opinions |
| Escalation logic | Human handoff when needed |
| Confidence tracking | Evidence-based confidence vectors |

---

## Foundation for Voice (Future)

When we add phone intake:

```
Phone Call → Twilio → Speech-to-Text → Triage Agent
                                          │
                                          ▼
                                    (Same pipeline)
```

The only new component is the voice-to-text front end. The rest of the pipeline stays the same.

---

*Version: 1.0*
*Created: 2025-01-05*
