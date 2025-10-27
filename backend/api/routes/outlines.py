from datetime import datetime
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from backend.api.schemas.outline import (
    OutlineApprove,
    OutlineGenerateRequest,
    OutlineResponse,
    OutlineUpdate,
)
from backend.api.schemas.payment import PaymentIntentResponse
from backend.db.session import get_db
from backend.models.user import User
from backend.models.job import Job
from backend.models.outline import Outline
from backend.models.payment import Payment
from backend.api.dependencies import get_current_user
from backend.services.outline_generator import generate_outline as run_outline_generator
from backend.services.payment import create_payment_intent
from backend.tasks.audiobook_tasks import resume_audiobook_workflow
from backend.tools.db_tools import estimate_job_cost, persist_outline

router = APIRouter(prefix="/api/v1/jobs/{job_id}/outline", tags=["outlines"])


def _get_job_for_user(db: Session, job_id: uuid.UUID, user_id: uuid.UUID) -> Job | None:
    return db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()


def _get_outline_for_job(db: Session, job_id: uuid.UUID) -> Outline | None:
    return db.query(Outline).filter(Outline.job_id == job_id).first()


@router.get("", response_model=OutlineResponse)
async def get_outline(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    outline = _get_outline_for_job(db, job.id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")

    return OutlineResponse.model_validate(outline)


@router.post("", response_model=OutlineResponse, status_code=status.HTTP_201_CREATED)
async def generate_outline(
    job_id: uuid.UUID,
    payload: OutlineGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    outline_payload = await run_outline_generator(
        analysis_data=payload.analysis_data,
        depth_tier=job.depth_tier,
        job_id=str(job.id),
    )
    outline_model = outline_payload.model_copy(update={"depth_tier": job.depth_tier})
    outline_record = persist_outline(str(job.id), outline_model, db=db)
    job.status = "waiting_approval"
    job.current_stage = "outline"
    db.commit()
    db.refresh(outline_record)
    return OutlineResponse.model_validate(outline_record)


@router.put("", response_model=OutlineResponse)
async def update_outline(
    job_id: uuid.UUID,
    outline_update: OutlineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    outline = _get_outline_for_job(db, job.id)
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")

    outline.outline_data = outline_update.outline_data.model_dump()
    outline.user_modifications = outline_update.user_modifications
    outline.user_approved = False
    outline.approved_at = None
    job.status = "waiting_approval"
    job.current_stage = "outline"
    db.commit()
    db.refresh(outline)
    return OutlineResponse.model_validate(outline)


@router.post("/approve", response_model=PaymentIntentResponse)
async def approve_outline(
    job_id: uuid.UUID,
    approval: OutlineApprove,
    background: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = _get_job_for_user(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    outline = (
        db.query(Outline)
        .filter(Outline.job_id == job.id, Outline.id == approval.outline_id)
        .first()
    )
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found")

    outline.user_approved = True
    outline.approved_at = datetime.utcnow()
    db.flush()

    existing_payment = (
        db.query(Payment)
        .filter(Payment.job_id == job.id)
        .order_by(Payment.created_at.desc())
        .first()
    )

    if existing_payment and existing_payment.status == "succeeded":
        background.add_task(resume_audiobook_workflow, str(job.id))
        db.commit()
        db.refresh(outline)
        return PaymentIntentResponse(
            payment_intent_id=existing_payment.stripe_payment_intent_id,
            client_secret="",
            amount_cents=existing_payment.amount_cents,
            currency=existing_payment.currency,
        )

    amount_cents = approval.payment_amount_cents
    if amount_cents is None or amount_cents <= 0:
        if job.price_paid_cents and job.price_paid_cents > 0:
            amount_cents = job.price_paid_cents
        else:
            estimate = estimate_job_cost(job.repo_url, job.depth_tier)
            amount_cents = estimate["estimated_cost_cents"]
    if amount_cents <= 0:
        raise HTTPException(
            status_code=400, detail="Unable to determine a valid payment amount"
        )

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
    db.refresh(outline)

    return PaymentIntentResponse(
        payment_intent_id=intent.id,
        client_secret=intent.client_secret,
        amount_cents=intent.amount,
        currency=intent.currency,
    )
