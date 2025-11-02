"""Episode related API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.session import get_db
from backend.models.episode import Episode, EpisodeStatus
from backend.models.job import Job
from backend.api.schemas.episode import EpisodeResponse, EpisodesListResponse
from backend.services.dependency_analyzer import DependencyAnalyzer
from backend.config import get_settings
from sqlalchemy import func
import math
import uuid

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


@router.post("/job/{job_id}/plan", response_model=EpisodesListResponse, status_code=status.HTTP_201_CREATED)
def plan_episodes(
    job_id: str,
    db: Session = Depends(get_db),
    _user = Depends(get_current_user_optional),  # noqa: B008
):
    """Generate initial episode plan for a job.

    Idempotent: if episodes already exist for the job, returns them without
    regenerating (future: add force parameter / revisioning).
    """
    settings = get_settings()
    if not settings.feature_episode_planning:
        raise HTTPException(status_code=403, detail="Episode planning feature disabled")

    job: Job | None = db.query(Job).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = (
        db.query(Episode)
        .filter(Episode.job_id == job_id)
        .order_by(Episode.episode_number.asc())
        .all()
    )
    if existing:
        return EpisodesListResponse(episodes=existing, total=len(existing))

    # Determine selected files from job metadata if present
    selected_files = []
    if getattr(job, "selected_files", None):  # job may not yet have this field in earlier migrations
        selected_files = job.selected_files or []

    if not selected_files:
        # Fallback: cannot plan without scope selection for MVP
        raise HTTPException(status_code=400, detail="Job has no selected files scope to plan episodes")

    analyzer = DependencyAnalyzer(repo_root=job.metadata.get("local_repo_path", "."), primary_language=getattr(job, "primary_language", None))  # type: ignore[attr-defined]
    cluster_dicts = analyzer.plan_episodes(selected_files)

    # Heuristic: each cluster becomes an episode
    episodes: list[Episode] = []
    for idx, cluster in enumerate(cluster_dicts, start=1):
        # Flatten file list length for duration heuristic (approx 3 mins per file baseline)
        files = [f for files in cluster.values() for f in files]
        est_duration = int(math.ceil(len(files) * 3)) or 5
        ep = Episode(
            id=uuid.uuid4(),
            job_id=job_id,
            episode_number=idx,
            title=f"Episode {idx}",
            narrative_theme="Initial thematic grouping (auto)",
            file_clusters=cluster,
            dependency_graph=None,
            architectural_boundary=None,
            conversation_hooks=["Explain key relationships", "Discuss trade-offs"],
            learning_objectives=["Understand grouped files purpose"],
            goals=["Refine in editor"],
            dependency_inputs=[],
            dependency_outputs=[],
            depends_on=[f"Episode {idx-1}" ] if idx > 1 else [],
            leads_to=[],
            estimated_duration_minutes=est_duration,
            estimated_tokens=None,
            status=EpisodeStatus.PLANNING,
        )
        episodes.append(ep)
        db.add(ep)

    db.commit()

    # Post-process leads_to after all created
    if len(episodes) > 1:
        for i, ep in enumerate(episodes[:-1]):
            ep.leads_to = [episodes[i+1].id.hex]
        db.commit()

    return EpisodesListResponse(episodes=episodes, total=len(episodes))
