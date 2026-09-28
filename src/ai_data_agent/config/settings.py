from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded and validated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM provider
    llm_provider: str = Field(default="ollama")
    llm_model_name: str = Field(default="llama3.2:3b")
    ollama_base_url: str = Field(default="http://localhost:11434")

    # Database
    db_provider: str = Field(default="postgres")
    database_url: str
    readonly_database_url: str
    marketing_database_url: str = ""
    marketing_readonly_database_url: str = ""

    # Snowflake (only required if db_provider=snowflake)
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
    snowflake_database: Optional[str] = None

    # App behavior
    app_env: str = Field(default="development")
    max_retry_count: int = Field(default=2, ge=0, le=5)
    query_timeout_seconds: int = Field(default=10, ge=1)
    max_result_rows: int = Field(default=500, ge=1, le=5000)


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance, loaded once per process."""
    return Settings()

