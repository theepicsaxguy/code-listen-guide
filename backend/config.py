"""
Configuration management using Pydantic Settings.

TODO: Implementation steps:
1. Define Settings class with all environment variables
2. Add validation for required fields
3. Implement get_settings() function with caching
4. Add environment-specific configurations (dev, staging, prod)
5. Validate API keys on startup
6. Add configuration for rate limiting
7. Configure CORS origins
8. Set up logging configuration
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    TODO:
    - Add all environment variables from .env.example
    - Implement validators for URLs and API keys
    - Add computed properties for derived settings
    - Configure different settings for dev/staging/prod
    """

    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    checkpoint_database_url: str = Field(..., env="CHECKPOINT_DATABASE_URL")
    azure_openai_api_version: str = Field(default="2024-10-21", env="AZURE_OPENAI_API_VERSION")

    # LLM Providers
    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    azure_openai_deployment_name: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT_NAME")
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    elevenlabs_api_key: Optional[str] = Field(None, env="ELEVENLABS_API_KEY")

    # Stripe
    stripe_secret_key: str = Field(..., env="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(..., env="STRIPE_WEBHOOK_SECRET")
    stripe_publishable_key: str = Field(..., env="STRIPE_PUBLISHABLE_KEY")

    # AWS S3
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    s3_bucket_name: str = Field(..., env="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")

    # Authentication
    jwt_secret: str = Field(..., env="JWT_SECRET")
    clerk_secret_key: Optional[str] = Field(None, env="CLERK_SECRET_KEY")

    # Application
    api_base_url: str = Field(..., env="API_BASE_URL")
    frontend_url: str = Field(..., env="FRONTEND_URL")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Observability
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")
    otel_exporter_otlp_endpoint: Optional[str] = Field(None, env="OTEL_EXPORTER_OTLP_ENDPOINT")
    service_name: str = Field(default="cba-backend", env="OTEL_SERVICE_NAME")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")

    # Processing Limits
    max_repo_size_mb: int = Field(default=500, env="MAX_REPO_SIZE_MB")
    max_concurrent_jobs_per_user: int = Field(default=3, env="MAX_CONCURRENT_JOBS_PER_USER")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    TODO:
    - Add error handling for missing required env vars
    - Log configuration warnings
    - Validate configuration on startup
    """

    return Settings()
