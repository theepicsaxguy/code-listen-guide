"""Job cancellation endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.job import Job, JobStatus
from backend.models.user import User
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a running job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify ownership
    if str(job.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to cancel this job")
    
    # Check if job can be cancelled
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Update job status to cancelled
    job.status = JobStatus.FAILED
    job.error_message = "Job cancelled by user"
    job.progress_percentage = 0.0
    
    db.commit()
    db.refresh(job)
    
    # TODO: Send signal to running workflow to stop processing
    # This would typically involve:
    # 1. Publishing a cancellation event to a message queue
    # 2. The workflow executor checking for cancellation signals
    # 3. Cleaning up any in-progress resources (temp files, API calls, etc.)
    
    return {
        "success": True,
        "message": "Job cancelled successfully",
        "job_id": str(job.id),
        "status": job.status
    }
