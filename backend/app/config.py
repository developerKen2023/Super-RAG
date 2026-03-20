from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Union


def parse_cors_origins(value: Union[str, list]) -> list[str]:
    """Parse CORS origins from string or list."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        # Try JSON first, then comma-separated
        import json
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return [v.strip() for v in value.split(",") if v.strip()]
    return ["http://localhost:5173"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # LLM Provider (OpenAI-compatible)
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"

    # LangSmith
    langsmith_api_key: str | None = None
    langsmith_tracing: bool = False
    langsmith_project: str = "agentic-rag-masterclass"

    # App
    app_env: str = "development"
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_cors_origins(self) -> list[str]:
        return parse_cors_origins(self.cors_origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()
