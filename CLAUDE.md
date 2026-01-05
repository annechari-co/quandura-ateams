# Quandura - Project Instructions

Enterprise AI agent platform for local government operations.

## Quick Start

**Start here:** `planning/QUANDURA_ARCHITECTURE.md` - Complete technical specification

### Key Documents

| Document | Purpose |
|----------|---------|
| `planning/QUANDURA_ARCHITECTURE.md` | Core architecture, schemas, implementation roadmap |
| `planning/ENTERPRISE_PLAN.md` | Business context, target market, service model |
| `planning/teams/LAW_OFFICE_LEGAL_RESEARCH.md` | First validation team specification |
| `research/COMPLIANCE_RESEARCH.md` | SOC 2, CJIS, StateRAMP requirements |
| `research/ARCHITECTURE_RESEARCH.md` | Multi-tenancy, sandboxing patterns |
| `research/VOICE_RESEARCH.md` | Telephony, STT, TTS integration |

## Vision

Build the "OS for Local Governments" - AI agent teams that run department operations with minimal human staff.

**Beachhead:** Risk Management departments at county level
**First Validation:** County Law Office (Legal Research & Opinions team)
**Deployment Model:** Palantir-style embedded teams

## Current Phase

**Phase 1: Core Foundation** (8-10 weeks)

Priority order:
1. Project scaffolding (FastAPI, PostgreSQL, Redis)
2. Passport schema and persistence
3. LangGraph checkpointing integration
4. Base agent class with confidence tracking
5. Single-team orchestrator
6. Basic Librarian (ChromaDB)
7. Simple web UI
8. Authentication (Keycloak)

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, LangGraph
- **LLM:** Claude 3.5 Sonnet
- **Database:** PostgreSQL (RLS for multi-tenancy)
- **Cache:** Redis
- **Vector DB:** ChromaDB (→ Pinecone at scale)
- **Frontend:** React + TypeScript + Tailwind + shadcn/ui
- **Voice:** Twilio + Deepgram + ElevenLabs

## Architecture Principles

1. **Multi-tenant from day one** - Every table has tenant_id, RLS enabled
2. **Passport is the state** - JSON object travels between agents
3. **Hub-and-spoke communication** - Specialists only talk to orchestrators
4. **Evidence-based confidence** - Vectors not scalars
5. **External validation required** - Self-correction needs feedback
6. **De-scaffolding** - Start structured, earn autonomy

## Code Standards

- Use Pydantic for all data models
- Type hints everywhere
- Google-style docstrings
- Async by default
- Tests for agent behaviors

## Commands

```bash
# Backend
cd backend && uv run uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev

# Tests
cd backend && uv run pytest
```

## Don't Forget

- This is government software - compliance matters
- Latency budget for voice is tight (<1000ms)
- Every action must be auditable
- Human escalation paths are required
