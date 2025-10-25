"""Payment routes for Stripe integration."""

from datetime import datetime
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

import stripe
from backend.api.dependencies import get_current_user
from backend.api.schemas.payment import PaymentHistoryResponse, PaymentIntentCreate, PaymentIntentResponse, PaymentResponse
from backend.config import get_settings
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.payment import Payment
from backend.models.user import User
from backend.services.payment import create_payment_intent, get_stripe_service
from backend.tasks.audiobook_tasks import start_audiobook_workflow
from backend.tools.db_tools import estimate_job_cost

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
settings = get_settings()


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe payment intent for the given job."""
    job = (
        db.query(Job)
        .filter(Job.id == payment_data.job_id, Job.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status == "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job already completed")

    existing_payment = (
        db.query(Payment)
        .filter(Payment.job_id == job.id, Payment.status.in_(["succeeded", "requires_capture"]))
        .first()
    )
    if existing_payment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Job already paid")

    if payment_data.amount_cents is not None:
        amount_cents = payment_data.amount_cents
    else:
        estimate = estimate_job_cost(job.repo_url, job.depth_tier)
        amount_cents = estimate["estimated_cost_cents"]

    if amount_cents <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment amount")

    intent = await create_payment_intent(
        job_id=str(job.id),
        amount_cents=amount_cents,
        user_email=current_user.email,
        customer_id=current_user.stripe_customer_id,
    )

    payment_record = Payment(
        user_id=current_user.id,
        job_id=job.id,
        stripe_payment_intent_id=intent.id,
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
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    """Process Stripe webhook events and trigger workflows when payments succeed."""
    payload = await request.body()
    try:
        event = get_stripe_service().verify_webhook_signature(payload, stripe_signature)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload") from exc
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature") from exc

    if event.get("type") == "payment_intent.succeeded":
        data = event.get("data", {}).get("object", {})
        intent_id = data.get("id")
        metadata = data.get("metadata", {})
        job_id = metadata.get("job_id")
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
                methods = data.get("payment_method_types") or []
                payment_record.payment_method_type = methods[0] if methods else payment_record.payment_method_type
                payment_record.completed_at = datetime.utcnow()
        job = None
        if job_id:
            try:
                job_uuid = uuid.UUID(job_id)
            except ValueError:
                job_uuid = None
            if job_uuid:
                job = db.query(Job).filter(Job.id == job_uuid).first()
                if job:
                    job.status = "paid"
                    if payment_record:
                        job.price_paid_cents = payment_record.amount_cents
        db.commit()
        if job:
            background.add_task(start_audiobook_workflow, str(job.id), job.repo_url, job.depth_tier)
    return {"received": True}


@router.get("/history", response_model=PaymentHistoryResponse)
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return the current user's payment history."""
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return PaymentHistoryResponse(
        payments=[PaymentResponse.from_orm(payment) for payment in payments],
        total=len(payments),
    )
