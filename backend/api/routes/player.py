"""
Public player routes for accessing audiobooks via shareable links.

Routes are defined but implementation pending.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from backend.api.schemas.job import JobResponse
from backend.api.schemas.chapter import ChapterListResponse
from backend.db.session import get_db
from backend.models.job import Job

router = APIRouter(prefix="/api/v1/player", tags=["player"])


@router.get("/{job_id}")
async def get_audiobook_player_data(
    job_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get audiobook data for player (public endpoint).

    Note: This is a public endpoint - no authentication required.
    Optional access token can be added for private audiobooks.
    """
    raise HTTPException(status_code=501, detail="Not yet implemented")


@router.get("/{job_id}/download/{deliverable_type}")
async def download_deliverable(
    job_id: uuid.UUID,
    deliverable_type: str,
    db: Session = Depends(get_db)
):
    """
    Download a specific deliverable.

    Implementation: Generate pre-signed S3 URL and redirect.
    """
    raise HTTPException(status_code=501, detail="Not yet implemented")
