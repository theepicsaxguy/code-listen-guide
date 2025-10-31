"""
Pydantic schemas for Payment-related requests and responses.

Provides schemas for:
- Payment intent creation
- Stripe payment processing
- Webhook event handling
- Payment history and refunds
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import uuid


class PaymentIntentCreate(BaseModel):
    """
    Schema for creating a payment intent.
    
    Amount can be auto-calculated from job's depth tier if not provided.
    This will be handled in the route handler with database access.
    """

    job_id: uuid.UUID
    amount_cents: Optional[int] = None  # Auto-calculated if not provided


class PaymentIntentResponse(BaseModel):
    """Schema for payment intent response."""

    payment_intent_id: str
    client_secret: str
    amount_cents: int
    currency: str


class PaymentResponse(BaseModel):
    """
    Schema for payment data in responses.
    
    Includes complete Stripe metadata for payment tracking,
    refund processing, and payment method details.
    
    Note: job_id and stripe_payment_intent_id are optional because
    subscription payments may not be associated with a specific job.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: Optional[uuid.UUID] = None
    stripe_payment_intent_id: Optional[str] = None
    amount_cents: int
    currency: str
    status: str
    payment_method_type: Optional[str]
    
    # Stripe-specific metadata
    stripe_customer_id: Optional[str] = None
    receipt_url: Optional[str] = None
    refund_status: Optional[str] = None
    refunded_amount_cents: Optional[int] = None
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    
    created_at: datetime
    completed_at: Optional[datetime]
    refunded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @field_validator("amount_cents", "refunded_amount_cents")
    @classmethod
    def validate_amount(cls, v: Optional[int]) -> Optional[int]:
        """Ensure amounts are non-negative if provided."""
        if v is not None and v < 0:
            raise ValueError("Amount cannot be negative")
        if v is not None and v > 10000000:  # $100,000 max
            raise ValueError("Amount exceeds maximum allowed")
        return v


class PaymentHistoryResponse(BaseModel):
    """Schema for payment history list."""

    payments: list[PaymentResponse]
    total: int


class CheckoutSessionCreate(BaseModel):
    """Schema for creating a Stripe checkout session."""

    plan_id: str
    success_url: str
    cancel_url: str


class CheckoutSessionResponse(BaseModel):
    """Schema for the response of a Stripe checkout session."""

    session_id: str
    url: str


class StripeWebhookEvent(BaseModel):
    """
    Schema for Stripe webhook events.
    
    Validates event type and can be used with verify_webhook_signature
    for secure webhook processing.
    """

    type: str
    data: dict
    
    @field_validator("type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        """Validate that event type is supported."""
        supported_events = [
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "payment_intent.canceled",
            "charge.refunded",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ]
        if v not in supported_events:
            raise ValueError(f"Unsupported event type: {v}")
        return v


def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """
    Verify Stripe webhook signature for security.
    
    Args:
        payload: Raw webhook payload string
        signature: Stripe signature from request headers
        secret: Webhook secret from Stripe dashboard
        
    Returns:
        True if signature is valid, False otherwise
        
    Example:
        >>> from backend.config import get_settings
        >>> settings = get_settings()
        >>> is_valid = verify_webhook_signature(
        ...     payload=request.body,
        ...     signature=request.headers["Stripe-Signature"],
        ...     secret=settings.STRIPE_WEBHOOK_SECRET
        ... )
    """
    try:
        import stripe
        stripe.Webhook.construct_event(payload, signature, secret)
        return True
    except stripe.SignatureVerificationError:
        return False
    except Exception:
        return False


class RefundRequest(BaseModel):
    """Schema for refund request."""

    amount: Optional[float] = None
    reason: str = "requested_by_customer"

    @field_validator("reason", mode="before")
    def validate_reason(cls, v: Optional[str]) -> str:
        """Validate refund reason."""
        # Use default if None
        if v is None:
            return "requested_by_customer"
        
        allowed_reasons = ["duplicate", "fraudulent", "requested_by_customer"]
        if v not in allowed_reasons:
            raise ValueError(f"Reason must be one of: {', '.join(allowed_reasons)}")
        return v

    @field_validator("amount", mode="before")
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate refund amount."""
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v
