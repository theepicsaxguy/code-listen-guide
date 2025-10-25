"""
Outline routes for generating and managing chapter outlines.

Routes are defined but implementation pending.
Use backend/agents/outline_agent.py for actual outline generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from backend.api.schemas.outline import OutlineResponse, OutlineUpdate, OutlineApprove
from backend.api.schemas.payment import PaymentIntentResponse
from backend.db.session import get_db
from backend.models.user import User
from backend.models.job import Job
from backend.models.outline import Outline
from backend.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/jobs/{job_id}/outline", tags=["outlines"])


@router.post("", response_model=OutlineResponse, status_code=status.HTTP_201_CREATED)
async def generate_outline(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate chapter outline for a job.

    Implementation: Use backend/agents/outline_agent.py for generation.
    """
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.put("", response_model=OutlineResponse)
async def update_outline(
    job_id: uuid.UUID,
    outline_update: OutlineUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update outline with user modifications."""
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.post("/approve", response_model=PaymentIntentResponse)
async def approve_outline(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve outline and create payment intent.

    Note: After payment succeeds (webhook), trigger Microsoft Agent Framework workflow.
    """
    raise HTTPException(status_code=501, detail="Not yet implemented")
