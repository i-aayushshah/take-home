"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables."""

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    redis_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    github_token: str = ""
    github_model: str = "openai/gpt-4o-mini"
    ai_summary_fallback_mock: bool = True
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=str(_ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field
    @property
    def cors_origin_list(self) -> list[str]:
        """Return parsed CORS allowed origins from a comma-separated env value."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @computed_field
    @property
    def database_url(self) -> str:
        """Build the async PostgreSQL connection URL from POSTGRES_* variables."""
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    """Return the cached Settings singleton."""
    return Settings()
