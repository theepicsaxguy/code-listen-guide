"""
Pydantic schemas for User-related requests and responses.

TODO: Implementation steps:
1. Define UserCreate schema for registration
2. Define UserLogin schema
3. Define UserResponse schema (exclude password)
4. Define UserUpdate schema
5. Add email validation
6. Add password strength validation
7. Create subscription tier enum
"""

from datetime import datetime
from enum import Enum
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from backend.utils.validators import validate_password_strength


class SubscriptionTier(str, Enum):
    """User subscription tiers."""
    FREE = "free"
    PROFESSIONAL = "professional"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"


class UserCreate(BaseModel):
    """Input payload for user registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def enforce_password_strength(cls, value: str) -> str:
        is_valid, error_msg = validate_password_strength(value)
        if not is_valid and error_msg:
            raise ValueError(error_msg)
        return value

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        return cleaned or None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Serialized user data for API responses."""
    id: uuid.UUID
    email: EmailStr
    name: Optional[str]
    subscription_tier: str
    subscription_status: Optional[str]
    credits_remaining: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefreshRequest(BaseModel):
    """Input payload for refreshing access tokens."""

    refresh_token: str = Field(..., min_length=1)
