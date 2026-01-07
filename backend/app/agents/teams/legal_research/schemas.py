"""Schemas for Legal Research Team."""

from typing import Literal

from pydantic import BaseModel, Field

# =============================================================================
# Citation Types
# =============================================================================


class Citation(BaseModel):
    """Base citation model."""

    source_type: str
    citation_text: str
    title: str
    date: str | None = None
    url: str | None = None
    relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    excerpt: str = ""


class StatuteCitation(Citation):
    """Citation to a statute or code section."""

    source_type: str = "statute"
    code: str = ""  # e.g., "Maryland Code"
    section: str = ""
    subsection: str = ""


class CaseCitation(Citation):
    """Citation to a court case."""

    source_type: str = "case"
    court: str = ""
    year: int | None = None
    reporter: str = ""
    page: str = ""


class RegulationCitation(Citation):
    """Citation to a regulation."""

    source_type: str = "regulation"
    agency: str = ""
    section: str = ""


class PriorOpinionCitation(Citation):
    """Citation to a prior opinion from this office."""

    source_type: str = "prior_opinion"
    opinion_id: str = ""
    matter_type: str = ""
    outcome: str = ""


# =============================================================================
# Research Types
# =============================================================================


class Finding(BaseModel):
    """A key finding from research."""

    statement: str
    supporting_citations: list[str]  # Citation texts
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class Conflict(BaseModel):
    """A conflict between sources."""

    description: str
    source_a: str
    source_b: str
    resolution_approach: str = ""


class Gap(BaseModel):
    """A gap in the research."""

    description: str
    impact: str  # How this affects the conclusion
    mitigation: str = ""  # What we did about it


class AlternativeConclusion(BaseModel):
    """An alternative conclusion that could be supported."""

    conclusion: str
    supporting_authority: list[str]
    confidence: float = Field(default=0.3, ge=0.0, le=1.0)
    why_not_recommended: str = ""


# =============================================================================
# Request and Response Types
# =============================================================================


class RequesterInfo(BaseModel):
    """Information about the requester."""

    name: str
    email: str
    department: str
    title: str = ""
    phone: str = ""


class TriageResult(BaseModel):
    """Output from the Intake/Triage agent."""

    request_id: str
    requester: RequesterInfo

    # Parsed question
    core_question: str
    sub_questions: list[str] = Field(default_factory=list)

    # Context
    department: str
    urgency: Literal["routine", "priority", "urgent"] = "routine"
    matter_type: str  # employment, contracts, liability, etc.

    # Routing
    needs_clarification: bool = False
    clarification_questions: list[str] = Field(default_factory=list)

    # Assignment
    complexity: Literal["simple", "moderate", "complex"] = "moderate"
    estimated_research_hours: float = 2.0
    relevant_prior_opinions: list[str] = Field(default_factory=list)


class ResearchMemo(BaseModel):
    """Output from the Research agent."""

    request_id: str

    # Sources found
    statutes: list[StatuteCitation] = Field(default_factory=list)
    cases: list[CaseCitation] = Field(default_factory=list)
    regulations: list[RegulationCitation] = Field(default_factory=list)
    prior_opinions: list[PriorOpinionCitation] = Field(default_factory=list)

    # Synthesis
    key_findings: list[Finding] = Field(default_factory=list)
    applicable_rules: list[str] = Field(default_factory=list)

    # Analysis
    conflicts: list[Conflict] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)

    # Recommendation
    recommended_conclusion: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    alternative_conclusions: list[AlternativeConclusion] = Field(default_factory=list)


class CitationCheck(BaseModel):
    """Result of verifying a citation."""

    citation: str
    verified: bool
    issue: str = ""
    corrected: str = ""


class OpinionHeader(BaseModel):
    """Header for the formal opinion."""

    to: str
    from_: str = Field(alias="from")
    date: str
    re: str
    opinion_number: str = ""


class DraftOpinion(BaseModel):
    """Output from the Drafting agent."""

    request_id: str

    # Document sections
    header: OpinionHeader
    question_presented: str
    brief_answer: str
    facts: str
    analysis: str
    conclusion: str

    # Metadata
    citations_used: list[Citation] = Field(default_factory=list)
    word_count: int = 0
    draft_version: int = 1

    # Caveats
    limitations: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class ReviewIssue(BaseModel):
    """An issue found during review."""

    category: str  # citation, logic, completeness, clarity, risk
    severity: Literal["minor", "major", "critical"]
    description: str
    location: str = ""  # Where in the document
    suggestion: str = ""


class ReviewResult(BaseModel):
    """Output from the Review agent."""

    request_id: str
    draft_version: int

    # Verification
    citations_verified: list[CitationCheck] = Field(default_factory=list)
    reasoning_sound: bool = True
    question_answered: bool = True

    # Issues found
    issues: list[ReviewIssue] = Field(default_factory=list)
    severity: Literal["none", "minor", "major", "critical"] = "none"

    # Decision
    approved: bool = False
    revision_instructions: str = ""

    # Quality metrics
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    consistency_with_prior: float = Field(default=0.5, ge=0.0, le=1.0)


# =============================================================================
# Team Memory Types
# =============================================================================


class LegalResearchMemoryTypes:
    """Memory type definitions for the Legal Research team."""

    STRATEGIC = ["goal", "policy_objective"]
    OPERATIONAL = ["standard", "procedure", "template", "style_guide"]
    ENTITY = ["department", "attorney", "topic", "statute_summary"]
    EVENT = ["opinion", "research_request", "citation_update"]
