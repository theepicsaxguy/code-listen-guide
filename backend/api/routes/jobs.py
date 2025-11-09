"""Job routes for creating and managing audiobook generation jobs."""

import logging
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.api.dependencies import get_current_user
from backend.api.schemas.job import (
    JobCreate,
    JobEstimate,
    JobEstimateRequest,
    JobListResponse,
    JobResponse,
)
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.user import User
from backend.models.episode import Episode
from backend.tasks.audiobook_tasks import start_audiobook_workflow, cancel_workflow
from backend.tools.db_tools import (
    create_job_record,
    estimate_job_cost as calculate_job_estimate,
    get_job_record,
)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    operation_id="createJob",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new audiobook generation job."""
    logger.debug(f"Creating job with data: repo_url={job_data.repo_url}, depth_tier={job_data.depth_tier}, git_ref={job_data.git_ref}")

    # Parse GitHub URL to extract owner and repo name
    repo_parts = str(job_data.repo_url).rstrip('/').split('/')
    repo_owner = repo_parts[-2] if len(repo_parts) >= 2 else "unknown"
    repo_name = repo_parts[-1].replace('.git', '') if repo_parts else "unknown"

    logger.debug(f"Parsed repository: owner={repo_owner}, name={repo_name}")
    job = create_job_record(
        db=db,
        user_id=current_user.id,
        repo_url=job_data.repo_url,
        depth_tier=job_data.depth_tier.value,
        git_ref=job_data.git_ref,
    )

    # Avoid relying on ORM relationship population (relationships are currently commented out).
    # Manually construct response to prevent AttributeError when Pydantic attempts to access missing attributes.
    return JobResponse(
        id=job.id,
        user_id=job.user_id,
        repo_url=job.repo_url,
        repo_name=job.repo_name,
        repo_owner=job.repo_owner,
        git_ref=job.git_ref,
        depth_tier=job.depth_tier,
        status=job.status,
        current_stage=job.current_stage,
        progress_percentage=job.progress_percentage,
        error_message=job.error_message,
        estimated_duration_minutes=job.estimated_duration_minutes,
        estimated_chapters=job.estimated_chapters,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        chapters=[],  # relationships not yet active
        deliverables=[],  # relationships not yet active
    )


@router.get("", operation_id="listJobs", response_model=JobListResponse)
async def list_jobs(
    status_filter: Optional[str] = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a paginated list of jobs for the current user."""
    # Build base query
    query = db.query(Job).filter(Job.user_id == current_user.id)
    if status_filter:
        query = query.filter(Job.status == status_filter)
    
    # Count is optimized by composite index (ix_jobs_user_status)
    total = query.count()
    items = query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()
    page = (offset // limit) + 1 if limit else 1
    has_next = offset + limit < total
    jobs_serialized = [
        JobResponse(
            id=item.id,
            user_id=item.user_id,
            repo_url=item.repo_url,
            repo_name=item.repo_name,
            repo_owner=item.repo_owner,
            git_ref=item.git_ref,
            depth_tier=item.depth_tier,
            status=item.status,
            current_stage=item.current_stage,
            progress_percentage=item.progress_percentage,
            error_message=item.error_message,
            estimated_duration_minutes=item.estimated_duration_minutes,
            estimated_chapters=item.estimated_chapters,
            created_at=item.created_at,
            started_at=item.started_at,
            completed_at=item.completed_at,
            chapters=[],
            deliverables=[],
        )
        for item in items
    ]
    return JobListResponse(
        jobs=jobs_serialized,
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
    )


@router.get("/{job_id}", operation_id="getJob", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return job details for the specified job."""
    job = get_job_record(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # Use model_validate for Pydantic v2, fallback to from_orm for v1
    return JobResponse(
        id=job.id,
        user_id=job.user_id,
        repo_url=job.repo_url,
        repo_name=job.repo_name,
        repo_owner=job.repo_owner,
        git_ref=job.git_ref,
        depth_tier=job.depth_tier,
        status=job.status,
        current_stage=job.current_stage,
        progress_percentage=job.progress_percentage,
        error_message=job.error_message,
        estimated_duration_minutes=job.estimated_duration_minutes,
        estimated_chapters=job.estimated_chapters,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        chapters=[],
        deliverables=[],
    )


@router.delete("/{job_id}", operation_id="deleteJob", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a job owned by the current user."""
    job = get_job_record(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return


@router.post("/estimate", operation_id="estimateCost", response_model=JobEstimate)
async def estimate_job_cost(
    estimate_request: JobEstimateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Estimate cost and timeline for a repository without creating a job.
    
    This endpoint:
    1. Parses the repository to get file contents
    2. Applies user's scope selection (files, exclusions)
    3. Calculates real token counts using tiktoken
    4. Returns detailed cost breakdown
    """
    from backend.services.token_estimator import TokenEstimator
    from backend.tools.git_tools import clone_repository
    import shutil
    from pathlib import Path
    import tempfile
    
    # Clone repository
    repo_path = None
    try:
        repo_path = clone_repository(str(estimate_request.repo_url))
        
        # Read file contents based on scope selection
        file_contents = []
        repo_path_obj = Path(repo_path)
        
        # Get all files or selected files
        if estimate_request.selected_files:
            # User selected specific files
            for file_path in estimate_request.selected_files:
                full_path = repo_path_obj / file_path
                if full_path.exists() and full_path.is_file():
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            file_contents.append(f.read())
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
        else:
            # Include all files (excluding patterns)
            excluded_patterns = estimate_request.excluded_patterns or [
                '*.test.ts', '*.test.js', '*.spec.ts', '*.spec.js',
                'node_modules/**', '__pycache__/**', '.git/**'
            ]
            
            for file_path in repo_path_obj.rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(repo_path_obj)
                    
                    # Check exclusion patterns
                    from fnmatch import fnmatch
                    should_exclude = any(
                        fnmatch(str(rel_path), pattern) 
                        for pattern in excluded_patterns
                    )
                    
                    if not should_exclude:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                file_contents.append(f.read())
                        except Exception as e:
                            logger.warning(f"Could not read {file_path}: {e}")
        
        # Estimate tokens and costs
        estimator = TokenEstimator()
        cost_breakdown = estimator.estimate_job_cost(
            file_contents,
            depth_tier=estimate_request.depth_tier.value,
            selected_files=estimate_request.selected_files,
            excluded_patterns=estimate_request.excluded_patterns,
        )
        
        return JobEstimate(
            estimated_cost_cents=cost_breakdown['total_cost_cents'],
            estimated_duration_minutes=cost_breakdown['estimated_duration_minutes'],
            estimated_chapters=cost_breakdown['estimated_episodes'],
            depth_tier=estimate_request.depth_tier.value,
            llm_tokens=cost_breakdown['llm_tokens'],
            tts_chars=cost_breakdown['tts_chars'],
            llm_cost_cents=cost_breakdown['llm_cost_cents'],
            tts_cost_cents=cost_breakdown['tts_cost_cents'],
            total_cost_cents=cost_breakdown['total_cost_cents'],
        )
        
    finally:
        # Cleanup cloned repository
        if repo_path:
            try:
                sandbox_dir = Path(repo_path).parent
                shutil.rmtree(sandbox_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Failed to cleanup repository: {e}")


@router.post("/{job_id}/start", operation_id="startJob", status_code=status.HTTP_202_ACCEPTED)
async def start_job(
    job_id: uuid.UUID,
    background: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job_record(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in {"pending", "waiting_approval", "paid"}:
        raise HTTPException(
            status_code=400, detail="Job cannot be started in current status"
        )
    background.add_task(
        start_audiobook_workflow, str(job.id), job.repo_url, job.depth_tier
    )
    return {"accepted": True}


@router.post("/{job_id}/episodes/approve", operation_id="approveEpisodes", status_code=status.HTTP_200_OK)
async def approve_episodes(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Approve episode outline and transition job to scripting phase.
    
    This endpoint transitions the job from `waiting_episode_approval` to `scripting`,
    allowing the workflow to proceed with dialogue generation.
    """
    job = get_job_record(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify episodes exist
    episodes = db.query(Episode).filter(Episode.job_id == str(job_id)).all()
    if not episodes:
        raise HTTPException(
            status_code=400,
            detail="No episodes found for this job. Please plan episodes first."
        )
    
    # Check current status
    if job.status not in {"waiting_episode_approval", "planning"}:
        if job.status == "scripting" or job.status == "running":
            raise HTTPException(
                status_code=400,
                detail=f"Job already approved and in progress (status: {job.status})"
            )
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve episodes for job with status: {job.status}"
        )
    
    # Transition to scripting status
    job.status = "scripting"
    job.current_stage = "episode_approval_complete"
    db.commit()
    db.refresh(job)
    
    logger.info(f"User {current_user.email} approved {len(episodes)} episodes for job {job_id}")
    
    return {
        "success": True,
        "message": f"Approved {len(episodes)} episodes",
        "episode_count": len(episodes),
        "job_status": job.status,
    }


@router.post("/{job_id}/cancel", operation_id="cancelJob", status_code=status.HTTP_200_OK)
async def cancel_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a running job.
    
    Only the job owner can cancel their jobs.
    Cannot cancel already completed or failed jobs.
    """
    job = get_job_record(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if job is in a cancellable state
    if job.status in {"completed", "failed"}:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel job with status: {job.status}"
        )
    
    # Update job status to failed with cancellation message
    job.status = "failed"
    job.error_message = "Job canceled by user"
    
    db.commit()
    db.refresh(job)
    
    # Send signal to workflow to gracefully stop processing
    # This calls the workflow's cancel() method if it's currently active
    workflow_cancelled = cancel_workflow(str(job.id))
    
    if workflow_cancelled:
        logger.info(f"Active workflow cancelled for job {job_id}")
    else:
        logger.info(f"No active workflow found for job {job_id}, database updated only")
    
    logger.info(f"User {current_user.email} canceled job {job_id}")
    
    return {
        "success": True,
        "message": "Job canceled successfully",
        "job_id": str(job.id),
        "workflow_cancelled": workflow_cancelled
    }
