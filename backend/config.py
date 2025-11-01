"""Application configuration helpers."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this config file is located
_CONFIG_DIR = Path(__file__).resolve().parent
_ENV_FILE = _CONFIG_DIR / ".env"


class Settings(BaseSettings):
    """Runtime configuration with sensible defaults for local development."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE), case_sensitive=False, extra="ignore"
    )

    database_url: str = Field(..., min_length=1)
    checkpoint_database_url: str = Field(..., min_length=1)

    anthropic_api_key: str = Field(..., min_length=1)
    openai_api_key: Optional[str] = Field(default=None)
    openai_responses_model: str = Field(default="gpt-4o-mini")
    openai_base_url: Optional[str] = Field(default=None)

    stripe_secret_key: str = Field(..., min_length=1)
    stripe_webhook_secret: str = Field(..., min_length=1)
    stripe_publishable_key: str = Field(..., min_length=1)

    aws_access_key_id: str = Field(..., min_length=1)
    aws_secret_access_key: str = Field(..., min_length=1)
    s3_bucket_name: str = Field(..., min_length=1)
    s3_region: str = Field(..., min_length=1)

    jwt_secret: str = Field(..., min_length=1)
    clerk_secret_key: Optional[str] = Field(default=None)

    api_base_url: str = Field(..., min_length=1)
    frontend_url: Optional[str] = Field(default=None)
    environment: str = Field(default="development")

    sentry_dsn: Optional[str] = Field(default=None)
    otel_exporter_otlp_endpoint: Optional[str] = Field(default=None)
    service_name: str = Field(default="cba-backend")
    billing_service_url: Optional[str] = Field(default=None)
    observability_ingest_url: Optional[str] = Field(default=None)

    rate_limit_per_minute: int = Field(default=60)
    rate_limit_storage_uri: str = Field(default="memory://")
    rate_limit_storage_options: dict[str, str] = Field(default_factory=dict)
    max_repo_size_mb: int = Field(default=500)
    max_concurrent_jobs_per_user: int = Field(default=3)
    redis_url: str = Field(..., min_length=1)
    log_level: str = Field(default="INFO")
    tool_registry_check_interval_seconds: int = Field(default=900, ge=60)

    @model_validator(mode="after")
    def ensure_postgres(cls, values: "Settings") -> "Settings":
        environment = values.environment.lower()
        for field_name in ("database_url", "checkpoint_database_url"):
            url_value = getattr(values, field_name)
            if environment != "test" and url_value.startswith("sqlite"):
                msg = f"{field_name} must point to PostgreSQL; SQLite is not supported"
                raise ValueError(msg)
        return values


@lru_cache()
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""

    return Settings()
