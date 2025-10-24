"""Payment routes for Stripe integration."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Header, status
from sqlalchemy.orm import Session
import stripe
import uuid

from backend.api.schemas.payment import PaymentHistoryResponse, PaymentIntentCreate, PaymentIntentResponse
from backend.api.dependencies import get_current_user
from backend.config import get_settings
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.user import User
from backend.services.payment import StripeService
from backend.tasks.audiobook_tasks import start_audiobook_workflow

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
settings = get_settings()
stripe.api_key = settings.stripe_secret_key


@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a Stripe payment intent for the given job."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


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
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=settings.stripe_webhook_secret,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc
    except stripe.error.SignatureVerificationError as exc:
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    if event.get("type") == "payment_intent.succeeded":
        data = event.get("data", {}).get("object", {})
        metadata = data.get("metadata", {})
        job_id = metadata.get("job_id")
        if job_id:
            try:
                job_uuid = uuid.UUID(job_id)
            except ValueError:
                job_uuid = None
            if job_uuid:
                job = db.query(Job).filter(Job.id == job_uuid).first()
                if job:
                    background.add_task(start_audiobook_workflow, job_id, job.repo_url, job.depth_tier)
    return {"received": True}


@router.get("/history", response_model=PaymentHistoryResponse)
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return the current user's payment history."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
