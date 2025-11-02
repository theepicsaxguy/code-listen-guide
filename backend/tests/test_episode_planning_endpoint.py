import uuid
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.session import SessionLocal

client = TestClient(app)

def db():
    return SessionLocal()

def seed_job_with_scope(dbs, selected_files):
    job_id = uuid.uuid4()
    user_id = uuid.uuid4()
    dbs.execute(
        "INSERT INTO jobs (id, user_id, repo_url, repo_name, repo_owner, git_ref, depth_tier, status, selected_files, created_at, updated_at) "
        "VALUES (:id, :user_id, 'https://example.com/repo', 'repo', 'owner', 'main', 'survey', 'pending', :selected_files::jsonb, NOW(), NOW())",
        {"id": job_id, "user_id": user_id, "selected_files": selected_files},
    )
    dbs.commit()
    return job_id

def test_plan_episodes_success(tmp_path, monkeypatch):
    # Create fake repo path in job metadata not yet supported -> rely on default '.'
    dbs = db()
    job_id = seed_job_with_scope(dbs, '["app/main.py","app/utils.py"]')
    resp = client.post(f"/episodes/job/{job_id}/plan")
    assert resp.status_code in (201, 200)
    data = resp.json()
    assert data['total'] >= 1
    first = data['episodes'][0]
    assert 'file_clusters' in first
    assert 'estimated_duration_minutes' in first

