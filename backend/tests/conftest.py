"""
Pytest configuration and shared fixtures for backend tests.

This file provides:
- Database fixtures for testing
- Mock clients for external services (OpenAI, Anthropic, Stripe, S3)
- Test data factories
- Async test support
"""

import asyncio
import json
import os
import sqlite3
import sys
import uuid
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock
from typing import Any, Dict, Generator

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool

# Add backend to path if not already there
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "sqlite:///./backend_test.db")
os.environ.setdefault("CHECKPOINT_DATABASE_URL", "sqlite:///./backend_test.db")
os.environ.setdefault("API_BASE_URL", "http://testserver/api/v1")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_123")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_123")
os.environ.setdefault("STRIPE_PUBLISHABLE_KEY", "pk_test_123")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret-key")
os.environ.setdefault("S3_BUCKET_NAME", "test-bucket")
os.environ.setdefault("S3_REGION", "us-east-1")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from backend.db.session import get_db
from backend.utils.auth import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)

if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = SimpleNamespace(__version__=getattr(bcrypt, "__version__", "0"))

_native_hashpw = bcrypt.hashpw


def _safe_hashpw(password: bytes, salt: bytes) -> bytes:
    try:
        return _native_hashpw(password, salt)
    except ValueError:
        return _native_hashpw(password[:72], salt)


bcrypt.hashpw = _safe_hashpw

sqlite3.register_adapter(dict, lambda value: json.dumps(value))
sqlite3.register_adapter(list, lambda value: json.dumps(value))
sqlite3.register_converter(
    "JSON", lambda value: value.decode("utf-8") if value else None
)

# Mock OpenTelemetry before any imports
trace_module = ModuleType("opentelemetry.trace")
trace_module.get_tracer = lambda name: MagicMock()
opentelemetry_module = ModuleType("opentelemetry")
opentelemetry_module.trace = trace_module
sys.modules.setdefault("opentelemetry.trace", trace_module)
sys.modules.setdefault("opentelemetry", opentelemetry_module)

# Mock agent framework dependencies used by services
agent_framework_module = ModuleType("agent_framework")


class _StubRole:
    ASSISTANT = "assistant"
    USER = "user"


class _StubTextContent:
    def __init__(self, text: str | None = None):
        self.text = text


class _StubChatMessage:
    def __init__(self, *, role: str, contents: list | None = None):
        self.role = role
        self.contents = contents or []

    @property
    def text(self) -> str | None:
        for content in self.contents:
            if hasattr(content, "text"):
                return content.text
        return None


agent_framework_module.ChatAgent = MagicMock()
agent_framework_module.AgentMessage = MagicMock()
agent_framework_module.AgentExecutor = MagicMock()
agent_framework_module.ConcurrentBuilder = MagicMock()
agent_framework_module.SequentialBuilder = MagicMock()
agent_framework_module.WorkflowBuilder = MagicMock()
agent_framework_module.AIFunction = MagicMock()
agent_framework_module.ChatMessage = _StubChatMessage
agent_framework_module.TextContent = _StubTextContent
agent_framework_module.Role = _StubRole
agent_framework_openai = ModuleType("agent_framework.openai")
agent_framework_openai.OpenAIResponsesClient = MagicMock()
agent_framework_anthropic = ModuleType("agent_framework.anthropic")
agent_framework_anthropic.AnthropicClaudeClient = MagicMock()
sys.modules.setdefault("agent_framework", agent_framework_module)
sys.modules.setdefault("agent_framework.openai", agent_framework_openai)
sys.modules.setdefault("agent_framework.anthropic", agent_framework_anthropic)

stripe_module = MagicMock()
sys.modules.setdefault("stripe", stripe_module)

boto3_module = MagicMock()
sys.modules.setdefault("boto3", boto3_module)

botocore_module = ModuleType("botocore")
botocore_exceptions = ModuleType("botocore.exceptions")
botocore_exceptions.ClientError = Exception
sys.modules.setdefault("botocore", botocore_module)
sys.modules.setdefault("botocore.exceptions", botocore_exceptions)


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine using SQLite in-memory."""
    from backend.db.session import Base
    from backend.models import user, job, outline, payment, chapter, deliverable

    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
            "detect_types": sqlite3.PARSE_DECLTYPES,
        },
        poolclass=StaticPool,
        json_serializer=lambda value: json.dumps(value),
        json_deserializer=lambda value: (
            json.loads(value) if isinstance(value, str) else value
        ),
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_db_engine) -> Generator[Session, None, None]:
    """Create a test database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def override_get_db(test_db):
    """Override the get_db dependency for FastAPI testing."""

    def _override_get_db():
        try:
            yield test_db
        finally:
            pass

    return _override_get_db


# ============================================================================
# API Client Fixtures
# ============================================================================


@pytest.fixture
def test_client(override_get_db):
    """Create a test client for the FastAPI application."""
    from backend.main import app
    from backend.db.session import get_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# ============================================================================
# Mock External Service Fixtures
# ============================================================================


@pytest.fixture
def mock_openai_responses_client():
    """Mock OpenAI responses client."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(
        return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))],
            usage=MagicMock(total_tokens=100, prompt_tokens=50, completion_tokens=50),
        )
    )
    return client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic Claude client."""
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock(
        return_value=MagicMock(
            content=[MagicMock(text="Test Claude response")],
            usage=MagicMock(input_tokens=50, output_tokens=50),
        )
    )
    return client


@pytest.fixture
def mock_stripe_client():
    """Mock Stripe client."""
    client = MagicMock()

    # Mock PaymentIntent
    client.PaymentIntent = MagicMock()
    client.PaymentIntent.create = MagicMock(
        return_value=MagicMock(
            id="pi_test_123",
            client_secret="pi_test_123_secret",
            status="requires_payment_method",
        )
    )

    # Mock Webhook
    client.Webhook = MagicMock()
    client.Webhook.construct_event = MagicMock(
        return_value={
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_test_123"}},
        }
    )

    return client


@pytest.fixture
def mock_s3_client():
    """Mock AWS S3 client."""
    client = MagicMock()

    # Mock upload_file
    client.upload_file = MagicMock(return_value=None)

    # Mock generate_presigned_url
    client.generate_presigned_url = MagicMock(
        return_value="https://s3.example.com/test-bucket/test-key"
    )

    # Mock delete_object
    client.delete_object = MagicMock(return_value={"DeleteMarker": True})

    return client


@pytest.fixture
def mock_git_repo():
    """Mock GitPython repository."""
    repo = MagicMock()
    repo.git = MagicMock()
    repo.git.checkout = MagicMock()
    repo.head = MagicMock()
    repo.head.commit = MagicMock()
    repo.head.commit.hexsha = "abc123def456"
    return repo


# ============================================================================
# Test Data Factories
# ============================================================================


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "hashed_password": "hashed_password_123",
        "subscription_tier": "free",
        "credits_remaining": 0,
    }


@pytest.fixture
def sample_job_data() -> Dict[str, Any]:
    """Sample job data for testing."""
    return {
        "repo_url": "https://github.com/user/test-repo",
        "repo_name": "test-repo",
        "repo_owner": "user",
        "git_ref": "main",
        "depth_tier": "standard",
        "status": "pending",
        "progress_percentage": 0.0,
        "price_paid_cents": 4900,
    }


@pytest.fixture
def sample_outline_data() -> Dict[str, Any]:
    """Sample outline data for testing."""
    return {
        "chapters": [
            {
                "number": 1,
                "title": "Introduction",
                "description": "Overview of the codebase",
                "files_covered": ["README.md", "main.py"],
                "topics": ["architecture", "setup"],
                "estimated_duration_minutes": 15,
                "learning_objectives": ["Understand project structure"],
            },
            {
                "number": 2,
                "title": "Core Modules",
                "description": "Deep dive into core functionality",
                "files_covered": ["core/engine.py", "core/utils.py"],
                "topics": ["core logic", "utilities"],
                "estimated_duration_minutes": 25,
                "learning_objectives": ["Learn core patterns"],
            },
        ],
        "total_estimated_duration_minutes": 40,
        "total_chapters": 2,
    }


@pytest.fixture
def sample_chapter_data() -> Dict[str, Any]:
    """Sample chapter data for testing."""
    return {
        "chapter_number": 1,
        "title": "Introduction",
        "description": "Overview of the codebase",
        "files_covered": ["README.md", "main.py"],
        "topics_covered": ["architecture", "setup"],
        "status": "pending",
        "script_text": None,
        "audio_url": None,
        "audio_duration_seconds": None,
    }


@pytest.fixture
def sample_analysis_result() -> Dict[str, Any]:
    """Sample repository analysis result."""
    return {
        "repository_url": "https://github.com/user/test-repo",
        "git_ref": "main",
        "commit_hash": "abc123",
        "analysis_mode": "docling",
        "structure": {
            "file_count": 42,
            "total_size_bytes": 1024000,
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React"],
        },
        "parsed": {
            "files": [],
            "summary": {
                "total_files": 42,
                "successfully_parsed": 40,
                "failed_to_parse": 2,
                "parse_success_rate": 95.2,
            },
            "entry_points": ["main.py", "app.py"],
            "dependency_graph": {},
        },
    }


# ============================================================================
# Agent Framework Fixtures
# ============================================================================


@pytest.fixture
def mock_agent():
    """Mock Microsoft Agent Framework Agent."""
    agent = MagicMock()
    agent.run = AsyncMock(
        return_value=MagicMock(
            result="Agent execution result", usage=MagicMock(total_tokens=100)
        )
    )
    return agent


@pytest.fixture
def mock_workflow():
    """Mock audiobook workflow."""
    workflow = MagicMock()
    workflow.execute = AsyncMock(
        return_value={"status": "completed", "job_id": "test-job-1"}
    )
    workflow.continue_after_approval = AsyncMock(
        return_value={"status": "completed", "job_id": "test-job-1"}
    )
    return workflow


# ============================================================================
# Helper Functions
# ============================================================================


@pytest.fixture
def create_user(test_db):
    """Factory fixture for creating test users."""
    from backend.models.user import User

    def _create_user(password: str = "SecurePass123!", **kwargs):
        hashed = kwargs.pop(
            "hashed_password",
            get_password_hash(password),
        )
        user_data = {
            "email": kwargs.pop("email", f"user-{uuid.uuid4().hex}@example.com"),
            "name": "Test User",
            "hashed_password": hashed,
            "subscription_tier": "free",
            "subscription_status": "active",
            "credits_remaining": 0,
        }
        user_data.update(kwargs)

        user = User(**user_data)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user

    return _create_user


@pytest.fixture
def auth_tokens(create_user):
    """Return access and refresh tokens for a test user."""

    def _auth_tokens(user=None, **kwargs):
        user_obj = user or create_user(**kwargs)
        payload = {"sub": str(user_obj.id)}
        access = create_access_token(payload)
        refresh = create_refresh_token(payload)
        return {"access": access, "refresh": refresh, "user": user_obj}

    return _auth_tokens


@pytest.fixture
def auth_header(auth_tokens):
    """Return authorization header for a test user."""

    def _auth_header(user=None, **kwargs):
        tokens = auth_tokens(user=user, **kwargs)
        header = {"Authorization": f"Bearer {tokens['access']}"}
        return header, tokens["user"]

    return _auth_header


@pytest.fixture
def create_job(test_db, create_user):
    """Factory fixture for creating test jobs."""
    from backend.models.job import Job

    def _create_job(user=None, **kwargs):
        if user is None:
            user = create_user()

        job_data = {
            "user_id": user.id,
            "repo_url": "https://github.com/user/test-repo",
            "repo_name": "test-repo",
            "repo_owner": "user",
            "git_ref": "main",
            "depth_tier": "standard",
            "status": "pending",
            "price_paid_cents": 4900,
        }
        job_data.update(kwargs)

        job = Job(**job_data)
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)
        return job

    return _create_job


# ============================================================================
# Event Loop Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Allow JSONB columns to compile under SQLite for tests
@compiles(JSONB, "sqlite")
def compile_jsonb(element, compiler, **kwargs):
    return "JSON"


@compiles(ARRAY, "sqlite")
def compile_array(element, compiler, **kwargs):
    return "JSON"
