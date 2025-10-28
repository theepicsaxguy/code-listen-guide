"""
Admin API routes.

Provides admin-only endpoints for:
- Dashboard statistics
- User management
- System monitoring
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.db.session import get_db
from backend.models.user import User
from backend.models.job import Job
from backend.api.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)


@router.get("/dashboard/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get admin dashboard statistics.

    Requires admin privileges.
    """
    try:
        # Count total users
        total_users = db.query(func.count(User.id)).scalar()

        # Count active jobs (not completed or failed)
        active_jobs = db.query(func.count(Job.id)).filter(
            Job.status.in_(['pending', 'analyzing', 'scripting', 'synthesizing', 'post_processing'])
        ).scalar()

        # Calculate monthly revenue (placeholder - would need Payment model)
        revenue_month = 0

        # Calculate storage used (placeholder - would need to sum file sizes)
        storage_used_gb = 0.0

        return {
            "total_users": total_users or 0,
            "active_jobs": active_jobs or 0,
            "revenue_month": revenue_month,
            "storage_used_gb": storage_used_gb,
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard statistics"
        )


@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get paginated list of users.

    Requires admin privileges.
    """
    try:
        per_page = 20
        offset = (page - 1) * per_page

        # Build query
        query = db.query(User)

        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (User.email.ilike(search_filter)) |
                (User.name.ilike(search_filter))
            )

        # Get total count
        total = query.count()

        # Get paginated results
        users = query.order_by(desc(User.created_at)).offset(offset).limit(per_page).all()

        # Format response
        user_list = []
        for user in users:
            user_list.append({
                "id": str(user.id),
                "name": user.name or "Unknown",
                "email": user.email,
                "status": user.subscription_status or "active",
                "credits": user.credits_remaining,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": None,  # Would need to track this
            })

        return {
            "users": user_list,
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users"
        )


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get detailed information about a specific user.

    Requires admin privileges.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return {
            "id": str(user.id),
            "name": user.name or "Unknown",
            "email": user.email,
            "status": user.subscription_status or "active",
            "credits": user.credits_remaining,
            "subscription_tier": user.subscription_tier,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: str,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Update user status (active/suspended).

    Requires admin privileges.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        new_status = status_data.get("status")
        if new_status not in ["active", "suspended", "canceled", "past_due"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value"
            )

        # Update subscription status
        user.subscription_status = new_status
        db.commit()

        logger.info(f"Admin {current_user.email} updated user {user.email} status to {new_status}")

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user status: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )
