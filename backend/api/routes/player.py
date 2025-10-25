"""Public player routes for accessing audiobooks via shareable links."""

from datetime import datetime
from typing import Any, Dict
from urllib.parse import urlparse
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.schemas.chapter import ChapterListResponse, ChapterResponse
from backend.api.schemas.job import JobResponse
from backend.config import get_settings
from backend.db.session import get_db
from backend.models.chapter import Chapter
from backend.models.deliverable import Deliverable
from backend.models.job import Job
from backend.services.storage import generate_presigned_url

router = APIRouter(prefix="/api/v1/player", tags=["player"])
settings = get_settings()


@router.get("/{job_id}")
async def get_audiobook_player_data(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Return job metadata, chapter list, and deliverable manifest."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    chapters = (
        db.query(Chapter)
        .filter(Chapter.job_id == job_id)
        .order_by(Chapter.chapter_number.asc())
        .all()
    )
    deliverables = (
        db.query(Deliverable)
        .filter(Deliverable.job_id == job_id)
        .order_by(Deliverable.created_at.desc())
        .all()
    )

    total_duration = sum(ch.audio_duration_seconds or 0 for ch in chapters)

    return {
        "job": JobResponse.from_orm(job),
        "chapters": ChapterListResponse(
            chapters=[ChapterResponse.from_orm(chapter) for chapter in chapters],
            total_chapters=len(chapters),
            total_duration_seconds=total_duration,
        ),
        "deliverables": [
            {
                "id": str(deliverable.id),
                "file_type": deliverable.file_type,
                "file_url": deliverable.file_url,
                "created_at": deliverable.created_at.isoformat() if isinstance(deliverable.created_at, datetime) else None,
            }
            for deliverable in deliverables
        ],
    }


@router.get("/{job_id}/download/{deliverable_type}")
async def download_deliverable(
    job_id: uuid.UUID,
    deliverable_type: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Return a signed URL for downloading the requested deliverable."""
    deliverable = (
        db.query(Deliverable)
        .filter(Deliverable.job_id == job_id, Deliverable.file_type == deliverable_type)
        .order_by(Deliverable.created_at.desc())
        .first()
    )
    if not deliverable:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deliverable not found")

    parsed = urlparse(deliverable.file_url)
    if parsed.scheme.startswith("http") and parsed.netloc and parsed.path:
        bucket_host = f"{settings.s3_bucket_name}." if settings.s3_bucket_name else ""
        if bucket_host and bucket_host in parsed.netloc:
            s3_key = parsed.path.lstrip("/")
            try:
                signed_url = await generate_presigned_url(s3_key)
            except Exception:  # noqa: BLE001
                signed_url = deliverable.file_url
        else:
            signed_url = deliverable.file_url
    else:
        signed_url = deliverable.file_url

    return {"download_url": signed_url}
