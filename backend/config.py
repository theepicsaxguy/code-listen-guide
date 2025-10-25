"""Application configuration helpers."""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration with sensible defaults for local development."""

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )

    database_url: str = Field(default="sqlite:///./backend_dev.db")
    checkpoint_database_url: str = Field(default="sqlite:///./backend_dev.db")

    anthropic_api_key: str = Field(default="dev-anthropic-key")
    openai_api_key: Optional[str] = Field(default=None)
    openai_responses_model: str = Field(default="gpt-4o-mini")
    openai_base_url: Optional[str] = Field(default=None)

    stripe_secret_key: str = Field(default="sk_test_placeholder")
    stripe_webhook_secret: str = Field(default="whsec_placeholder")
    stripe_publishable_key: str = Field(default="pk_test_placeholder")

    aws_access_key_id: str = Field(default="aws-access-key")
    aws_secret_access_key: str = Field(default="aws-secret-key")
    s3_bucket_name: str = Field(default="codebase-audiobooks")
    s3_region: str = Field(default="us-east-1")

    jwt_secret: str = Field(default="development-secret")
    clerk_secret_key: Optional[str] = Field(default=None)

    api_base_url: str = Field(default="http://localhost:8000")
    frontend_url: str = Field(default="http://localhost:4173")
    environment: str = Field(default="development")

    sentry_dsn: Optional[str] = Field(default=None)
    otel_exporter_otlp_endpoint: Optional[str] = Field(default=None)
    service_name: str = Field(default="cba-backend")

    rate_limit_per_minute: int = Field(default=60)
    max_repo_size_mb: int = Field(default=500)
    max_concurrent_jobs_per_user: int = Field(default=3)


@lru_cache()
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""

    return Settings()
