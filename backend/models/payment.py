"""
Payment model for tracking Stripe payments.

TODO: Implementation steps:
1. Define Payment SQLAlchemy model
2. Add foreign keys to User and Job
3. Store Stripe payment intent and charge IDs
4. Track payment status
5. Add amount and currency fields
6. Implement payment method tracking
7. Add indexes for lookups
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from backend.db.session import Base


class Payment(Base):
    """
    Payment model for tracking Stripe payment transactions.

    TODO:
    - Implement all fields from database schema
    - Add Stripe integration fields
    - Track payment status
    - Add relationships to User and Job
    - Implement payment verification methods
    """

    __tablename__ = "payments"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), index=True)

    # Stripe IDs
    stripe_payment_intent_id = Column(String(255), unique=True)
    stripe_charge_id = Column(String(255))

    # Payment Details
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(String(50))  # pending, succeeded, failed, refunded

    # Payment Method
    payment_method_type = Column(String(50))  # card, bank_account, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    # TODO: Add relationships
    # user = relationship("User", back_populates="payments")
    # job = relationship("Job", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.id} - ${self.amount_cents/100:.2f} ({self.status})>"

    # TODO: Implement methods
    # def mark_succeeded(self, charge_id: str):
    #     """Mark payment as succeeded."""
    #     pass
    #
    # def mark_failed(self):
    #     """Mark payment as failed."""
    #     pass
    #
    # def process_refund(self):
    #     """Process refund for this payment."""
    #     pass
