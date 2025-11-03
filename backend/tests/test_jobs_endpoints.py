from fastapi.testclient import TestClient
import pytest

from backend.main import app
from backend.models.user import User
from backend.db.session import SessionLocal
from backend.api.dependencies import get_current_user, get_db


@pytest.fixture()
def db_session():
    # Use the existing SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def user(db_session):
    u = User(
        email="jobtester@example.com",
        name="Job Tester",
        hashed_password="dummy-hash",
        subscription_tier="free",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture()
def client(user):
    # Override current user dependency
    def override_get_current_user():
        return user

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


def test_create_job_success(client):
    payload = {
        "repo_url": "https://github.com/example/repo",
        "depth_tier": "survey",
        "git_ref": "main"
    }
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["repo_name"] == "repo"
    assert data["repo_owner"] == "example"
    assert data["status"] == "pending"
    assert data["chapters"] == []
    assert data["deliverables"] == []


def test_list_jobs_returns_created_job(client):
    # Create a job first
    create_payload = {
        "repo_url": "https://github.com/example/repo2",
        "depth_tier": "survey",
        "git_ref": "main"
    }
    create_resp = client.post("/api/v1/jobs", json=create_payload)
    assert create_resp.status_code == 201

    list_resp = client.get("/api/v1/jobs")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert "jobs" in data
    assert data["total"] >= 1
    assert len(data["jobs"]) >= 1
    first = data["jobs"][0]
    assert "repo_url" in first
    assert "depth_tier" in first


def test_get_job_success(client):
    payload = {
        "repo_url": "https://github.com/example/repo3",
        "depth_tier": "standard",
        "git_ref": "main"
    }
    create_resp = client.post("/api/v1/jobs", json=payload)
    assert create_resp.status_code == 201
    job_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert get_resp.status_code == 200
    job = get_resp.json()
    assert job["id"] == job_id
    assert job["repo_owner"] == "example"
    assert job["status"] == "pending"

