"""
Pydantic schemas for User-related requests and responses.

Provides schemas for:
- User registration and login
- User profile management
- Subscription tier management
- Token-based authentication

All schemas include comprehensive validation for email format,
password strength, and proper data sanitization.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

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
    """Response schema for user information."""

    id: UUID
    email: str
    name: Optional[str] = None
    is_admin: bool = False
    subscription_tier: str
    subscription_status: str = "active"
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

    refresh_token: Optional[str] = None

    @field_validator("refresh_token")
    @classmethod
    def ensure_token_has_value(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("refresh_token must not be empty")
        return cleaned


class LogoutResponse(BaseModel):
    """Response schema for logout."""

    message: str


# WebAuthn/Passkey schemas
class PasskeyRegistrationOptionsRequest(BaseModel):
    """Request to generate passkey registration options."""

    name: Optional[str] = Field(None, description="User-friendly name for the passkey")


class PasskeyRegistrationOptionsResponse(BaseModel):
    """Response with registration options."""

    options: Dict
    challenge: str

    model_config = ConfigDict(extra="allow")


class PasskeyRegistrationRequest(BaseModel):
    """Request to complete passkey registration."""

    registration_response: Dict
    challenge: str
    name: Optional[str] = None


class PasskeyRegistrationResponse(BaseModel):
    """Response after successful passkey registration."""

    passkey_id: UUID
    name: Optional[str] = None
    message: str = "Passkey registered successfully"


class PasskeyAuthenticationOptionsRequest(BaseModel):
    """Request to generate passkey authentication options."""

    email: Optional[EmailStr] = None  # Optional for conditional UI


class PasskeyAuthenticationOptionsResponse(BaseModel):
    """Response with authentication options."""

    options: Dict
    challenge: str

    model_config = ConfigDict(extra="allow")


class PasskeyAuthenticationRequest(BaseModel):
    """Request to complete passkey authentication."""

    authentication_response: Dict
    challenge: str
    credential_id: str


class PasskeyResponse(BaseModel):
    """Response schema for passkey information."""

    id: UUID
    name: Optional[str]
    last_used_at: Optional[datetime]
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
