"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Quandura"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://quandura:quandura@localhost:5432/quandura"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    anthropic_api_key: str = ""
    default_model: str = "claude-sonnet-4-20250514"

    # Auth (Keycloak)
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "quandura"
    keycloak_client_id: str = "quandura-api"

    # Vector DB
    chroma_host: str = "localhost"
    chroma_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
