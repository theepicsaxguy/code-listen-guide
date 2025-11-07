"""Tests for user schema validation."""

import pytest
import uuid
from datetime import datetime
from pydantic import ValidationError

from backend.api.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    SubscriptionTier,
    SubscriptionStatus,
    TokenResponse,
    TokenRefreshRequest,
)


class TestUserCreate:
    """Tests for UserCreate schema."""

    def test_valid_user_create(self):
        """Test creating user with valid data."""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "Test User",
        }
        user = UserCreate(**data)
        assert user.email == "test@example.com"
        assert user.password == "SecurePass123"
        assert user.name == "Test User"

    def test_user_create_without_name(self):
        """Test creating user without optional name field."""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
        }
        user = UserCreate(**data)
        assert user.email == "test@example.com"
        assert user.name is None

    def test_user_create_invalid_email(self):
        """Test that invalid email is rejected."""
        data = {
            "email": "not-an-email",
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "email" in str(exc_info.value).lower()

    def test_user_create_weak_password_too_short(self):
        """Test that short password is rejected."""
        data = {
            "email": "test@example.com",
            "password": "weak",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "8 characters" in str(exc_info.value)

    def test_user_create_weak_password_no_uppercase(self):
        """Test that password without uppercase is rejected."""
        data = {
            "email": "test@example.com",
            "password": "securepass123",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "uppercase" in str(exc_info.value).lower()

    def test_user_create_weak_password_no_lowercase(self):
        """Test that password without lowercase is rejected."""
        data = {
            "email": "test@example.com",
            "password": "SECUREPASS123",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "lowercase" in str(exc_info.value).lower()

    def test_user_create_weak_password_no_number(self):
        """Test that password without number is rejected."""
        data = {
            "email": "test@example.com",
            "password": "SecurePass",
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**data)
        assert "number" in str(exc_info.value).lower()

    def test_user_create_name_normalization(self):
        """Test that name is trimmed."""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "  Test User  ",
        }
        user = UserCreate(**data)
        assert user.name == "Test User"

    def test_user_create_empty_name_becomes_none(self):
        """Test that empty string name becomes None."""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "name": "   ",
        }
        user = UserCreate(**data)
        assert user.name is None


class TestUserLogin:
    """Tests for UserLogin schema."""

    def test_valid_user_login(self):
        """Test creating login with valid credentials."""
        data = {
            "email": "test@example.com",
            "password": "mypassword",
        }
        login = UserLogin(**data)
        assert login.email == "test@example.com"
        assert login.password == "mypassword"

    def test_user_login_invalid_email(self):
        """Test that invalid email is rejected."""
        data = {
            "email": "not-an-email",
            "password": "mypassword",
        }
        with pytest.raises(ValidationError):
            UserLogin(**data)


class TestUserResponse:
    """Tests for UserResponse schema."""

    def test_valid_user_response(self):
        """Test creating user response with valid data."""
        response_dict = {
            "id": uuid.uuid4(),
            "email": "test@example.com",
            "name": "Test User",
            "is_admin": False,
            "subscription_tier": "free",
            "subscription_status": "active",
            "credits_remaining": 100,
            "created_at": datetime.utcnow(),
        }
        response = UserResponse(**response_dict)
        assert response.email == "test@example.com"
        assert response.subscription_tier == "free"
        assert response.is_admin is False

    def test_user_response_no_password_field(self):
        """Test that password is not in response schema."""
        response_dict = {
            "id": uuid.uuid4(),
            "email": "test@example.com",
            "name": "Test",
            "subscription_tier": "free",
            "subscription_status": "active",
            "credits_remaining": 100,
            "created_at": datetime.utcnow(),
        }
        response = UserResponse(**response_dict)
        assert not hasattr(response, "password")
        assert response.is_admin is False


class TestUserUpdate:
    """Tests for UserUpdate schema."""

    def test_update_name_only(self):
        """Test updating just name."""
        data = {"name": "New Name"}
        update = UserUpdate(**data)
        assert update.name == "New Name"
        assert update.email is None

    def test_update_email_only(self):
        """Test updating just email."""
        data = {"email": "newemail@example.com"}
        update = UserUpdate(**data)
        assert update.email == "newemail@example.com"
        assert update.name is None

    def test_update_both_fields(self):
        """Test updating both fields."""
        data = {"name": "New Name", "email": "newemail@example.com"}
        update = UserUpdate(**data)
        assert update.name == "New Name"
        assert update.email == "newemail@example.com"


class TestEnums:
    """Tests for enum values."""

    def test_subscription_tier_enum(self):
        """Test subscription tier enum values."""
        assert SubscriptionTier.FREE == "free"
        assert SubscriptionTier.PROFESSIONAL == "professional"
        assert SubscriptionTier.TEAM == "team"
        assert SubscriptionTier.ENTERPRISE == "enterprise"

    def test_subscription_status_enum(self):
        """Test subscription status enum values."""
        assert SubscriptionStatus.ACTIVE == "active"
        assert SubscriptionStatus.CANCELED == "canceled"
        assert SubscriptionStatus.PAST_DUE == "past_due"


class TestTokenResponse:
    """Tests for TokenResponse schema."""

    def test_valid_token_response(self):
        """Test creating token response."""
        data = {
            "access_token": "access_token_here",
            "refresh_token": "refresh_token_here",
            "expires_in": 3600,
        }
        token = TokenResponse(**data)
        assert token.access_token == "access_token_here"
        assert token.token_type == "bearer"


class TestTokenRefreshRequest:
    """Tests for TokenRefreshRequest schema."""

    def test_valid_refresh_request(self):
        """Test creating refresh request."""
        data = {"refresh_token": "valid_token"}
        request = TokenRefreshRequest(**data)
        assert request.refresh_token == "valid_token"

    def test_none_refresh_token_allowed(self):
        """Test that refresh token can be omitted."""
        request = TokenRefreshRequest()
        assert request.refresh_token is None

    def test_empty_refresh_token_rejected(self):
        """Test that empty refresh token is rejected."""
        data = {"refresh_token": ""}
        with pytest.raises(ValidationError):
            TokenRefreshRequest(**data)
