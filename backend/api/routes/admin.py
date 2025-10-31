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
from backend.models.payment import Payment
from backend.api.dependencies import require_admin
from backend.api.schemas.payment import RefundRequest

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


@router.get("/users/{user_id}/jobs")
async def get_user_jobs(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get all jobs for a specific user.

    Requires admin privileges.
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        jobs = db.query(Job).filter(Job.user_id == user_id).order_by(desc(Job.created_at)).all()

        return {
            "jobs": [
                {
                    "id": str(job.id),
                    "repo_url": job.repo_url,
                    "repo_name": job.repo_name,
                    "status": job.status,
                    "depth_tier": job.depth_tier,
                    "price_paid_cents": job.price_paid_cents,
                    "created_at": job.created_at.isoformat() if job.created_at else None,
                }
                for job in jobs
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching jobs for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user jobs"
        )


@router.post("/users/{user_id}/credits")
async def update_user_credits(
    user_id: str,
    credit_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Add or remove credits from a user's account.

    Requires admin privileges.
    
    Request body:
    {
        "amount": 100,
        "operation": "add" or "subtract"
    }
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        amount = credit_data.get("amount")
        operation = credit_data.get("operation")

        if not isinstance(amount, int) or amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be a positive integer"
            )

        if operation not in ["add", "subtract"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation must be 'add' or 'subtract'"
            )

        # Update credits
        if operation == "add":
            user.credits_remaining = (user.credits_remaining or 0) + amount
        else:  # subtract
            new_balance = (user.credits_remaining or 0) - amount
            if new_balance < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient credits"
                )
            user.credits_remaining = new_balance

        db.commit()
        db.refresh(user)

        logger.info(f"Admin {current_user.email} {operation}ed {amount} credits for user {user.email}")

        return {
            "success": True,
            "new_balance": user.credits_remaining
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating credits for user {user_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update credits"
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

        # Query payments with user join for email
        query = db.query(Payment, User).join(User, Payment.user_id == User.id)
        
        # Get total count
        total = query.count()

        # Get paginated results ordered by most recent first
        results = query.order_by(desc(Payment.created_at)).offset(offset).limit(per_page).all()

        # Format response
        payment_list = []
        for payment, user in results:
            payment_list.append({
                "id": str(payment.id),
                "user_id": str(payment.user_id),
                "user_email": user.email,
                "job_id": str(payment.job_id) if payment.job_id else None,
                "amount": payment.amount_cents / 100,  # Convert cents to dollars
                "currency": payment.currency or "usd",
                "status": payment.status,
                "payment_method": payment.payment_method_type,
                "stripe_payment_intent_id": payment.stripe_payment_intent_id,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
            })

        return {
            "payments": payment_list,
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    except Exception as e:
        logger.error(f"Error fetching payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payments"
        )


@router.get("/payments/{payment_id}")
async def get_payment_details(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get detailed information about a specific payment.

    Requires admin privileges.
    """
    try:
        # Query payment with user and job info
        result = db.query(Payment, User, Job).join(
            User, Payment.user_id == User.id
        ).outerjoin(
            Job, Payment.job_id == Job.id
        ).filter(Payment.id == payment_id).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        payment, user, job = result

        # Build detailed response
        payment_details = {
            "id": str(payment.id),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
            },
            "job": None,
            "amount_cents": payment.amount_cents,
            "amount": payment.amount_cents / 100,
            "currency": payment.currency or "usd",
            "status": payment.status,
            "payment_method_type": payment.payment_method_type,
            "stripe_payment_intent_id": payment.stripe_payment_intent_id,
            "stripe_charge_id": payment.stripe_charge_id,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
        }

        # Add job details if payment is associated with a job
        if job:
            payment_details["job"] = {
                "id": str(job.id),
                "repo_url": job.repo_url,
                "repo_name": job.repo_name,
                "status": job.status,
                "depth_tier": job.depth_tier,
            }

        return payment_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment details"
        )


@router.get("/payments/search")
async def search_payments(
    query: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    user_email: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Search and filter payments with advanced criteria.

    Requires admin privileges.
    """
    try:
        per_page = 20
        offset = (page - 1) * per_page

        # Start with base query
        query_obj = db.query(Payment, User).join(User, Payment.user_id == User.id)

        # Apply filters
        if status_filter:
            query_obj = query_obj.filter(Payment.status == status_filter)

        if user_email:
            query_obj = query_obj.filter(User.email.ilike(f"%{user_email}%"))

        if min_amount is not None:
            query_obj = query_obj.filter(Payment.amount_cents >= int(min_amount * 100))

        if max_amount is not None:
            query_obj = query_obj.filter(Payment.amount_cents <= int(max_amount * 100))

        if start_date:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_obj = query_obj.filter(Payment.created_at >= start_dt)

        if end_date:
            from datetime import datetime
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query_obj = query_obj.filter(Payment.created_at <= end_dt)

        if query:
            # Search in payment intent ID or charge ID
            query_obj = query_obj.filter(
                (Payment.stripe_payment_intent_id.ilike(f"%{query}%")) |
                (Payment.stripe_charge_id.ilike(f"%{query}%"))
            )

        # Get total count
        total = query_obj.count()

        # Get paginated results
        results = query_obj.order_by(desc(Payment.created_at)).offset(offset).limit(per_page).all()

        # Format response
        payment_list = []
        for payment, user in results:
            payment_list.append({
                "id": str(payment.id),
                "user_id": str(payment.user_id),
                "user_email": user.email,
                "job_id": str(payment.job_id) if payment.job_id else None,
                "amount": payment.amount_cents / 100,
                "currency": payment.currency or "usd",
                "status": payment.status,
                "payment_method": payment.payment_method_type,
                "stripe_payment_intent_id": payment.stripe_payment_intent_id,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
            })

        return {
            "payments": payment_list,
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    except Exception as e:
        logger.error(f"Error searching payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search payments"
        )


@router.get("/payments/stats")
async def get_payment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Get payment statistics for admin dashboard.

    Requires admin privileges.
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import extract

        # Total revenue (all succeeded payments)
        total_revenue = db.query(func.sum(Payment.amount_cents)).filter(
            Payment.status == 'succeeded'
        ).scalar() or 0

        # Revenue this month
        now = datetime.utcnow()
        first_day_of_month = datetime(now.year, now.month, 1)
        revenue_this_month = db.query(func.sum(Payment.amount_cents)).filter(
            Payment.status == 'succeeded',
            Payment.created_at >= first_day_of_month
        ).scalar() or 0

        # Revenue last month
        if now.month == 1:
            first_day_last_month = datetime(now.year - 1, 12, 1)
            last_day_last_month = datetime(now.year, 1, 1)
        else:
            first_day_last_month = datetime(now.year, now.month - 1, 1)
            last_day_last_month = first_day_of_month

        revenue_last_month = db.query(func.sum(Payment.amount_cents)).filter(
            Payment.status == 'succeeded',
            Payment.created_at >= first_day_last_month,
            Payment.created_at < last_day_last_month
        ).scalar() or 0

        # Total payment count
        total_payments = db.query(func.count(Payment.id)).scalar() or 0

        # Payment count by status
        status_counts = {}
        status_results = db.query(
            Payment.status, func.count(Payment.id)
        ).group_by(Payment.status).all()
        
        for status, count in status_results:
            status_counts[status or 'unknown'] = count

        # Average transaction value
        avg_transaction = db.query(func.avg(Payment.amount_cents)).filter(
            Payment.status == 'succeeded'
        ).scalar() or 0

        # Recent transactions (last 7 days)
        seven_days_ago = now - timedelta(days=7)
        recent_transaction_count = db.query(func.count(Payment.id)).filter(
            Payment.created_at >= seven_days_ago
        ).scalar() or 0

        # Revenue by day for last 30 days (for charts)
        thirty_days_ago = now - timedelta(days=30)
        from sqlalchemy import cast, Date
        daily_revenue = db.query(
            cast(Payment.created_at, Date).label('date'),
            func.sum(Payment.amount_cents).label('revenue')
        ).filter(
            Payment.status == 'succeeded',
            Payment.created_at >= thirty_days_ago
        ).group_by(cast(Payment.created_at, Date)).order_by(cast(Payment.created_at, Date)).all()

        revenue_chart = [
            {
                "date": str(date),
                "revenue": float(revenue / 100) if revenue else 0
            }
            for date, revenue in daily_revenue
        ]

        return {
            "total_revenue": float(total_revenue / 100),
            "revenue_this_month": float(revenue_this_month / 100),
            "revenue_last_month": float(revenue_last_month / 100),
            "total_payments": total_payments,
            "status_counts": status_counts,
            "average_transaction": float(avg_transaction / 100),
            "recent_transaction_count": recent_transaction_count,
            "revenue_chart_30_days": revenue_chart,
        }
    except Exception as e:
        logger.error(f"Error fetching payment stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment statistics"
        )


@router.post("/payments/{payment_id}/refund")
async def refund_payment(
    payment_id: str,
    refund_data: RefundRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Issue a refund for a payment through Stripe.

    Requires admin privileges.

    Request body:
    {
        "amount": 49.99,  // Optional: partial refund amount in dollars
        "reason": "requested_by_customer"  // Optional: duplicate, fraudulent, requested_by_customer
    }
    """
    logger.info(f"Refund request for payment {payment_id} by admin {current_user.email}")
    logger.info(f"Refund data: {refund_data.dict() if refund_data else 'None'}")

    try:
        import stripe
        from backend.config import get_settings

        # Get payment from database
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            logger.error(f"Payment {payment_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        logger.info(f"Payment found: id={payment.id}, status={payment.status}, amount_cents={payment.amount_cents}, stripe_id={payment.stripe_payment_intent_id}")

        if payment.status != 'succeeded':
            logger.error(f"Cannot refund payment with status: {payment.status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot refund payment with status: {payment.status}"
            )

        if not payment.stripe_payment_intent_id:
            logger.error("Payment has no Stripe payment intent ID")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment has no Stripe payment intent ID"
            )

        # Initialize Stripe
        settings = get_settings()
        if not settings.STRIPE_SECRET_KEY:
            logger.error("Stripe secret key not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Stripe not configured"
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY
        logger.info("Stripe initialized")

        # Prepare refund parameters
        refund_params = {
            "payment_intent": payment.stripe_payment_intent_id,
        }

        # Add optional amount (convert dollars to cents)
        if refund_data.amount is not None:
            amount_dollars = refund_data.amount
            if payment.amount_cents is None:
                logger.error("Payment has no amount recorded")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment has no amount recorded"
                )
            if amount_dollars > (payment.amount_cents / 100):
                logger.error(f"Refund amount {amount_dollars} exceeds payment amount {payment.amount_cents / 100}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Refund amount cannot exceed payment amount"
                )
            refund_params["amount"] = int(amount_dollars * 100)
            logger.info(f"Refund amount: {amount_dollars} dollars = {refund_params['amount']} cents")

        # Add optional reason
        if refund_data.reason:
            refund_params["reason"] = refund_data.reason
            logger.info(f"Refund reason: {refund_data.reason}")

        logger.info(f"Creating Stripe refund with params: {refund_params}")

        # Create refund in Stripe
        refund = stripe.Refund.create(**refund_params)
        logger.info(f"Stripe refund created: {refund}")

        # Update payment status in database
        if refund["status"] == "succeeded":
            payment.status = "refunded"
            db.commit()
            logger.info(f"Payment {payment_id} status updated to refunded")

        logger.info(
            f"Admin {current_user.email} issued refund for payment {payment_id}. "
            f"Refund ID: {refund['id']}"
        )

        return {
            "success": True,
            "refund_id": refund["id"],
            "status": refund["status"],
            "amount_refunded": refund["amount"] / 100,
        }

    except stripe.StripeError as e:
        logger.error(f"Stripe error refunding payment {payment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error refunding payment {payment_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process refund"
        )


@router.get("/payments/export")
async def export_payments(
    format: str = Query("csv", regex="^(csv|json)$"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Export payment data in CSV or JSON format.

    Requires admin privileges.
    """
    try:
        from datetime import datetime
        import csv
        import io
        from fastapi.responses import StreamingResponse

        # Build query
        query_obj = db.query(Payment, User).join(User, Payment.user_id == User.id)

        # Apply filters
        if status_filter:
            query_obj = query_obj.filter(Payment.status == status_filter)

        if start_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            query_obj = query_obj.filter(Payment.created_at >= start_dt)

        if end_date:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            query_obj = query_obj.filter(Payment.created_at <= end_dt)

        # Get all results
        results = query_obj.order_by(Payment.created_at).all()

        if format == "csv":
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "Payment ID", "User Email", "Job ID", "Amount", "Currency",
                "Status", "Payment Method", "Stripe Payment Intent ID",
                "Created At", "Completed At"
            ])

            # Write data
            for payment, user in results:
                writer.writerow([
                    str(payment.id),
                    user.email,
                    str(payment.job_id) if payment.job_id else "",
                    payment.amount_cents / 100,
                    payment.currency or "usd",
                    payment.status,
                    payment.payment_method_type or "",
                    payment.stripe_payment_intent_id or "",
                    payment.created_at.isoformat() if payment.created_at else "",
                    payment.completed_at.isoformat() if payment.completed_at else "",
                ])

            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=payments_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                }
            )
        else:  # JSON
            # Create JSON
            payment_list = []
            for payment, user in results:
                payment_list.append({
                    "id": str(payment.id),
                    "user_email": user.email,
                    "user_id": str(payment.user_id),
                    "job_id": str(payment.job_id) if payment.job_id else None,
                    "amount": payment.amount_cents / 100,
                    "currency": payment.currency or "usd",
                    "status": payment.status,
                    "payment_method": payment.payment_method_type,
                    "stripe_payment_intent_id": payment.stripe_payment_intent_id,
                    "created_at": payment.created_at.isoformat() if payment.created_at else None,
                    "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
                })

            import json
            json_data = json.dumps({"payments": payment_list, "total": len(payment_list)}, indent=2)
            
            return StreamingResponse(
                iter([json_data]),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=payments_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                }
            )

    except Exception as e:
        logger.error(f"Error exporting payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export payments"
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
