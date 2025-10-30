"""Admin routes for agent monitoring and management."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.api.dependencies import require_admin
from backend.api.schemas.job import JobStatus
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.user import User
from backend.models.workflow_checkpoint import WorkflowCheckpoint

router = APIRouter(prefix="/api/v1/admin/agents", tags=["admin", "agents"])
logger = logging.getLogger(__name__)


@router.get("/jobs")
async def list_agent_jobs(
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    List all jobs with their agent execution status.
    Returns jobs with checkpoint information for monitoring.
    """
    query = db.query(Job)
    
    if status:
        query = query.filter(Job.status == status)
    
    total = query.count()
    jobs = query.order_by(desc(Job.updated_at)).offset(offset).limit(limit).all()
    
    # Get checkpoint info for each job
    job_data = []
    for job in jobs:
        # Get latest checkpoint
        checkpoint = (
            db.query(WorkflowCheckpoint)
            .filter(WorkflowCheckpoint.workflow_id == str(job.id))
            .order_by(desc(WorkflowCheckpoint.created_at))
            .first()
        )
        
        # Get user info
        user = db.query(User).filter(User.id == job.user_id).first()
        
        job_info = {
            "id": str(job.id),
            "user_email": user.email if user else "unknown",
            "user_name": user.name if user else "unknown",
            "repo_url": job.repo_url,
            "repo_name": job.repo_name,
            "repo_owner": job.repo_owner,
            "git_ref": job.git_ref,
            "depth_tier": job.depth_tier,
            "status": job.status,
            "progress_percentage": float(job.progress_percentage or 0),
            "current_stage": job.current_stage,
            "estimated_duration_minutes": job.estimated_duration_minutes,
            "estimated_chapters": job.estimated_chapters,
            "price_paid_cents": job.price_paid_cents,
            "llm_cost_cents": job.llm_cost_cents or 0,
            "tts_cost_cents": job.tts_cost_cents or 0,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "updated_at": job.updated_at.isoformat() if job.updated_at else None,
            "error_message": job.error_message,
            "checkpoint": {
                "step": checkpoint.step_id if checkpoint else None,
                "state": checkpoint.state if checkpoint else None,
                "created_at": checkpoint.created_at.isoformat() if checkpoint else None,
            } if checkpoint else None,
        }
        job_data.append(job_info)
    
    return {
        "jobs": job_data,
        "total": total,
        "page": (offset // limit) + 1 if limit else 1,
        "page_size": limit,
        "has_next": offset + limit < total,
    }


@router.get("/jobs/{job_id}")
async def get_agent_job_details(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Get detailed agent execution information for a specific job.
    Includes all checkpoints and stage information.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all checkpoints for this job
    checkpoints = (
        db.query(WorkflowCheckpoint)
        .filter(WorkflowCheckpoint.workflow_id == str(job_id))
        .order_by(WorkflowCheckpoint.created_at)
        .all()
    )
    
    # Get user info
    user = db.query(User).filter(User.id == job.user_id).first()
    
    checkpoint_data = [
        {
            "step": cp.step_id,
            "state": cp.state,
            "created_at": cp.created_at.isoformat(),
        }
        for cp in checkpoints
    ]
    
    # Parse stages from checkpoints and metadata
    stages = []
    if job.metadata_json and isinstance(job.metadata_json, dict):
        stages_data = job.metadata_json.get("stages", [])
        if stages_data:
            stages = stages_data
    
    # If no stages in metadata, derive from checkpoints
    if not stages and checkpoints:
        stage_names = ["analysis", "outline", "approval", "scripting", "audio", "postprocessing"]
        for stage_name in stage_names:
            matching_cp = next((cp for cp in checkpoints if stage_name in cp.step_id.lower()), None)
            if matching_cp:
                stages.append({
                    "name": stage_name,
                    "status": "completed" if job.status == "completed" else "running" if job.current_stage == stage_name else "pending",
                    "started_at": matching_cp.created_at.isoformat(),
                    "state": matching_cp.state,
                })
    
    return {
        "id": str(job.id),
        "user": {
            "id": str(user.id) if user else None,
            "email": user.email if user else None,
            "name": user.name if user else None,
        },
        "repo_url": job.repo_url,
        "repo_name": job.repo_name,
        "repo_owner": job.repo_owner,
        "git_ref": job.git_ref,
        "depth_tier": job.depth_tier,
        "status": job.status,
        "progress_percentage": float(job.progress_percentage or 0),
        "current_stage": job.current_stage,
        "estimated_duration_minutes": job.estimated_duration_minutes,
        "estimated_chapters": job.estimated_chapters,
        "price_paid_cents": job.price_paid_cents,
        "llm_cost_cents": job.llm_cost_cents or 0,
        "tts_cost_cents": job.tts_cost_cents or 0,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "error_message": job.error_message,
        "checkpoints": checkpoint_data,
        "stages": stages,
        "metadata": job.metadata_json,
    }


@router.get("/stats")
async def get_agent_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Get aggregate statistics about agent execution.
    """
    # Total jobs
    total_jobs = db.query(func.count(Job.id)).scalar()
    
    # Jobs by status
    running_jobs = db.query(func.count(Job.id)).filter(
        Job.status.in_(["analyzing", "scripting", "synthesizing", "post_processing"])
    ).scalar()
    
    completed_jobs = db.query(func.count(Job.id)).filter(Job.status == "completed").scalar()
    failed_jobs = db.query(func.count(Job.id)).filter(Job.status == "failed").scalar()
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_jobs = db.query(func.count(Job.id)).filter(Job.created_at >= yesterday).scalar()
    
    # Average costs
    avg_llm_cost = db.query(func.avg(Job.llm_cost_cents)).filter(Job.llm_cost_cents.isnot(None)).scalar() or 0
    avg_tts_cost = db.query(func.avg(Job.tts_cost_cents)).filter(Job.tts_cost_cents.isnot(None)).scalar() or 0
    
    # Total checkpoints
    total_checkpoints = db.query(func.count(WorkflowCheckpoint.id)).scalar()
    
    return {
        "total_jobs": total_jobs or 0,
        "running_jobs": running_jobs or 0,
        "completed_jobs": completed_jobs or 0,
        "failed_jobs": failed_jobs or 0,
        "pending_jobs": (total_jobs or 0) - (running_jobs or 0) - (completed_jobs or 0) - (failed_jobs or 0),
        "recent_jobs_24h": recent_jobs or 0,
        "avg_llm_cost_cents": float(avg_llm_cost),
        "avg_tts_cost_cents": float(avg_tts_cost),
        "total_checkpoints": total_checkpoints or 0,
    }


@router.get("/jobs/{job_id}/logs")
async def get_job_logs(
    job_id: UUID,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Get execution logs for a specific job from checkpoints.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    checkpoints = (
        db.query(WorkflowCheckpoint)
        .filter(WorkflowCheckpoint.workflow_id == str(job_id))
        .order_by(desc(WorkflowCheckpoint.created_at))
        .limit(limit)
        .all()
    )
    
    logs = []
    for cp in reversed(checkpoints):
        logs.append({
            "timestamp": cp.created_at.isoformat(),
            "step": cp.step_id,
            "message": f"Checkpoint reached: {cp.step_id}",
            "state": cp.state,
        })
    
    # Add job status changes
    logs.append({
        "timestamp": job.created_at.isoformat() if job.created_at else None,
        "step": "created",
        "message": f"Job created for {job.repo_url}",
        "metadata": {"depth_tier": job.depth_tier},
    })
    
    if job.error_message:
        logs.append({
            "timestamp": job.updated_at.isoformat() if job.updated_at else None,
            "step": "error",
            "message": job.error_message,
            "metadata": {"status": job.status},
        })
    
    return {
        "job_id": str(job_id),
        "logs": sorted(logs, key=lambda x: x["timestamp"]),
        "total": len(logs),
    }


@router.post("/jobs/{job_id}/retry")
async def retry_failed_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    """
    Retry a failed job from the last successful checkpoint.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != "failed":
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed jobs. Current status: {job.status}"
        )
    
    # Reset job to pending
    job.status = "pending"
    job.error_message = None
    job.progress_percentage = 0
    job.current_stage = None
    
    db.commit()
    db.refresh(job)
    
    # TODO: Trigger workflow restart from last checkpoint
    logger.info(f"Admin {current_admin.email} retried job {job_id}")
    
    return {
        "success": True,
        "message": "Job queued for retry",
        "job_id": str(job_id),
    }
