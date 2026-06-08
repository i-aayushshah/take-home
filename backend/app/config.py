"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    database_url: str
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    github_token: str = ""
    github_model: str = "openai/gpt-4o-mini"
    ai_summary_fallback_mock: bool = True

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton."""
    return Settings()
