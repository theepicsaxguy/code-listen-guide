"""Episode related API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.session import get_db
from backend.models.episode import Episode
from backend.api.schemas.episode import EpisodeResponse, EpisodesListResponse

# TODO: integrate auth dependency when user system active
def get_current_user_optional():  # placeholder
    return None

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("/job/{job_id}", response_model=EpisodesListResponse, status_code=status.HTTP_200_OK)
def list_job_episodes(
    job_id: str,
    db: Session = Depends(get_db),
    _user = Depends(get_current_user_optional),  # noqa: B008
):
    """Return all episodes for a job (ordered by episode_number)."""
    episodes: List[Episode] = (
        db.query(Episode)
        .filter(Episode.job_id == job_id)
        .order_by(Episode.episode_number.asc())
        .all()
    )
    return EpisodesListResponse(episodes=episodes, total=len(episodes))


@router.get("/{episode_id}", response_model=EpisodeResponse, status_code=status.HTTP_200_OK)
def get_episode(
    episode_id: str,
    db: Session = Depends(get_db),
    _user = Depends(get_current_user_optional),  # noqa: B008
):
    episode: Episode | None = db.query(Episode).get(episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode
