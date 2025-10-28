"""Tests for payment schema validation."""

import pytest
import uuid
from datetime import datetime
from pydantic import ValidationError

from backend.api.schemas.payment import (
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentResponse,
    PaymentHistoryResponse,
    StripeWebhookEvent,
    verify_webhook_signature,
)


class TestPaymentIntentCreate:
    """Tests for PaymentIntentCreate schema."""

    def test_valid_payment_intent_with_amount(self):
        """Test creating payment intent with explicit amount."""
        data = {
            "job_id": uuid.uuid4(),
            "amount_cents": 4900,
        }
        intent = PaymentIntentCreate(**data)
        assert intent.amount_cents == 4900

    def test_valid_payment_intent_without_amount(self):
        """Test creating payment intent without amount (auto-calculated)."""
        data = {
            "job_id": uuid.uuid4(),
        }
        intent = PaymentIntentCreate(**data)
        assert intent.amount_cents is None


class TestPaymentResponse:
    """Tests for PaymentResponse schema."""

    def test_valid_payment_response(self):
        """Test creating payment response with valid data."""
        response_dict = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "job_id": uuid.uuid4(),
            "stripe_payment_intent_id": "pi_123456789",
            "amount_cents": 4900,
            "currency": "usd",
            "status": "succeeded",
            "payment_method_type": "card",
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
        }
        response = PaymentResponse(**response_dict)
        assert response.amount_cents == 4900
        assert response.status == "succeeded"

    def test_payment_response_with_refund_data(self):
        """Test payment response with refund information."""
        response_dict = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "job_id": uuid.uuid4(),
            "stripe_payment_intent_id": "pi_123456789",
            "amount_cents": 4900,
            "currency": "usd",
            "status": "refunded",
            "payment_method_type": "card",
            "refund_status": "succeeded",
            "refunded_amount_cents": 4900,
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
            "refunded_at": datetime.utcnow(),
        }
        response = PaymentResponse(**response_dict)
        assert response.refund_status == "succeeded"
        assert response.refunded_amount_cents == 4900

    def test_payment_response_with_failure_data(self):
        """Test payment response with failure information."""
        response_dict = {
            "id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "job_id": uuid.uuid4(),
            "stripe_payment_intent_id": "pi_123456789",
            "amount_cents": 4900,
            "currency": "usd",
            "status": "failed",
            "payment_method_type": "card",
            "failure_code": "card_declined",
            "failure_message": "Your card was declined",
            "created_at": datetime.utcnow(),
            "completed_at": None,
        }
        response = PaymentResponse(**response_dict)
        assert response.failure_code == "card_declined"
        assert response.failure_message == "Your card was declined"

    def test_payment_response_negative_amount_rejected(self):
        """Test that negative amount is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PaymentResponse(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                job_id=uuid.uuid4(),
                stripe_payment_intent_id="pi_123",
                amount_cents=-100,
                currency="usd",
                status="pending",
                payment_method_type="card",
                created_at=datetime.utcnow(),
            )
        assert "negative" in str(exc_info.value).lower()

    def test_payment_response_excessive_amount_rejected(self):
        """Test that excessive amount is rejected."""
        with pytest.raises(ValidationError):
            PaymentResponse(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                job_id=uuid.uuid4(),
                stripe_payment_intent_id="pi_123",
                amount_cents=20000000,  # $200,000
                currency="usd",
                status="pending",
                payment_method_type="card",
                created_at=datetime.utcnow(),
            )


class TestStripeWebhookEvent:
    """Tests for StripeWebhookEvent schema."""

    def test_valid_webhook_event_payment_succeeded(self):
        """Test creating webhook event for payment success."""
        data = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_123"}},
        }
        event = StripeWebhookEvent(**data)
        assert event.type == "payment_intent.succeeded"

    def test_valid_webhook_event_payment_failed(self):
        """Test creating webhook event for payment failure."""
        data = {
            "type": "payment_intent.payment_failed",
            "data": {"object": {"id": "pi_123"}},
        }
        event = StripeWebhookEvent(**data)
        assert event.type == "payment_intent.payment_failed"

    def test_valid_webhook_event_refund(self):
        """Test creating webhook event for refund."""
        data = {
            "type": "charge.refunded",
            "data": {"object": {"id": "ch_123"}},
        }
        event = StripeWebhookEvent(**data)
        assert event.type == "charge.refunded"

    def test_unsupported_webhook_event_rejected(self):
        """Test that unsupported event type is rejected."""
        data = {
            "type": "unsupported.event.type",
            "data": {"object": {}},
        }
        with pytest.raises(ValidationError) as exc_info:
            StripeWebhookEvent(**data)
        assert "Unsupported event type" in str(exc_info.value)

    def test_all_supported_webhook_events(self):
        """Test that all documented event types are supported."""
        supported_events = [
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "payment_intent.canceled",
            "charge.refunded",
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ]
        
        for event_type in supported_events:
            data = {
                "type": event_type,
                "data": {"object": {}},
            }
            event = StripeWebhookEvent(**data)
            assert event.type == event_type


class TestWebhookSignatureVerification:
    """Tests for webhook signature verification function."""

    def test_verify_webhook_signature_invalid_signature(self):
        """Test that invalid signature returns False."""
        # This will return False because we're not using real Stripe data
        result = verify_webhook_signature(
            payload='{"test": "data"}',
            signature="invalid_signature",
            secret="whsec_test",
        )
        assert result is False

    def test_verify_webhook_signature_handles_exceptions(self):
        """Test that verification handles exceptions gracefully."""
        # Should not raise exception, just return False
        result = verify_webhook_signature(
            payload="",
            signature="",
            secret="",
        )
        assert result is False
