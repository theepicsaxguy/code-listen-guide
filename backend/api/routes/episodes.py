"""Episode related API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.db.session import get_db
from backend.models.episode import Episode, EpisodeStatus
from backend.models.job import Job
from backend.api.schemas.episode import EpisodeResponse, EpisodesListResponse
from backend.services.dependency_analyzer import DependencyAnalyzer, ClusterPlan
from backend.services.episode_planner import plan_episodes_from_clusters
from math import ceil
from backend.config import get_settings
from sqlalchemy import func
import math
import uuid
import asyncio

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

    # Get repository path from metadata
    metadata = getattr(job, "metadata_json", None) or {}
    repo_root = metadata.get("local_repo_path", ".")
    primary_language = getattr(job, "primary_language", None)

    # Build dependency graph and clusters
    analyzer = DependencyAnalyzer(repo_root=repo_root, primary_language=primary_language)
    dependency_graph = analyzer.build_import_graph(selected_files)
    clusters = analyzer.cluster_graph(dependency_graph)
    
    # Identify architectural layers
    architectural_layers = analyzer.identify_architectural_layers(clusters)
    
    # Prepare repository context for LLM
    repo_context = {
        "repo_name": job.repo_name,
        "repo_owner": job.repo_owner,
        "depth_tier": job.depth_tier,
    }

    # Generate LLM-based episode plans
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        episode_plans = loop.run_until_complete(
            plan_episodes_from_clusters(clusters, dependency_graph, architectural_layers, repo_context)
        )
    finally:
        loop.close()

    # Cost/token allocation heuristic: distribute job.estimated_total_tokens across clusters proportionally
    total_tokens = getattr(job, "estimated_total_tokens", None)
    cluster_sizes = [len(cluster.files) for cluster in clusters]
    size_sum = sum(cluster_sizes) or 1

    # Create episode records with LLM-generated metadata
    episodes: list[Episode] = []
    for idx, (cluster, cluster_size, plan) in enumerate(zip(clusters, cluster_sizes, episode_plans), start=1):
        # Flatten file list length for duration heuristic (approx 3 mins per file baseline)
        files = sorted(cluster.files)
        est_duration = int(math.ceil(len(files) * 3)) or 5
        est_tokens = None
        if total_tokens:
            proportional = total_tokens * (cluster_size / size_sum)
            # Add small overhead for dialogue connective tissue
            est_tokens = int(ceil(proportional * 1.15))
        
        # Extract cluster-specific dependency graph
        cluster_deps = {f: deps for f, deps in dependency_graph.items() if f in cluster.files}
        
        # Find architectural boundary for this cluster
        arch_boundary = None
        for layer_name, layer_cluster in architectural_layers.items():
            if cluster.files.intersection(layer_cluster.files):
                arch_boundary = layer_name
                break

        # Convert cluster to dict format for JSONB storage
        cluster_dict = {f"cluster_{idx}": files}

        ep = Episode(
            id=uuid.uuid4(),
            job_id=job_id,
            episode_number=idx,
            title=plan["title"],
            narrative_theme=plan["narrative_theme"],
            file_clusters=cluster_dict,
            dependency_graph=cluster_deps,
            architectural_boundary=arch_boundary,
            conversation_hooks=plan["conversation_hooks"],
            learning_objectives=plan["learning_objectives"],
            goals=plan.get("learning_objectives", []),  # Use learning objectives as goals
            dependency_inputs=[],
            dependency_outputs=[],
            depends_on=[],
            leads_to=[],
            estimated_duration_minutes=est_duration,
            estimated_tokens=est_tokens,
            status=EpisodeStatus.PLANNING,
        )
        episodes.append(ep)
        db.add(ep)

    db.commit()

    # Post-process depends_on and leads_to after all created (linear chain for now)
    if len(episodes) > 1:
        for i, ep in enumerate(episodes):
            if i > 0:
                ep.depends_on = [str(episodes[i-1].id)]
            if i < len(episodes) - 1:
                ep.leads_to = [str(episodes[i+1].id)]
        db.commit()

    return EpisodesListResponse(episodes=episodes, total=len(episodes))
