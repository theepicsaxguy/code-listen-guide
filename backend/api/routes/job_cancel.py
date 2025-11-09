"""Job cancellation endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from backend.api.dependencies import get_current_user
from backend.api.schemas.job import JobStatus
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.user import User
from backend.tasks.audiobook_tasks import cancel_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/{job_id}/cancel", operation_id="cancelJobDuplicate")
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
    if job.status in ["completed", "failed"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Update job status to cancelled
    job.status = "failed"
    job.error_message = "Job cancelled by user"
    job.progress_percentage = 0.0
    
    db.commit()
    db.refresh(job)
    
    # Send signal to running workflow to stop processing
    # This will call the workflow's cancel() method if it's currently active
    workflow_cancelled = cancel_workflow(job_id)
    
    if workflow_cancelled:
        logger.info(f"Active workflow cancelled for job {job_id}")
    else:
        logger.info(f"No active workflow found for job {job_id}, database updated only")
    
    return {
        "success": True,
        "message": "Job cancelled successfully",
        "job_id": str(job.id),
        "status": job.status,
        "workflow_cancelled": workflow_cancelled
    }
