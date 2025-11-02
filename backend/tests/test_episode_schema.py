import uuid

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.episode import Episode, EpisodeStatus
from backend.models.job import Job
from backend.models.user import User
from sqlalchemy import text

client = TestClient(app)


def test_episode_response_minimal(db_session):
    user = User(email=f"test+{uuid.uuid4()}@example.com", hashed_password="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    job = Job(
        user_id=user.id,
        repo_url="https://example.com/repo",
        repo_name="repo",
        repo_owner="owner",
        depth_tier="survey",
        git_ref="main",
        status="pending",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    episode = Episode(
        job_id=job.id,
        episode_number=1,
        title="Authentication Flow",
        narrative_theme="How requests authenticate and propagate identity",
        status=EpisodeStatus.PENDING,
    )
    db_session.add(episode)
    db_session.commit()
    db_session.refresh(episode)

    # direct attribute assertions
    assert episode.episode_number == 1
    assert episode.title.startswith("Authentication")


def test_episode_planning_fields_defaults(db_session):
    user = User(email=f"test+{uuid.uuid4()}@example.com", hashed_password="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    job = Job(
        user_id=user.id,
        repo_url="https://example.com/repo",
        repo_name="repo",
        repo_owner="owner",
        depth_tier="standard",
        git_ref="main",
        status="pending",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    episode = Episode(
        job_id=job.id,
        episode_number=2,
        title="Data Layer",
        narrative_theme="Persistence mechanics and abstractions",
        status=EpisodeStatus.PLANNING,
        goals=["Explain ORM abstractions"],
        depends_on=["Episode 1"],
        estimated_duration_minutes=20,
    )
    db_session.add(episode)
    db_session.commit()
    db_session.refresh(episode)
    assert episode.goals == ["Explain ORM abstractions"]
    assert episode.depends_on == ["Episode 1"]
    assert episode.estimated_duration_minutes == 20


def test_plan_episodes_endpoint_requires_scope(db_session):
    user = User(email=f"test+{uuid.uuid4()}@example.com", hashed_password="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    job = Job(
        user_id=user.id,
        repo_url="https://example.com/repo",
        repo_name="repo",
        repo_owner="owner",
        depth_tier="survey",
        git_ref="main",
        status="pending",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    resp = client.post(f"/episodes/job/{job.id}/plan")
    assert resp.status_code == 400  # Missing selected_files scope



def test_list_job_episodes_endpoint(db_session):
    user = User(email=f"test+{uuid.uuid4()}@example.com", hashed_password="x")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    job = Job(
        user_id=user.id,
        repo_url="https://example.com/repo",
        repo_name="repo",
        repo_owner="owner",
        depth_tier="survey",
        git_ref="main",
        status="pending",
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    r = client.get(f"/episodes/job/{job.id}")
    assert r.status_code == 200
    body = r.json()
    assert "episodes" in body
    assert body["total"] == 0
