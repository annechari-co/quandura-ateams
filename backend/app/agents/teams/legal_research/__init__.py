"""Legal Research Team - County Law Office implementation."""

from app.agents.teams.legal_research.analyst import CitationAnalyst
from app.agents.teams.legal_research.drafter import OpinionDrafter
from app.agents.teams.legal_research.intake import ResearchIntake
from app.agents.teams.legal_research.orchestrator import LegalResearchOrchestrator
from app.agents.teams.legal_research.researcher import LegalResearcher
from app.agents.teams.legal_research.reviewer import QualityReviewer

__all__ = [
    "LegalResearchOrchestrator",
    "ResearchIntake",
    "LegalResearcher",
    "CitationAnalyst",
    "OpinionDrafter",
    "QualityReviewer",
]
