import json
import math
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.db.session import SessionLocal
from backend.models.chapter import Chapter
from backend.models.deliverable import Deliverable
from backend.models.job import Job
from backend.models.outline import Outline


def _session() -> Session:
    return SessionLocal()


def _normalize_repo(repo_url: str) -> Dict[str, str]:
    trimmed = repo_url.rstrip("/").replace(".git", "")
    parts = trimmed.split("/")
    repo_name = parts[-1] if parts else "repo"
    repo_owner = parts[-2] if len(parts) > 1 else "unknown"
    return {"name": repo_name, "owner": repo_owner}


def create_job_record(db: Session, user_id: UUID, repo_url: str, depth_tier: str, git_ref: Optional[str]) -> Job:
    meta = _normalize_repo(repo_url)
    job = Job(
        user_id=user_id,
        repo_url=repo_url,
        repo_name=meta["name"],
        repo_owner=meta["owner"],
        git_ref=git_ref or "main",
        depth_tier=depth_tier,
        status="pending",
        progress_percentage=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_record(db: Session, job_id: UUID, user_id: UUID) -> Optional[Job]:
    return (
        db.query(Job)
        .filter(Job.id == job_id, Job.user_id == user_id)
        .first()
    )


def get_job_by_id(job_id: str) -> Optional[Job]:
    with _session() as db:
        return db.query(Job).filter(Job.id == job_id).first()


def mark_job_status(job_id: str, status: str, stage: Optional[str]) -> None:
    with _session() as db:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return
        job.status = status
        job.current_stage = stage
        if status in {"running", "waiting_approval"} and not job.started_at:
            job.started_at = datetime.utcnow()
        if status == "completed":
            job.completed_at = datetime.utcnow()
        db.commit()


def persist_outline(job_id: str, outline_payload: str) -> None:
    with _session() as db:
        outline = db.query(Outline).filter(Outline.job_id == job_id).first()
        if outline is None:
            outline = Outline(job_id=job_id, outline_data={})
            db.add(outline)
        try:
            parsed = json.loads(outline_payload)
        except json.JSONDecodeError:
            parsed = {"raw": outline_payload}
        outline.outline_data = parsed
        db.commit()


def load_approved_outline(job_id: str) -> Optional[Outline]:
    with _session() as db:
        return (
            db.query(Outline)
            .filter(Outline.job_id == job_id, Outline.user_approved.is_(True))
            .first()
        )


def save_chapter_script(job_id: str, chapter_number: int, script: str) -> bool:
    with _session() as db:
        chapter = (
            db.query(Chapter)
            .filter(Chapter.job_id == job_id, Chapter.chapter_number == chapter_number)
            .first()
        )
        if chapter is None:
            chapter = Chapter(job_id=job_id, chapter_number=chapter_number, title=f"Chapter {chapter_number}")
            db.add(chapter)
        chapter.script_text = script
        chapter.status = "scripting"
        db.commit()
    return True


def persist_audio_parts(job_id: str, audio_urls: List[str]) -> None:
    with _session() as db:
        for index, url in enumerate(audio_urls, start=1):
            chapter = (
                db.query(Chapter)
                .filter(Chapter.job_id == job_id, Chapter.chapter_number == index)
                .first()
            )
            if chapter:
                chapter.audio_url = url
                chapter.status = "synthesizing"
        for url in audio_urls:
            deliverable = Deliverable(job_id=job_id, file_type="chapter_audio", file_url=url)
            db.add(deliverable)
        db.commit()


def estimate_job_cost(repo_url: str, depth_tier: str) -> Dict[str, Any]:
    tiers = {"survey": 2, "standard": 4, "comprehensive": 6}
    chapters = tiers.get(depth_tier, 3)
    duration_hours = chapters * 0.5
    cost_cents = int(math.ceil(chapters * 500))
    return {
        "estimated_cost_cents": cost_cents,
        "estimated_duration_hours": duration_hours,
        "estimated_chapters": chapters,
        "depth_tier": depth_tier,
    }
