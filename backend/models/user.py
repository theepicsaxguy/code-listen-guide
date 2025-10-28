"""
User model for authentication and subscription management.

Provides:
- User authentication with password hashing
- Subscription tier management (free, professional, team, enterprise)
- Credit tracking for pay-per-use features
- Stripe customer integration
"""

from sqlalchemy import Column, String, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from backend.db.session import Base


class User(Base):
    """
    User model representing a registered user.

    Attributes:
        id: Unique user identifier (UUID)
        email: User email address (unique, indexed)
        hashed_password: Bcrypt hashed password
        name: User display name
        stripe_customer_id: Stripe customer ID for billing
        subscription_tier: Subscription level (free, professional, team, enterprise)
        subscription_status: Subscription state (active, canceled, past_due)
        credits_remaining: Available credits for pay-per-use features
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255))
    is_admin = Column(Boolean, default=False, nullable=False)

    # Stripe Integration
    stripe_customer_id = Column(String(255), unique=True)

    # Subscription
    subscription_tier = Column(
        String(50), default="free"
    )  # free, professional, team, enterprise
    subscription_status = Column(
        String(50), default="active"
    )  # active, canceled, past_due

    # Credits
    credits_remaining = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # Note: Uncomment when ready to use relationships
    # jobs = relationship("Job", back_populates="user")
    # payments = relationship("Payment", back_populates="user")
    # usage_logs = relationship("UsageLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"

    def deduct_credits(self, amount: int) -> bool:
        """
        Deduct credits from user account.

        Args:
            amount: Number of credits to deduct

        Returns:
            True if deduction successful, False if insufficient credits
        """
        if self.credits_remaining >= amount:
            self.credits_remaining -= amount
            return True
        return False

    def has_active_subscription(self) -> bool:
        """
        Check if user has an active paid subscription.

        Returns:
            True if subscription is active and not free tier
        """
        return self.subscription_status == "active" and self.subscription_tier != "free"
