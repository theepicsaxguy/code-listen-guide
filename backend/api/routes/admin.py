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

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
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


@router.get("/jobs")
async def get_all_jobs(
    page: int = Query(1, ge=1),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get all jobs with admin view.

    Requires admin privileges.
    """
    try:
        per_page = 20
        offset = (page - 1) * per_page

        query = db.query(Job)

        if status_filter:
            query = query.filter(Job.status == status_filter)

        total = query.count()
        jobs = query.order_by(desc(Job.created_at)).offset(offset).limit(per_page).all()

        job_list = []
        for job in jobs:
            job_list.append({
                "id": str(job.id),
                "user_id": str(job.user_id),
                "repo_url": job.repo_url,
                "repo_name": job.repo_name,
                "status": job.status,
                "progress_percentage": job.progress_percentage,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "error_message": job.error_message,
            })

        return {
            "jobs": job_list,
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch jobs"
        )


@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get audit logs for admin actions.

    Requires admin privileges.

    Note: This is a placeholder. Implement proper audit logging model.
    """
    # Placeholder implementation
    return {
        "logs": [],
        "total": 0,
        "page": page,
        "per_page": 20,
    }


@router.get("/settings")
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get system settings.

    Requires admin privileges.
    """
    # Placeholder - return basic system info
    return {
        "rate_limits": {
            "enabled": True,
            "requests_per_minute": 60,
        },
        "features": {
            "user_registration": True,
            "payment_processing": True,
        },
        "system": {
            "version": "1.0.0",
            "environment": "production",
        }
    }


@router.patch("/settings")
async def update_settings(
    settings_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Update system settings.

    Requires admin privileges.
    """
    # Placeholder implementation
    logger.info(f"Admin {current_user.email} updated settings: {settings_data}")
    return {"success": True}


@router.get("/payments")
async def get_payments(
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get all payments with pagination.

    Requires admin privileges.
    """
    try:
        per_page = 20
        offset = (page - 1) * per_page

        # TODO: Implement Payment model and queries
        # For now, return empty list
        return {
            "payments": [],
            "total": 0,
            "page": page,
            "per_page": per_page,
        }
    except Exception as e:
        logger.error(f"Error fetching payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payments"
        )


@router.get("/content")
async def get_content(
    page: int = Query(1, ge=1),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get content (jobs) for admin content management.

    This endpoint is an alias for /admin/jobs used by the content management page.

    Requires admin privileges.
    """
    # Delegate to the jobs endpoint
    return await get_all_jobs(page=page, status_filter=status_filter, db=db, current_user=current_user)


@router.get("/support/tickets")
async def get_support_tickets(
    page: int = Query(1, ge=1),
    status_filter: Optional[str] = Query(None, alias="status"),
    priority_filter: Optional[str] = Query(None, alias="priority"),
    category_filter: Optional[str] = Query(None, alias="category"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get support tickets with pagination and filtering.

    Requires admin privileges.

    Note: This is a placeholder. Implement proper SupportTicket model.
    """
    try:
        # Placeholder implementation
        return {
            "tickets": [],
            "total": 0,
            "page": page,
            "per_page": 20,
        }
    except Exception as e:
        logger.error(f"Error fetching support tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch support tickets"
        )


@router.get("/support/tickets/{ticket_id}")
async def get_support_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get a specific support ticket with all messages.

    Requires admin privileges.
    """
    try:
        # Placeholder implementation
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch ticket"
        )


@router.post("/support/tickets/{ticket_id}/reply")
async def reply_to_ticket(
    ticket_id: str,
    reply_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Reply to a support ticket.

    Requires admin privileges.
    """
    try:
        content = reply_data.get("content")
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is required"
            )

        # Placeholder implementation
        logger.info(f"Admin {current_user.email} replied to ticket {ticket_id}")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replying to ticket {ticket_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reply to ticket"
        )


@router.patch("/support/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: str,
    status_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Update support ticket status.

    Requires admin privileges.
    """
    try:
        new_status = status_data.get("status")
        if new_status not in ["open", "in_progress", "waiting", "resolved", "closed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value"
            )

        # Placeholder implementation
        logger.info(f"Admin {current_user.email} updated ticket {ticket_id} status to {new_status}")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ticket status"
        )


@router.get("/support/canned-replies")
async def get_canned_replies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get canned reply templates for support tickets.

    Requires admin privileges.
    """
    try:
        # Placeholder implementation with some common replies
        return {
            "replies": [
                {
                    "id": "1",
                    "title": "Job Processing",
                    "content": "Your audiobook is currently being processed. This typically takes 15-30 minutes depending on repository size. We'll notify you when it's complete.",
                    "category": "technical"
                },
                {
                    "id": "2",
                    "title": "Payment Confirmation",
                    "content": "We've received your payment successfully. Your credits have been added to your account.",
                    "category": "billing"
                },
                {
                    "id": "3",
                    "title": "General Thanks",
                    "content": "Thank you for contacting support. We're here to help! Is there anything else we can assist you with?",
                    "category": "other"
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching canned replies: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch canned replies"
        )
