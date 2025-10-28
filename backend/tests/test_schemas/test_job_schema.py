"""Tests for job schema validation."""

import pytest
import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

from backend.api.schemas.job import (
    JobCreate,
    JobResponse,
    JobListResponse,
    JobEstimate,
    JobEstimateRequest,
    DepthTier,
    JobStatus,
    calculate_price_for_tier,
)


class TestJobCreate:
    """Tests for JobCreate schema."""

    def test_valid_job_create_https(self):
        """Test creating job with valid HTTPS GitHub URL."""
        data = {
            "repo_url": "https://github.com/owner/repo",
            "depth_tier": "standard",
        }
        job = JobCreate(**data)
        assert job.repo_url == "https://github.com/owner/repo"
        assert job.depth_tier == DepthTier.STANDARD
        assert job.git_ref == "main"

    def test_valid_job_create_ssh(self):
        """Test creating job with valid SSH GitHub URL."""
        data = {
            "repo_url": "git@github.com:owner/repo.git",
            "depth_tier": "survey",
        }
        job = JobCreate(**data)
        assert job.repo_url == "git@github.com:owner/repo.git"
        assert job.depth_tier == DepthTier.SURVEY

    def test_job_create_custom_git_ref(self):
        """Test creating job with custom git ref."""
        data = {
            "repo_url": "https://github.com/owner/repo",
            "depth_tier": "comprehensive",
            "git_ref": "develop",
        }
        job = JobCreate(**data)
        assert job.git_ref == "develop"

    def test_job_create_invalid_github_url(self):
        """Test that non-GitHub URL is rejected."""
        data = {
            "repo_url": "https://gitlab.com/owner/repo",
            "depth_tier": "standard",
        }
        with pytest.raises(ValidationError) as exc_info:
            JobCreate(**data)
        assert "GitHub URL" in str(exc_info.value)

    def test_job_create_invalid_url_format(self):
        """Test that invalid URL format is rejected."""
        data = {
            "repo_url": "not-a-url",
            "depth_tier": "standard",
        }
        with pytest.raises(ValidationError):
            JobCreate(**data)

    def test_job_create_invalid_git_ref_empty(self):
        """Test that empty git ref is rejected."""
        data = {
            "repo_url": "https://github.com/owner/repo",
            "depth_tier": "standard",
            "git_ref": "",
        }
        with pytest.raises(ValidationError) as exc_info:
            JobCreate(**data)
        assert "empty" in str(exc_info.value).lower()

    def test_job_create_invalid_git_ref_too_long(self):
        """Test that overly long git ref is rejected."""
        data = {
            "repo_url": "https://github.com/owner/repo",
            "depth_tier": "standard",
            "git_ref": "a" * 256,
        }
        with pytest.raises(ValidationError) as exc_info:
            JobCreate(**data)
        assert "255" in str(exc_info.value)

    def test_job_create_invalid_git_ref_characters(self):
        """Test that git ref with invalid characters is rejected."""
        data = {
            "repo_url": "https://github.com/owner/repo",
            "depth_tier": "standard",
            "git_ref": "feature/test@#$%",
        }
        with pytest.raises(ValidationError) as exc_info:
            JobCreate(**data)
        assert "invalid characters" in str(exc_info.value).lower()

    def test_job_create_valid_git_ref_with_slashes(self):
        """Test that git ref with slashes is accepted."""
        data = {
            "repo_url": "https://github.com/owner/repo",
            "depth_tier": "standard",
            "git_ref": "feature/my-feature",
        }
        job = JobCreate(**data)
        assert job.git_ref == "feature/my-feature"


class TestJobResponse:
    """Tests for JobResponse schema."""

    def test_valid_job_response(self):
        """Test creating job response with valid data."""
        response_dict = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "repo_url": "https://github.com/owner/repo",
            "repo_name": "repo",
            "repo_owner": "owner",
            "git_ref": "main",
            "depth_tier": "standard",
            "status": "pending",
            "current_stage": None,
            "progress_percentage": Decimal("0.0"),
            "error_message": None,
            "estimated_duration_minutes": 480,
            "estimated_chapters": 10,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "chapters": [],
            "deliverables": [],
        }
        response = JobResponse(**response_dict)
        assert response.repo_url == "https://github.com/owner/repo"
        assert response.status == "pending"


class TestJobEstimate:
    """Tests for JobEstimate schema and pricing."""

    def test_calculate_price_survey(self):
        """Test price calculation for survey tier."""
        price = calculate_price_for_tier(DepthTier.SURVEY)
        assert price == 1900  # $19

    def test_calculate_price_standard(self):
        """Test price calculation for standard tier."""
        price = calculate_price_for_tier(DepthTier.STANDARD)
        assert price == 4900  # $49

    def test_calculate_price_comprehensive(self):
        """Test price calculation for comprehensive tier."""
        price = calculate_price_for_tier(DepthTier.COMPREHENSIVE)
        assert price == 9900  # $99

    def test_job_estimate_from_tier_survey(self):
        """Test creating estimate for survey tier."""
        estimate = JobEstimate.from_tier(DepthTier.SURVEY)
        assert estimate.estimated_cost_cents == 1900
        assert estimate.estimated_duration_minutes == 180
        assert estimate.estimated_chapters == 5
        assert estimate.depth_tier == "survey"

    def test_job_estimate_from_tier_standard(self):
        """Test creating estimate for standard tier."""
        estimate = JobEstimate.from_tier(DepthTier.STANDARD)
        assert estimate.estimated_cost_cents == 4900
        assert estimate.estimated_duration_minutes == 480
        assert estimate.estimated_chapters == 10
        assert estimate.depth_tier == "standard"

    def test_job_estimate_from_tier_comprehensive(self):
        """Test creating estimate for comprehensive tier."""
        estimate = JobEstimate.from_tier(DepthTier.COMPREHENSIVE)
        assert estimate.estimated_cost_cents == 9900
        assert estimate.estimated_duration_minutes == 1200
        assert estimate.estimated_chapters == 20
        assert estimate.depth_tier == "comprehensive"

    def test_job_estimate_cost_validation_negative(self):
        """Test that negative cost is rejected."""
        with pytest.raises(ValidationError):
            JobEstimate(
                estimated_cost_cents=-100,
                estimated_duration_minutes=120,
                estimated_chapters=5,
                depth_tier="survey",
            )

    def test_job_estimate_cost_validation_too_high(self):
        """Test that excessive cost is rejected."""
        with pytest.raises(ValidationError):
            JobEstimate(
                estimated_cost_cents=2000000,  # $20,000
                estimated_duration_minutes=120,
                estimated_chapters=5,
                depth_tier="survey",
            )


class TestEnums:
    """Tests for enum values."""

    def test_depth_tier_enum(self):
        """Test depth tier enum values."""
        assert DepthTier.SURVEY == "survey"
        assert DepthTier.STANDARD == "standard"
        assert DepthTier.COMPREHENSIVE == "comprehensive"

    def test_job_status_enum(self):
        """Test job status enum values."""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.ANALYZING == "analyzing"
        assert JobStatus.SCRIPTING == "scripting"
        assert JobStatus.SYNTHESIZING == "synthesizing"
        assert JobStatus.POST_PROCESSING == "post_processing"
        assert JobStatus.COMPLETED == "completed"
        assert JobStatus.FAILED == "failed"
