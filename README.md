# Quandura

Enterprise AI agent platform for local government operations.

## Overview

Quandura enables local governments to deploy AI agent teams that automate department workflows while maintaining full audit trails and human oversight.

## Status

**Phase 1: Core Foundation** - In Development

## Documentation

- [Architecture Specification](planning/QUANDURA_ARCHITECTURE.md)
- [Enterprise Plan](planning/ENTERPRISE_PLAN.md)
- [Legal Research Team](planning/teams/LAW_OFFICE_LEGAL_RESEARCH.md)

## Development

```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## License

Proprietary - All rights reserved
