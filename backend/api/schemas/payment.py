"""
Pydantic schemas for Payment-related requests and responses.

TODO: Implementation steps:
1. Define PaymentIntentCreate schema
2. Define PaymentResponse schema
3. Define webhook event schema
4. Add Stripe-specific fields
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class PaymentIntentCreate(BaseModel):
    """
    Schema for creating a payment intent.

    TODO:
    - Add amount calculation based on job
    - Add currency selection
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

    TODO:
    - Add all Stripe metadata
    - Include payment method details
    """

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    stripe_payment_intent_id: str
    amount_cents: int
    currency: str
    status: str
    payment_method_type: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaymentHistoryResponse(BaseModel):
    """Schema for payment history list."""

    payments: list[PaymentResponse]
    total: int


class StripeWebhookEvent(BaseModel):
    """
    Schema for Stripe webhook events.

    TODO:
    - Add signature verification
    - Handle different event types
    """

    type: str
    data: dict
