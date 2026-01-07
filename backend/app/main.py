"""Quandura API entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import memory_router, missions_router

app = FastAPI(
    title="Quandura",
    description="Enterprise AI agent platform for local government operations",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Quandura API", "docs": "/docs"}


# Include routers
app.include_router(missions_router, prefix="/api/v1")
app.include_router(memory_router, prefix="/api/v1")
