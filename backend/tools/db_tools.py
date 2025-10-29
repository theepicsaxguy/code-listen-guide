import argparse
import math
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.agents.schemas import OutlineAgentResponse
from backend.db.session import SessionLocal
from backend.models.chapter import Chapter
from backend.models.deliverable import Deliverable
from backend.models.job import Job
from backend.models.outline import Outline
from backend.models.user import User


def _session() -> Session:
    return SessionLocal()


def _normalize_repo(repo_url: str) -> Dict[str, str]:
    trimmed = repo_url.rstrip("/").replace(".git", "")
    parts = trimmed.split("/")
    repo_name = parts[-1] if parts else "repo"
    repo_owner = parts[-2] if len(parts) > 1 else "unknown"
    return {"name": repo_name, "owner": repo_owner}


def create_job_record(
    db: Session,
    user_id: UUID,
    repo_url: str,
    depth_tier: str,
    git_ref: Optional[str],
) -> Job:
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
    return db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()


def get_job_by_id(job_id: str) -> Optional[Job]:
    with _session() as db:
        normalized_id = UUID(job_id) if isinstance(job_id, str) else job_id
        return db.query(Job).filter(Job.id == normalized_id).first()


def mark_job_status(job_id: str, status: str, stage: Optional[str]) -> None:
    with _session() as db:
        normalized_id = UUID(job_id) if isinstance(job_id, str) else job_id
        job = db.query(Job).filter(Job.id == normalized_id).first()
        if not job:
            return
        job.status = status
        job.current_stage = stage
        if status in {"running", "waiting_approval"} and not job.started_at:
            job.started_at = datetime.utcnow()
        if status == "completed":
            job.completed_at = datetime.utcnow()
        db.commit()


def persist_outline(
    job_id: Union[str, UUID],
    outline_payload: Union[str, Dict[str, Any], OutlineAgentResponse],
    db: Optional[Session] = None,
) -> Outline:
    owns_session = db is None
    session = db or _session()
    try:
        normalized_job_id = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
        outline = (
            session.query(Outline).filter(Outline.job_id == normalized_job_id).first()
        )
        if outline is None:
            outline = Outline(job_id=normalized_job_id, outline_data={})
            session.add(outline)
        if isinstance(outline_payload, OutlineAgentResponse):
            payload_model = outline_payload
        elif isinstance(outline_payload, str):
            try:
                payload_model = OutlineAgentResponse.model_validate_json(outline_payload)
            except ValidationError:
                payload_model = OutlineAgentResponse(
                    chapters=[], raw_outline=outline_payload.strip() or None
                )
        else:
            try:
                payload_model = OutlineAgentResponse.model_validate(outline_payload)
            except ValidationError:
                payload_model = OutlineAgentResponse(
                    chapters=[], raw_outline=str(outline_payload)
                )
        outline.outline_data = payload_model.model_dump()
        outline.user_approved = False
        outline.user_modifications = None
        outline.approved_at = None
        session.flush()
        if owns_session:
            session.commit()
            session.refresh(outline)
        else:
            session.refresh(outline)
        return outline
    finally:
        if owns_session:
            session.close()


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
            chapter = Chapter(
                job_id=job_id,
                chapter_number=chapter_number,
                title=f"Chapter {chapter_number}",
            )
            db.add(chapter)
        chapter.script_text = script
        chapter.status = "scripting"
        db.commit()
    return True


def persist_audio_parts(job_id: str, audio_urls: List[str]) -> None:
    with _session() as db:
        db.query(Deliverable).filter(
            Deliverable.job_id == job_id,
            Deliverable.file_type == "chapter_audio",
        ).delete(synchronize_session=False)
        for index, url in enumerate(audio_urls, start=1):
            chapter = (
                db.query(Chapter)
                .filter(Chapter.job_id == job_id, Chapter.chapter_number == index)
                .first()
            )
            if chapter:
                chapter.audio_url = url
                chapter.status = "completed"
                chapter.completed_at = datetime.utcnow()
        for url in audio_urls:
            deliverable = Deliverable(
                job_id=job_id, file_type="chapter_audio", file_url=url
            )
            db.add(deliverable)
        db.commit()


def estimate_job_cost(repo_url: str, depth_tier: str) -> Dict[str, Any]:
    tiers = {"survey": 2, "standard": 4, "comprehensive": 6}
    chapters = tiers.get(depth_tier, 3)
    duration_minutes = int(chapters * 30)
    cost_cents = int(math.ceil(chapters * 500))
    return {
        "estimated_cost_cents": cost_cents,
        "estimated_duration_minutes": duration_minutes,
        "estimated_chapters": chapters,
        "depth_tier": depth_tier,
    }


def set_user_admin_status(
    user_identifier: Union[str, UUID], is_admin: bool, db: Optional[Session] = None
) -> bool:
    session_owner = db is None
    session = db or _session()
    try:
        target: Optional[User] = None
        if isinstance(user_identifier, UUID):
            target = session.query(User).filter(User.id == user_identifier).first()
        else:
            try:
                normalized = UUID(str(user_identifier))
                target = (
                    session.query(User)
                    .filter(User.id == normalized)
                    .first()
                )
            except (TypeError, ValueError):
                target = None
        if target is None and isinstance(user_identifier, str):
            target = (
                session.query(User)
                .filter(User.email == user_identifier.strip())
                .first()
            )
        if target is None:
            return False
        target.is_admin = is_admin
        session.commit()
        if session_owner:
            session.refresh(target)
        return True
    finally:
        if session_owner:
            session.close()


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Database maintenance utilities."
    )
    subcommands = parser.add_subparsers(dest="command")
    set_admin = subcommands.add_parser(
        "set-admin", help="Set administrator access by email or user ID."
    )
    set_admin.add_argument("identifier", help="User email address or UUID.")
    set_admin.add_argument(
        "--remove",
        action="store_true",
        help="Revoke administrator access for the user.",
    )
    return parser


def _run_cli() -> None:
    parser = _build_cli_parser()
    args = parser.parse_args()
    if args.command == "set-admin":
        desired = not args.remove
        success = set_user_admin_status(args.identifier, desired)
        if not success:
            print("User not found.", file=sys.stderr)
            sys.exit(1)
        action = "granted" if desired else "revoked"
        print(f"Administrator access {action} for {args.identifier}.")
        return
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    _run_cli()
