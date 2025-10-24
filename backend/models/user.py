"""
User model for authentication and subscription management.

TODO: Implementation steps:
1. Define User SQLAlchemy model with all fields from schema
2. Add relationships to jobs, payments, and usage_logs
3. Implement password hashing methods
4. Add subscription tier validation
5. Create methods for credit management
6. Add indexes for email lookups
7. Implement soft delete if needed
8. Add created_at/updated_at timestamps with auto-update
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

    TODO:
    - Implement all fields from database schema
    - Add password hashing with passlib
    - Create methods: check_password, set_password
    - Add subscription management methods
    - Implement credit deduction logic
    - Add relationship to Job, Payment, UsageLog models
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Basic Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    # TODO: Add hashed_password field

    # Stripe Integration
    stripe_customer_id = Column(String(255), unique=True)

    # Subscription
    # TODO: Use proper Enum type
    subscription_tier = Column(String(50), default="free")  # free, professional, team, enterprise
    subscription_status = Column(String(50))  # active, canceled, past_due

    # Credits
    credits_remaining = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    # TODO: Add relationships
    # jobs = relationship("Job", back_populates="user")
    # payments = relationship("Payment", back_populates="user")
    # usage_logs = relationship("UsageLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"

    # TODO: Implement methods
    # def set_password(self, password: str):
    #     """Hash and set user password."""
    #     pass
    #
    # def check_password(self, password: str) -> bool:
    #     """Verify password against hash."""
    #     pass
    #
    # def deduct_credits(self, amount: int) -> bool:
    #     """Deduct credits from user account."""
    #     pass
    #
    # def has_active_subscription(self) -> bool:
    #     """Check if user has active paid subscription."""
    #     pass
