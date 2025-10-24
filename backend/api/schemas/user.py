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

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


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
    """
    Schema for user registration.

    TODO:
    - Add password strength validation
    - Add email format validation
    - Add name validation
    """
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: Optional[str] = None

    # TODO: Add validators
    # @validator("password")
    # def validate_password_strength(cls, v):
    #     # Check for uppercase, lowercase, number, special char
    #     pass


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for user data in responses (excludes password).

    TODO:
    - Add computed fields if needed
    - Configure from_attributes for ORM compatibility
    """
    id: uuid.UUID
    email: str
    name: Optional[str]
    subscription_tier: str
    subscription_status: Optional[str]
    credits_remaining: int
    created_at: datetime

    class Config:
        from_attributes = True


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
