"""Stripe payment helpers used by the API and workflows."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

import stripe

from backend.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class PaymentIntentResult:
    id: str
    client_secret: str
    amount: int
    currency: str
    status: str
    raw: Any


@dataclass
class CheckoutSessionResult:
    id: str
    url: str
    raw: Any


class StripeService:
    """Asynchronous wrapper around Stripe SDK operations."""

    def __init__(self, api_key: str, webhook_secret: str) -> None:
        stripe.api_key = api_key
        self.webhook_secret = webhook_secret

    async def create_payment_intent(
        self,
        *,
        amount_cents: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentIntentResult:
        payload: Dict[str, Any] = {
            "amount": amount_cents,
            "currency": currency,
            "automatic_payment_methods": {"enabled": True},
        }
        if customer_id:
            payload["customer"] = customer_id
        if metadata:
            payload["metadata"] = metadata

        def _create() -> Any:
            return stripe.PaymentIntent.create(**payload)

        intent = await asyncio.to_thread(_create)
        return PaymentIntentResult(
            id=getattr(intent, "id", intent["id"]),
            client_secret=getattr(intent, "client_secret", intent["client_secret"]),
            amount=getattr(intent, "amount", intent["amount"]),
            currency=getattr(intent, "currency", intent["currency"]),
            status=getattr(intent, "status", intent["status"]),
            raw=intent,
        )

    def verify_webhook_signature(
        self, payload: bytes, sig_header: str
    ) -> Dict[str, Any]:
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=self.webhook_secret,
        )

    async def create_customer(self, *, email: str, name: Optional[str] = None) -> str:
        def _create() -> Any:
            return stripe.Customer.create(email=email, name=name)

        customer = await asyncio.to_thread(_create)
        return getattr(customer, "id", customer["id"])

    async def process_refund(
        self,
        *,
        payment_intent_id: str,
        amount_cents: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Any:
        payload: Dict[str, Any] = {"payment_intent": payment_intent_id}
        if amount_cents:
            payload["amount"] = amount_cents
        if reason:
            payload["reason"] = reason

        def _refund() -> Any:
            return stripe.Refund.create(**payload)

        return await asyncio.to_thread(_refund)

    async def create_checkout_session(
        self,
        *,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        customer_id: Optional[str] = None,
    ) -> CheckoutSessionResult:
        def _list_prices() -> Any:
            return stripe.Price.list(lookup_keys=[plan_id], expand=["data.product"])

        prices = await asyncio.to_thread(_list_prices)
        if not prices.data:
            logger.error("Invalid plan_id provided for checkout session", extra={"plan_id": plan_id})
            raise ValueError(f"Invalid plan_id: {plan_id}")

        price_id = prices.data[0].id

        payload: Dict[str, Any] = {
            "payment_method_types": ["card"],
            "line_items": [
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            "mode": "subscription",
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        if customer_id:
            payload["customer"] = customer_id

        def _create() -> Any:
            return stripe.checkout.Session.create(**payload)

        session = await asyncio.to_thread(_create)
        return CheckoutSessionResult(
            id=getattr(session, "id", session["id"]),
            url=getattr(session, "url", session["url"]),
            raw=session,
        )


_stripe_service: Optional[StripeService] = None


def get_stripe_service() -> StripeService:
    global _stripe_service
    if _stripe_service is None:
        settings = get_settings()
        _stripe_service = StripeService(
            api_key=settings.stripe_secret_key,
            webhook_secret=settings.stripe_webhook_secret,
        )
    return _stripe_service


async def create_payment_intent(
    *,
    job_id: str,
    amount_cents: int,
    user_email: str,
    customer_id: Optional[str] = None,
    currency: str = "usd",
) -> PaymentIntentResult:
    service = get_stripe_service()
    metadata = {"job_id": job_id, "user_email": user_email}
    logger.info(
        "Creating Stripe payment intent",
        extra={"job_id": job_id, "amount": amount_cents},
    )
    return await service.create_payment_intent(
        amount_cents=amount_cents,
        currency=currency,
        customer_id=customer_id,
        metadata=metadata,
    )


async def create_checkout_session(
    *,
    plan_id: str,
    success_url: str,
    cancel_url: str,
    customer_id: Optional[str] = None,
) -> CheckoutSessionResult:
    service = get_stripe_service()
    logger.info(
        "Creating Stripe checkout session",
        extra={"plan_id": plan_id, "customer_id": customer_id},
    )
    return await service.create_checkout_session(
        plan_id=plan_id,
        success_url=success_url,
        cancel_url=cancel_url,
        customer_id=customer_id,
    )


async def handle_payment_webhook(
    *, payload: bytes | Dict[str, Any], signature: str
) -> Dict[str, Any]:
    service = get_stripe_service()
    raw_payload = (
        payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    )
    event = service.verify_webhook_signature(raw_payload, signature)
    logger.info("Processed Stripe webhook", extra={"type": event.get("type")})
    return event


async def process_refund(
    *,
    payment_intent_id: str,
    amount_cents: Optional[int] = None,
    reason: Optional[str] = None,
) -> Any:
    service = get_stripe_service()
    return await service.process_refund(
        payment_intent_id=payment_intent_id,
        amount_cents=amount_cents,
        reason=reason,
    )
