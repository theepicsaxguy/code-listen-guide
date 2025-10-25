"""
Pytest configuration and shared fixtures for backend tests.

This file provides:
- Database fixtures for testing
- Mock clients for external services (Azure OpenAI, Anthropic, ElevenLabs, Stripe, S3)
- Test data factories
- Async test support
"""

import asyncio
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, Mock
from typing import Dict, Any, Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Add backend to path if not already there
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Mock OpenTelemetry before any imports
trace_module = ModuleType("opentelemetry.trace")
trace_module.get_tracer = lambda name: MagicMock()
opentelemetry_module = ModuleType("opentelemetry")
opentelemetry_module.trace = trace_module
sys.modules.setdefault("opentelemetry.trace", trace_module)
sys.modules.setdefault("opentelemetry", opentelemetry_module)


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine using SQLite in-memory."""
    from backend.models import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
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
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
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
    from backend.db.session import get_db

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
def mock_azure_openai_client():
    """Mock Azure OpenAI client."""
    client = MagicMock()
    client.chat = MagicMock()
    client.chat.completions = MagicMock()
    client.chat.completions.create = AsyncMock(return_value=MagicMock(
        choices=[MagicMock(message=MagicMock(content="Test response"))],
        usage=MagicMock(total_tokens=100, prompt_tokens=50, completion_tokens=50)
    ))
    return client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic Claude client."""
    client = MagicMock()
    client.messages = MagicMock()
    client.messages.create = AsyncMock(return_value=MagicMock(
        content=[MagicMock(text="Test Claude response")],
        usage=MagicMock(input_tokens=50, output_tokens=50)
    ))
    return client


@pytest.fixture
def mock_elevenlabs_client():
    """Mock ElevenLabs TTS client."""
    client = MagicMock()
    client.generate = AsyncMock(return_value=b"fake_audio_data")
    return client


@pytest.fixture
def mock_stripe_client():
    """Mock Stripe client."""
    client = MagicMock()

    # Mock PaymentIntent
    client.PaymentIntent = MagicMock()
    client.PaymentIntent.create = MagicMock(return_value=MagicMock(
        id="pi_test_123",
        client_secret="pi_test_123_secret",
        status="requires_payment_method"
    ))

    # Mock Webhook
    client.Webhook = MagicMock()
    client.Webhook.construct_event = MagicMock(return_value={
        "type": "payment_intent.succeeded",
        "data": {"object": {"id": "pi_test_123"}}
    })

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
        "credits_remaining": 0
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
        "price_paid_cents": 4900
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
                "topics_covered": ["architecture", "setup"],
                "estimated_duration_minutes": 15,
                "learning_objectives": ["Understand project structure"]
            },
            {
                "number": 2,
                "title": "Core Modules",
                "description": "Deep dive into core functionality",
                "files_covered": ["core/engine.py", "core/utils.py"],
                "topics_covered": ["core logic", "utilities"],
                "estimated_duration_minutes": 25,
                "learning_objectives": ["Learn core patterns"]
            }
        ],
        "total_estimated_duration_minutes": 40,
        "total_chapters": 2
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
        "audio_duration_seconds": None
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
            "frameworks": ["FastAPI", "React"]
        },
        "parsed": {
            "files": [],
            "summary": {
                "total_files": 42,
                "successfully_parsed": 40,
                "failed_to_parse": 2,
                "parse_success_rate": 95.2
            },
            "entry_points": ["main.py", "app.py"],
            "dependency_graph": {}
        }
    }


# ============================================================================
# Agent Framework Fixtures
# ============================================================================

@pytest.fixture
def mock_agent():
    """Mock Microsoft Agent Framework Agent."""
    agent = MagicMock()
    agent.run = AsyncMock(return_value=MagicMock(
        result="Agent execution result",
        usage=MagicMock(total_tokens=100)
    ))
    return agent


@pytest.fixture
def mock_workflow():
    """Mock audiobook workflow."""
    workflow = MagicMock()
    workflow.execute = AsyncMock(return_value={
        "status": "completed",
        "job_id": "test-job-1"
    })
    workflow.continue_after_approval = AsyncMock(return_value={
        "status": "completed",
        "job_id": "test-job-1"
    })
    return workflow


# ============================================================================
# Helper Functions
# ============================================================================

@pytest.fixture
def create_user(test_db):
    """Factory fixture for creating test users."""
    from backend.models.user import User

    def _create_user(**kwargs):
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "hashed_password",
            "subscription_tier": "free",
            "credits_remaining": 0
        }
        user_data.update(kwargs)

        user = User(**user_data)
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        return user

    return _create_user


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
            "price_paid_cents": 4900
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
