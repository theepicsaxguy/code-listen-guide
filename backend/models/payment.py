"""
Payment model for tracking Stripe payments.

All fields are defined and the model is ready to use.
Relationships and helper methods are commented out - uncomment when needed.
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

    All fields are implemented. Uncomment relationships when User and Job models are active.
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
    stripe_customer_id = Column(String(255), index=True)

    # Payment Details
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default="usd")
    status = Column(String(50))  # pending, succeeded, failed, refunded

    # Payment Method
    payment_method_type = Column(String(50))  # card, bank_account, etc.

    # Receipt and Refund Information
    receipt_url = Column(String(500))
    refund_status = Column(String(50))  # None, partial, full
    refunded_amount_cents = Column(Integer)

    # Failure Information (for failed payments)
    failure_code = Column(String(100))
    failure_message = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))

    # Relationships (uncomment when User and Job models are active)
    # user = relationship("User", back_populates="payments")
    # job = relationship("Job", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.id} - ${self.amount_cents/100:.2f} ({self.status})>"

    # Helper methods (uncomment and implement as needed)
    # def mark_succeeded(self, charge_id: str):
    #     """Mark payment as succeeded."""
    #     pass
    #
    # def mark_failed(self):
    #     """Mark payment as failed."""
    #     pass
    #
    # def mark_refunded(self):
    #     """Mark payment as refunded."""
    #     pass
