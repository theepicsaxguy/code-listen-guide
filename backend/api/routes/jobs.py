"""Job routes for creating and managing audiobook generation jobs."""

import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.api.schemas.job import JobCreate, JobEstimate, JobListResponse, JobResponse
from backend.db.session import get_db
from backend.models.job import Job
from backend.models.user import User
from backend.tasks.audiobook_tasks import start_audiobook_workflow
from backend.tools.db_tools import (
    create_job_record,
    estimate_job_cost as calculate_job_estimate,
    get_job_record,
)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new audiobook generation job for the current user."""
    job = create_job_record(
        db=db,
        user_id=current_user.id,
        repo_url=job_data.repo_url,
        depth_tier=job_data.depth_tier.value,
        git_ref=job_data.git_ref,
    )
    return JobResponse.from_orm(job)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status_filter: Optional[str] = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return a paginated list of jobs for the current user."""
    query = db.query(Job).filter(Job.user_id == current_user.id)
    if status_filter:
        query = query.filter(Job.status == status_filter)
    total = query.count()
    items = (
        query.order_by(Job.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    page = (offset // limit) + 1 if limit else 1
    has_next = offset + limit < total
    return JobListResponse(
        jobs=[JobResponse.from_orm(item) for item in items],
        total=total,
        page=page,
        page_size=limit,
        has_next=has_next,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return job details for the specified job."""
    job = get_job_record(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.from_orm(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a job owned by the current user."""
    job = get_job_record(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return


@router.post("/estimate", response_model=JobEstimate)
async def estimate_job_cost(
    repo_url: str,
    depth_tier: str,
    current_user: User = Depends(get_current_user)
):
    """Estimate cost and timeline for a repository without creating a job."""
    estimate = calculate_job_estimate(repo_url, depth_tier)
    return JobEstimate(**estimate)


@router.post("/{job_id}/start", status_code=status.HTTP_202_ACCEPTED)
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
        raise HTTPException(status_code=400, detail="Job cannot be started in current status")
    background.add_task(start_audiobook_workflow, str(job.id), job.repo_url, job.depth_tier)
    return {"accepted": True}
