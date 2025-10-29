"""Admin user management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from backend.db.session import get_db
from backend.models.user import User
from backend.models.job import Job
from backend.utils.auth import get_current_admin_user

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


class CreditUpdate(BaseModel):
    """Credit update request."""
    amount: int
    operation: str  # "add" or "subtract"


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Get detailed user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "status": user.status if hasattr(user, 'status') else "active",
        "credits": user.credits_remaining,
        "subscription_tier": user.subscription_tier,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if hasattr(user, 'last_login') and user.last_login else None,
    }


@router.get("/{user_id}/jobs")
async def get_user_jobs(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Get all jobs for a specific user."""
    jobs = db.query(Job).filter(Job.user_id == user_id).order_by(Job.created_at.desc()).all()
    
    return {
        "jobs": [
            {
                "id": str(job.id),
                "repo_name": job.repo_name,
                "repo_owner": job.repo_owner,
                "repo_url": job.repo_url,
                "status": job.status,
                "depth_tier": job.depth_tier,
                "price_paid_cents": job.price_paid_cents or 0,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            }
            for job in jobs
        ]
    }


@router.post("/{user_id}/credits")
async def update_user_credits(
    user_id: str,
    update: CreditUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Add or remove credits from a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update.operation == "add":
        user.credits_remaining += update.amount
    elif update.operation == "subtract":
        if user.credits_remaining < update.amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient credits. User has {user.credits_remaining} credits."
            )
        user.credits_remaining -= update.amount
    else:
        raise HTTPException(status_code=400, detail="Invalid operation. Use 'add' or 'subtract'")
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "new_balance": user.credits_remaining
    }
