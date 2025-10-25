"""
Tests for database models.

Tests for:
- User model
- Job model
- Chapter model
- Outline model
- Payment model
- Deliverable model
- Usage Log model
- Workflow Checkpoint model
"""

import pytest
from datetime import datetime
import uuid


@pytest.mark.models
@pytest.mark.unit
class TestUserModel:
    """Test User model."""

    def test_create_user(self, test_db):
        """Test creating a user."""
        from backend.models.user import User

        user = User(
            email="test@example.com",
            name="Test User",
            hashed_password="hashed_password_123",
            subscription_tier="free"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.subscription_tier == "free"

    def test_user_email_unique(self, test_db):
        """Test user email must be unique."""
        from backend.models.user import User
        from sqlalchemy.exc import IntegrityError

        user1 = User(
            email="duplicate@example.com",
            name="User 1",
            hashed_password="pass1"
        )
        test_db.add(user1)
        test_db.commit()

        user2 = User(
            email="duplicate@example.com",
            name="User 2",
            hashed_password="pass2"
        )
        test_db.add(user2)

        # Should fail due to unique constraint
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_user_subscription_tiers(self, test_db):
        """Test different subscription tiers."""
        from backend.models.user import User

        tiers = ["free", "professional", "team", "enterprise"]

        for tier in tiers:
            user = User(
                email=f"{tier}@example.com",
                name=f"{tier.title()} User",
                hashed_password="pass",
                subscription_tier=tier
            )
            test_db.add(user)

        test_db.commit()

        # All should be created successfully
        users = test_db.query(User).all()
        assert len(users) >= len(tiers)


@pytest.mark.models
@pytest.mark.unit
class TestJobModel:
    """Test Job model."""

    def test_create_job(self, test_db, create_user):
        """Test creating a job."""
        from backend.models.job import Job

        user = create_user()

        job = Job(
            user_id=user.id,
            repo_url="https://github.com/user/repo",
            repo_name="repo",
            repo_owner="user",
            git_ref="main",
            depth_tier="standard",
            status="pending"
        )

        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)

        assert job.id is not None
        assert job.user_id == user.id
        assert job.status == "pending"

    def test_job_status_transitions(self, test_db, create_job):
        """Test job status can transition through states."""
        from backend.models.job import JobStatus

        job = create_job(status="pending")

        # Transition through statuses
        statuses = [
            "analyzing",
            "waiting_approval",
            "scripting",
            "synthesizing",
            "post_processing",
            "completed"
        ]

        for status in statuses:
            job.status = status
            test_db.commit()
            test_db.refresh(job)
            assert job.status == status

    def test_job_progress_tracking(self, test_db, create_job):
        """Test job progress percentage tracking."""
        job = create_job()

        # Update progress
        job.progress_percentage = 0.0
        test_db.commit()

        job.progress_percentage = 50.5
        test_db.commit()

        job.progress_percentage = 100.0
        test_db.commit()

        test_db.refresh(job)
        assert job.progress_percentage == 100.0

    def test_job_cost_tracking(self, test_db, create_job):
        """Test job cost fields."""
        job = create_job()

        job.price_paid_cents = 4900
        job.llm_cost_cents = 250
        job.tts_cost_cents = 150

        test_db.commit()
        test_db.refresh(job)

        assert job.price_paid_cents == 4900
        assert job.llm_cost_cents == 250
        assert job.tts_cost_cents == 150

    def test_job_timestamps(self, test_db, create_job):
        """Test job has creation and update timestamps."""
        job = create_job()

        assert job.created_at is not None
        assert job.updated_at is not None
        assert isinstance(job.created_at, datetime)


@pytest.mark.models
@pytest.mark.unit
class TestChapterModel:
    """Test Chapter model."""

    def test_create_chapter(self, test_db, create_job):
        """Test creating a chapter."""
        from backend.models.chapter import Chapter

        job = create_job()

        chapter = Chapter(
            job_id=job.id,
            chapter_number=1,
            title="Introduction",
            description="Overview of the project",
            files_covered=["README.md", "main.py"],
            topics_covered=["setup", "architecture"],
            status="pending"
        )

        test_db.add(chapter)
        test_db.commit()
        test_db.refresh(chapter)

        assert chapter.id is not None
        assert chapter.chapter_number == 1

    def test_chapter_audio_metadata(self, test_db, create_job):
        """Test chapter audio metadata fields."""
        from backend.models.chapter import Chapter

        job = create_job()

        chapter = Chapter(
            job_id=job.id,
            chapter_number=1,
            title="Test Chapter",
            audio_url="https://s3.example.com/audio.mp3",
            audio_duration_seconds=1800
        )

        test_db.add(chapter)
        test_db.commit()
        test_db.refresh(chapter)

        assert chapter.audio_url == "https://s3.example.com/audio.mp3"
        assert chapter.audio_duration_seconds == 1800

    def test_chapter_ordering(self, test_db, create_job):
        """Test chapters maintain proper ordering."""
        from backend.models.chapter import Chapter

        job = create_job()

        # Create chapters in reverse order
        for i in [3, 1, 2]:
            chapter = Chapter(
                job_id=job.id,
                chapter_number=i,
                title=f"Chapter {i}"
            )
            test_db.add(chapter)

        test_db.commit()

        # Query chapters ordered by chapter_number
        chapters = test_db.query(Chapter).filter_by(
            job_id=job.id
        ).order_by(Chapter.chapter_number).all()

        assert len(chapters) == 3
        assert chapters[0].chapter_number == 1
        assert chapters[1].chapter_number == 2
        assert chapters[2].chapter_number == 3


@pytest.mark.models
@pytest.mark.unit
class TestOutlineModel:
    """Test Outline model."""

    def test_create_outline(self, test_db, create_job, sample_outline_data):
        """Test creating an outline."""
        from backend.models.outline import Outline

        job = create_job()

        outline = Outline(
            job_id=job.id,
            outline_data=sample_outline_data,
            is_approved=False
        )

        test_db.add(outline)
        test_db.commit()
        test_db.refresh(outline)

        assert outline.id is not None
        assert outline.is_approved is False

    def test_outline_approval(self, test_db, create_job, sample_outline_data):
        """Test outline approval workflow."""
        from backend.models.outline import Outline

        job = create_job()

        outline = Outline(
            job_id=job.id,
            outline_data=sample_outline_data,
            is_approved=False
        )

        test_db.add(outline)
        test_db.commit()

        # Approve outline
        outline.is_approved = True
        test_db.commit()
        test_db.refresh(outline)

        assert outline.is_approved is True


@pytest.mark.models
@pytest.mark.unit
class TestPaymentModel:
    """Test Payment model."""

    def test_create_payment(self, test_db, create_user):
        """Test creating a payment record."""
        from backend.models.payment import Payment

        user = create_user()

        payment = Payment(
            user_id=user.id,
            stripe_payment_intent_id="pi_test_123",
            amount_cents=4900,
            status="succeeded"
        )

        test_db.add(payment)
        test_db.commit()
        test_db.refresh(payment)

        assert payment.id is not None
        assert payment.amount_cents == 4900

    def test_payment_status_tracking(self, test_db, create_user):
        """Test payment status tracking."""
        from backend.models.payment import Payment

        user = create_user()

        payment = Payment(
            user_id=user.id,
            stripe_payment_intent_id="pi_test_456",
            amount_cents=4900,
            status="pending"
        )

        test_db.add(payment)
        test_db.commit()

        # Update status
        payment.status = "succeeded"
        test_db.commit()
        test_db.refresh(payment)

        assert payment.status == "succeeded"


@pytest.mark.models
@pytest.mark.unit
class TestUsageLogModel:
    """Test Usage Log model."""

    def test_create_usage_log(self, test_db, create_job):
        """Test creating usage log entry."""
        from backend.models.usage_log import UsageLog

        job = create_job()

        log = UsageLog(
            job_id=job.id,
            service_type="azure_openai",
            tokens_used=1000,
            cost_cents=25
        )

        test_db.add(log)
        test_db.commit()
        test_db.refresh(log)

        assert log.id is not None
        assert log.tokens_used == 1000

    def test_track_multiple_services(self, test_db, create_job):
        """Test tracking usage for different services."""
        from backend.models.usage_log import UsageLog

        job = create_job()

        services = [
            ("azure_openai", 1000, 25),
            ("anthropic", 1500, 30),
            ("elevenlabs", 0, 100)
        ]

        for service_type, tokens, cost in services:
            log = UsageLog(
                job_id=job.id,
                service_type=service_type,
                tokens_used=tokens,
                cost_cents=cost
            )
            test_db.add(log)

        test_db.commit()

        # Query logs for job
        logs = test_db.query(UsageLog).filter_by(job_id=job.id).all()
        assert len(logs) == 3

        # Calculate total cost
        total_cost = sum(log.cost_cents for log in logs)
        assert total_cost == 155


@pytest.mark.models
@pytest.mark.unit
class TestWorkflowCheckpointModel:
    """Test Workflow Checkpoint model."""

    def test_create_checkpoint(self, test_db, create_job):
        """Test creating workflow checkpoint."""
        from backend.models.workflow_checkpoint import WorkflowCheckpoint

        job = create_job()

        checkpoint = WorkflowCheckpoint(
            job_id=job.id,
            stage="outline_generation",
            checkpoint_data={"analysis": "complete"}
        )

        test_db.add(checkpoint)
        test_db.commit()
        test_db.refresh(checkpoint)

        assert checkpoint.id is not None
        assert checkpoint.stage == "outline_generation"

    def test_multiple_checkpoints_per_job(self, test_db, create_job):
        """Test job can have multiple checkpoints."""
        from backend.models.workflow_checkpoint import WorkflowCheckpoint

        job = create_job()

        stages = ["analysis", "outline", "scripting", "audio", "post_process"]

        for stage in stages:
            checkpoint = WorkflowCheckpoint(
                job_id=job.id,
                stage=stage,
                checkpoint_data={"stage": stage}
            )
            test_db.add(checkpoint)

        test_db.commit()

        # Query checkpoints
        checkpoints = test_db.query(WorkflowCheckpoint).filter_by(
            job_id=job.id
        ).all()

        assert len(checkpoints) == 5


@pytest.mark.models
@pytest.mark.integration
class TestModelRelationships:
    """Test relationships between models."""

    @pytest.mark.skip(reason="Relationships commented out in models")
    def test_user_jobs_relationship(self, test_db, create_user, create_job):
        """Test user can have multiple jobs."""
        user = create_user()

        job1 = create_job(user=user)
        job2 = create_job(user=user)

        # Query user with jobs
        assert len(user.jobs) == 2

    @pytest.mark.skip(reason="Relationships commented out in models")
    def test_job_chapters_relationship(self, test_db, create_job):
        """Test job can have multiple chapters."""
        from backend.models.chapter import Chapter

        job = create_job()

        for i in range(3):
            chapter = Chapter(
                job_id=job.id,
                chapter_number=i + 1,
                title=f"Chapter {i + 1}"
            )
            test_db.add(chapter)

        test_db.commit()

        # Query job with chapters
        assert len(job.chapters) == 3

    @pytest.mark.skip(reason="Relationships commented out in models")
    def test_cascade_delete(self, test_db, create_user, create_job):
        """Test cascade delete of related records."""
        from backend.models.chapter import Chapter

        user = create_user()
        job = create_job(user=user)

        # Add chapters
        for i in range(2):
            chapter = Chapter(
                job_id=job.id,
                chapter_number=i + 1,
                title=f"Chapter {i + 1}"
            )
            test_db.add(chapter)

        test_db.commit()

        # Delete job
        test_db.delete(job)
        test_db.commit()

        # Chapters should be deleted too (if cascade is configured)
        chapters = test_db.query(Chapter).filter_by(job_id=job.id).all()
        assert len(chapters) == 0
