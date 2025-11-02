import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.db.session import SessionLocal
from backend.models.episode import Episode, EpisodeStatus


client = TestClient(app)


def get_db() -> Session:
    return SessionLocal()


def test_episode_response_minimal():
    db = get_db()
    job_id = uuid.uuid4()
    episode = Episode(
        job_id=job_id,
        episode_number=1,
        title="Authentication Flow",
        narrative_theme="How requests authenticate and propagate identity",
        status=EpisodeStatus.PENDING,
    )
    db.add(episode)
    db.commit()
    db.refresh(episode)

    # direct attribute assertions
    assert episode.episode_number == 1
    assert episode.title.startswith("Authentication")


def test_episode_planning_fields_defaults():
    db = get_db()
    job_id = uuid.uuid4()
    episode = Episode(
        job_id=job_id,
        episode_number=2,
        title="Data Layer",
        narrative_theme="Persistence mechanics and abstractions",
        status=EpisodeStatus.PLANNING,
        goals=["Explain ORM abstractions"],
        depends_on=["Episode 1"],
        estimated_duration_minutes=20,
    )
    db.add(episode)
    db.commit()
    db.refresh(episode)
    assert episode.goals == ["Explain ORM abstractions"]
    assert episode.depends_on == ["Episode 1"]
    assert episode.estimated_duration_minutes == 20


def test_plan_episodes_endpoint_requires_scope(monkeypatch):
    # Create a fake job row inserted directly using raw SQL since Job model import may cause circulars
    db = get_db()
    job_uuid = uuid.uuid4()
    db.execute(
        "INSERT INTO jobs (id, user_id, repo_url, repo_name, repo_owner, git_ref, depth_tier, status, created_at, updated_at) "
        "VALUES (:id, :user_id, 'https://example.com/repo', 'repo', 'owner', 'main', 'survey', 'pending', NOW(), NOW())",
        {"id": job_uuid, "user_id": uuid.uuid4()},
    )
    db.commit()
    resp = client.post(f"/episodes/job/{job_uuid}/plan")
    # Missing selected_files scope -> 400
    assert resp.status_code == 400



def test_list_job_episodes_endpoint():
    # Without auth currently (placeholder dependency) should 200 even if job has none
    job_id = uuid.uuid4()
    r = client.get(f"/episodes/job/{job_id}")
    assert r.status_code == 200
    body = r.json()
    assert 'episodes' in body
    assert body['total'] == 0
