# Quandura Backend

Enterprise AI agent platform for local government operations.

## Setup

```bash
# Install dependencies
uv sync

# Copy environment config
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# Run migrations
uv run alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload
```

## API

- `POST /api/v1/missions` - Create mission
- `GET /api/v1/missions` - List missions
- `GET /api/v1/missions/{id}` - Get mission details
- `POST /api/v1/missions/{id}/execute` - Run through agent pipeline
