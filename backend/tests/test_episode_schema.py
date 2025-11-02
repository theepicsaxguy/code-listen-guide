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


def test_list_job_episodes_endpoint():
    # Without auth currently (placeholder dependency) should 200 even if job has none
    job_id = uuid.uuid4()
    r = client.get(f"/episodes/job/{job_id}")
    assert r.status_code == 200
    body = r.json()
    assert 'episodes' in body
    assert body['total'] == 0
