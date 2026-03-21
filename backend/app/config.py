from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Union
import os


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

    # Default LLM Provider
    default_llm_provider: str = "minimax"

    # MiniMax
    minimax_api_key: str
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-M2.7-highspeed"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set LangSmith env vars so langsmith library can read them
        if self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
        if self.langsmith_tracing:
            os.environ["LANGSMITH_TRACING"] = "true"
        os.environ["LANGSMITH_PROJECT"] = self.langsmith_project

    def get_cors_origins(self) -> list[str]:
        return parse_cors_origins(self.cors_origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()
