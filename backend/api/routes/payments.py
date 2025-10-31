"""Payment routes for Stripe integration."""

import logging
from datetime import datetime
from typing import Optional
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session

import stripe
from backend.api.dependencies import get_current_user
from backend.api.schemas.payment import (
    PaymentHistoryResponse,
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentResponse,
    CheckoutSessionCreate,
    CheckoutSessionResponse,
)
from backend.config import get_settings
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.payment import Payment
from backend.models.user import User
from backend.services.payment import (
    create_payment_intent,
    get_stripe_service,
    create_checkout_session,
)
from backend.tasks.audiobook_tasks import start_audiobook_workflow
from backend.api.schemas.job import calculate_price_for_tier, DepthTier

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
settings = get_settings()
logger = logging.getLogger(__name__)


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent_route(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe payment intent for the given job."""
    job = (
        db.query(Job)
        .filter(Job.id == payment_data.job_id, Job.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    if job.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Job already completed"
        )

    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.job_id == job.id,
            Payment.status.in_(["succeeded", "requires_capture"]),
        )
        .first()
    )
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Job already paid"
        )

    # Calculate amount based on tier or use provided amount
    if payment_data.amount_cents is not None:
        amount_cents = payment_data.amount_cents
    else:
        # Use tier-based pricing from job schema
        try:
            depth_tier = DepthTier(job.depth_tier)
            amount_cents = calculate_price_for_tier(depth_tier)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid depth tier: {job.depth_tier}",
            )

    if amount_cents <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment amount"
        )

    # Create or get Stripe customer
    customer_id = current_user.stripe_customer_id
    if not customer_id:
        # Create Stripe customer if user doesn't have one
        stripe_service = get_stripe_service()
        try:
            customer_id = await stripe_service.create_customer(
                email=current_user.email, name=current_user.name
            )
            current_user.stripe_customer_id = customer_id
            db.commit()
            logger.info(
                "Created Stripe customer for user",
                extra={"user_id": str(current_user.id), "customer_id": customer_id},
            )
        except Exception as e:
            logger.error(
                "Failed to create Stripe customer",
                extra={"user_id": str(current_user.id), "error": str(e)},
                exc_info=True,
            )
            # Continue without customer_id - Stripe will create one automatically

    intent = await create_payment_intent(
        job_id=str(job.id),
        amount_cents=amount_cents,
        user_email=current_user.email,
        customer_id=customer_id,
        create_customer_if_missing=False,  # We handle customer creation above
    )

    payment_record = Payment(
        user_id=current_user.id,
        job_id=job.id,
        stripe_payment_intent_id=intent.id,
        stripe_customer_id=customer_id,  # Capture customer ID
        amount_cents=intent.amount,
        currency=intent.currency,
        status=intent.status,
    )
    db.add(payment_record)
    db.commit()
    db.refresh(payment_record)

    return PaymentIntentResponse(
        payment_intent_id=intent.id,
        client_secret=intent.client_secret,
        amount_cents=intent.amount,
        currency=intent.currency,
    )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
):
    """
    Process Stripe webhook events and trigger workflows when payments succeed.
    
    Handles:
    - payment_intent.succeeded: Mark payment as succeeded, trigger workflow
    - payment_intent.payment_failed: Mark payment as failed, update job status
    - charge.refunded: Mark payment as refunded, update job if needed
    """
    payload = await request.body()
    event_type = None
    
    logger.info("Webhook received", extra={
        "signature_present": stripe_signature is not None,
        "payload_length": len(payload),
        "headers": dict(request.headers)
    })
    
    # Check if signature is present
    if not stripe_signature:
        logger.error("Missing Stripe-Signature header")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Missing Stripe-Signature header"
        )
    
    try:
        event = get_stripe_service().verify_webhook_signature(payload, stripe_signature)
        event_type = event.get("type")
        logger.info("Received Stripe webhook", extra={"event_type": event_type, "event_id": event.get("id")})
    except ValueError as exc:
        logger.error("Invalid webhook payload", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
        ) from exc
    except stripe.SignatureVerificationError as exc:
        logger.error("Invalid webhook signature", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        ) from exc

    data = event.get("data", {}).get("object", {})
    intent_id = data.get("id")
    metadata = data.get("metadata", {})
    job_id = metadata.get("job_id")

    # Handle payment_intent.succeeded
    if event_type == "payment_intent.succeeded":
        payment_record = None
        if intent_id:
            payment_record = (
                db.query(Payment)
                .filter(Payment.stripe_payment_intent_id == intent_id)
                .first()
            )
            if payment_record:
                payment_record.status = "succeeded"
                payment_record.stripe_charge_id = data.get("latest_charge")
                payment_record.stripe_customer_id = data.get("customer")
                methods = data.get("payment_method_types") or []
                payment_record.payment_method_type = (
                    methods[0] if methods else payment_record.payment_method_type
                )
                payment_record.completed_at = datetime.utcnow()
                
                # Fetch charge details to get receipt URL
                charge_id = data.get("latest_charge")
                if charge_id:
                    try:
                        charge = stripe.Charge.retrieve(charge_id)
                        payment_record.receipt_url = charge.get("receipt_url")
                    except stripe.StripeError as e:
                        logger.warning(f"Failed to retrieve charge receipt URL: {e}")
                
                logger.info(
                    "Payment marked as succeeded",
                    extra={"payment_id": str(payment_record.id), "intent_id": intent_id},
                )

        job = None
        if job_id:
            try:
                job_uuid = uuid.UUID(job_id)
            except ValueError:
                logger.warning("Invalid job_id in webhook metadata", extra={"job_id": job_id})
                job_uuid = None
            if job_uuid:
                job = db.query(Job).filter(Job.id == job_uuid).first()
                if job:
                    job.status = "paid"
                    if payment_record:
                        job.price_paid_cents = payment_record.amount_cents
                    logger.info(
                        "Job marked as paid, triggering workflow",
                        extra={"job_id": str(job.id)},
                    )

        db.commit()
        if job:
            background.add_task(
                start_audiobook_workflow, str(job.id), job.repo_url, job.depth_tier
            )

    # Handle payment_intent.payment_failed
    elif event_type == "payment_intent.payment_failed":
        if intent_id:
            payment_record = (
                db.query(Payment)
                .filter(Payment.stripe_payment_intent_id == intent_id)
                .first()
            )
            if payment_record:
                payment_record.status = "failed"
                # Store failure information
                last_payment_error = data.get("last_payment_error", {})
                if last_payment_error:
                    payment_record.failure_code = last_payment_error.get("code")
                    payment_record.failure_message = last_payment_error.get("message")
                    logger.warning(
                        "Payment failed",
                        extra={
                            "payment_id": str(payment_record.id),
                            "intent_id": intent_id,
                            "error_code": payment_record.failure_code,
                            "error_message": payment_record.failure_message,
                        },
                    )

        if job_id:
            try:
                job_uuid = uuid.UUID(job_id)
                job = db.query(Job).filter(Job.id == job_uuid).first()
                if job:
                    job.status = "failed"
                    job.error_message = "Payment failed"
                    logger.info(
                        "Job marked as failed due to payment failure",
                        extra={"job_id": str(job.id)},
                    )
            except ValueError:
                pass

        db.commit()

    # Handle checkout.session.completed (for subscriptions)
    elif event_type == "checkout.session.completed":
        customer_id = data.get("customer")
        subscription_id = data.get("subscription")
        amount_total = data.get("amount_total", 0)  # Amount in cents
        
        if customer_id:
            # Find user by Stripe customer ID
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                # Get the subscription details to determine the plan
                if subscription_id:
                    try:
                        subscription = stripe.Subscription.retrieve(subscription_id)
                        # Get the price lookup key from the subscription
                        if subscription.get("items") and subscription["items"].get("data"):
                            price_id = subscription["items"]["data"][0]["price"]["id"]
                            price = stripe.Price.retrieve(price_id)
                            plan_lookup_key = price.get("lookup_key", "")
                            
                            # Update user's subscription tier
                            if plan_lookup_key in ["professional", "team", "enterprise"]:
                                user.subscription_tier = plan_lookup_key
                                user.subscription_status = "active"
                                
                                # Add credits based on plan
                                credits_to_add = {
                                    "professional": 10,
                                    "team": 50,
                                    "enterprise": 200
                                }.get(plan_lookup_key, 0)
                                
                                user.credits_remaining += credits_to_add
                                
                                # Create a payment record for the subscription
                                payment = Payment(
                                    user_id=user.id,
                                    amount_cents=amount_total,
                                    currency=data.get("currency", "usd"),
                                    status="succeeded",
                                    payment_method_type="subscription",
                                    stripe_payment_intent_id=data.get("payment_intent"),
                                    stripe_customer_id=customer_id,
                                    stripe_charge_id=None,
                                    completed_at=datetime.utcnow(),
                                )
                                db.add(payment)
                                
                                logger.info(
                                    "User subscription updated",
                                    extra={
                                        "user_id": str(user.id),
                                        "plan": plan_lookup_key,
                                        "credits_added": credits_to_add,
                                        "amount_cents": amount_total,
                                    },
                                )
                    except stripe.StripeError as e:
                        logger.error(f"Failed to retrieve subscription: {e}")
                
                db.commit()

    # Handle charge.refunded
    elif event_type == "charge.refunded":
        charge_id = data.get("id")
        payment_intent_id = data.get("payment_intent")
        
        if payment_intent_id:
            payment_record = (
                db.query(Payment)
                .filter(Payment.stripe_payment_intent_id == payment_intent_id)
                .first()
            )
            if payment_record:
                payment_record.status = "refunded"
                payment_record.refunded_at = datetime.utcnow()
                
                # Calculate refund status and amount
                amount_refunded = data.get("amount_refunded", 0)
                original_amount = data.get("amount", payment_record.amount_cents)
                
                if amount_refunded > 0:
                    payment_record.refunded_amount_cents = amount_refunded
                    
                    # Determine refund status: partial or full
                    if amount_refunded >= original_amount:
                        payment_record.refund_status = "full"
                    else:
                        payment_record.refund_status = "partial"
                    
                    logger.info(
                        "Payment refunded",
                        extra={
                            "payment_id": str(payment_record.id),
                            "amount_refunded_cents": amount_refunded,
                            "refund_status": payment_record.refund_status,
                        },
                    )

        if job_id:
            try:
                job_uuid = uuid.UUID(job_id)
                job = db.query(Job).filter(Job.id == job_uuid).first()
                if job and job.status == "completed":
                    # If job was completed, we may want to handle refunds differently
                    logger.info(
                        "Refund processed for completed job",
                        extra={"job_id": str(job.id)},
                    )
            except ValueError:
                pass

        db.commit()

    else:
        logger.debug("Unhandled webhook event type", extra={"event_type": event_type})

    return {"received": True}


@router.get("/history", response_model=PaymentHistoryResponse)
async def get_payment_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Return the current user's payment history."""
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return PaymentHistoryResponse(
        payments=[PaymentResponse.model_validate(payment) for payment in payments],
        total=len(payments),
    )


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session_route(
    checkout_data: CheckoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe checkout session for the given plan."""
    # Ensure user has a Stripe customer ID
    customer_id = current_user.stripe_customer_id
    if not customer_id:
        stripe_service = get_stripe_service()
        try:
            customer_id = await stripe_service.create_customer(
                email=current_user.email, name=current_user.name
            )
            current_user.stripe_customer_id = customer_id
            db.commit()
            logger.info(
                "Created Stripe customer for checkout session",
                extra={"user_id": str(current_user.id), "customer_id": customer_id},
            )
        except Exception as e:
            logger.error(
                "Failed to create Stripe customer for checkout",
                extra={"user_id": str(current_user.id), "error": str(e)},
                exc_info=True,
            )
            # Continue without customer_id

    session = await create_checkout_session(
        plan_id=checkout_data.plan_id,
        success_url=checkout_data.success_url,
        cancel_url=checkout_data.cancel_url,
        customer_id=customer_id,
    )
    return CheckoutSessionResponse(
        session_id=session.id,
        url=session.url,
    )


@router.post("/refund")
async def create_refund(
    payment_intent_id: str,
    amount_cents: Optional[int] = None,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a refund for a payment.
    
    Only the user who made the payment can request a refund.
    Refunds can be full or partial.
    """
    # Find the payment record
    payment = (
        db.query(Payment)
        .filter(
            Payment.stripe_payment_intent_id == payment_intent_id,
            Payment.user_id == current_user.id,
        )
        .first()
    )
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    # Verify payment was successful
    if payment.status != "succeeded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot refund payment with status: {payment.status}",
        )
    
    # Verify amount if provided
    if amount_cents is not None:
        if amount_cents <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount must be positive",
            )
        if amount_cents > payment.amount_cents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund amount cannot exceed payment amount",
            )
    
    try:
        # Process refund via Stripe
        from backend.services.payment import process_refund
        
        refund = await process_refund(
            payment_intent_id=payment_intent_id,
            amount_cents=amount_cents,
            reason=reason,
        )
        
        # Update payment status
        payment.status = "refunded"
        db.commit()
        
        logger.info(
            "Refund processed successfully",
            extra={
                "payment_id": str(payment.id),
                "payment_intent_id": payment_intent_id,
                "amount_cents": amount_cents or payment.amount_cents,
            },
        )
        
        return {
            "refund_id": getattr(refund, "id", refund.get("id") if isinstance(refund, dict) else None),
            "amount_refunded_cents": amount_cents or payment.amount_cents,
            "status": "refunded",
        }
    except Exception as e:
        logger.error(
            "Failed to process refund",
            extra={
                "payment_intent_id": payment_intent_id,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process refund: {str(e)}",
        )
