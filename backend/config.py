"""Application configuration helpers."""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration with sensible defaults for local development."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    database_url: str = Field(default="sqlite:///./backend_dev.db")
    checkpoint_database_url: str = Field(default="sqlite:///./backend_dev.db")

    azure_openai_endpoint: str = Field(default="https://example.openai.azure.com/")
    azure_openai_api_key: str = Field(default="dev-azure-openai-key")
    azure_openai_deployment_name: str = Field(default="gpt-4o")
    azure_openai_api_version: str = Field(default="2024-10-21")

    anthropic_api_key: str = Field(default="dev-anthropic-key")
    openai_api_key: Optional[str] = Field(default=None)

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
    frontend_url: str = Field(default="http://localhost:5173")
    allowed_cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
    )
    environment: str = Field(default="development")

    sentry_dsn: Optional[str] = Field(default=None)
    otel_exporter_otlp_endpoint: Optional[str] = Field(default=None)
    service_name: str = Field(default="cba-backend")

    rate_limit_per_minute: int = Field(default=60)
    content_security_policy: str = Field(
        default=(
            "default-src 'none'; "
            "base-uri 'self'; "
            "connect-src 'self'; "
            "form-action 'self'; "
            "img-src 'self' data:; "
            "media-src 'self'; "
            "script-src 'none'; "
            "style-src 'self' 'unsafe-inline'; "
            "frame-ancestors 'none'"
        )
    )
    referrer_policy: str = Field(default="no-referrer")
    max_repo_size_mb: int = Field(default=500)
    max_concurrent_jobs_per_user: int = Field(default=3)


@lru_cache()
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""

    return Settings()
