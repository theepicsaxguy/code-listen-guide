import pytest
from fastapi import status

from backend.api.routes import episodes as episodes_routes
from backend.models.episode import Episode, EpisodeStatus
from backend.services.dependency_analyzer import ClusterPlan


@pytest.fixture(autouse=True)
def stub_episode_planner(monkeypatch):
    """Provide deterministic planner outputs for endpoint tests."""

    class StubAnalyzer:
        def __init__(self, *args, **kwargs):
            pass

        def build_import_graph(self, selected_files):
            return {
                "backend/main.py": ["backend/utils.py"],
                "backend/utils.py": [],
            }

        def cluster_graph(self, graph):
            return [ClusterPlan(files=set(graph.keys()), index=1)]

        def identify_architectural_layers(self, clusters):
            return {}

    async def fake_plan_episodes_from_clusters(clusters, dependency_graph, architectural_layers, repo_context):
        return [
            {
                "title": "Architecture Overview",
                "narrative_theme": "Stub narrative",
                "conversation_hooks": [],
                "learning_objectives": [],
            }
        ]

    monkeypatch.setattr(episodes_routes, "DependencyAnalyzer", StubAnalyzer)
    monkeypatch.setattr(episodes_routes, "plan_episodes_from_clusters", fake_plan_episodes_from_clusters)


def _create_episode(db_session, job, episode_number=1):
    episode = Episode(
        job_id=job.id,
        episode_number=episode_number,
        title=f"Episode {episode_number}",
        narrative_theme="Stub narrative",
        status=EpisodeStatus.PENDING,
    )
    db_session.add(episode)
    db_session.commit()
    db_session.refresh(episode)
    return episode


def test_plan_episodes_requires_auth(test_client, create_job, create_user):
    owner = create_user()
    job = create_job(
        user=owner,
        selected_files=["backend/main.py", "backend/utils.py"],
        metadata_json={"local_repo_path": "."},
    )

    response = test_client.post(f"/episodes/job/{job.id}/plan")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_plan_episodes_rejects_other_user(test_client, create_job, create_user, auth_header):
    owner = create_user()
    job = create_job(
        user=owner,
        selected_files=["backend/main.py", "backend/utils.py"],
        metadata_json={"local_repo_path": "."},
    )
    other = create_user()
    headers, _ = auth_header(user=other)

    response = test_client.post(f"/episodes/job/{job.id}/plan", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_plan_episodes_allows_owner(test_client, create_job, create_user, auth_header):
    owner = create_user()
    job = create_job(
        user=owner,
        selected_files=["backend/main.py", "backend/utils.py"],
        metadata_json={"local_repo_path": "."},
    )
    headers, _ = auth_header(user=owner)

    response = test_client.post(f"/episodes/job/{job.id}/plan", headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["total"] == 1
    assert body["episodes"][0]["title"] == "Architecture Overview"


def test_plan_episodes_allows_admin(test_client, create_job, create_user, auth_header):
    owner = create_user()
    job = create_job(
        user=owner,
        selected_files=["backend/main.py", "backend/utils.py"],
        metadata_json={"local_repo_path": "."},
    )
    admin = create_user(is_admin=True)
    headers, _ = auth_header(user=admin)

    response = test_client.post(f"/episodes/job/{job.id}/plan", headers=headers)

    assert response.status_code == status.HTTP_201_CREATED


def test_list_job_episodes_requires_auth(test_client, create_job, create_user):
    owner = create_user()
    job = create_job(user=owner)

    response = test_client.get(f"/episodes/job/{job.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_job_episodes_rejects_other_user(test_client, create_job, create_user, auth_header, db_session):
    owner = create_user()
    job = create_job(user=owner)
    _create_episode(db_session, job)
    other = create_user()
    headers, _ = auth_header(user=other)

    response = test_client.get(f"/episodes/job/{job.id}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_job_episodes_allows_owner(test_client, create_job, create_user, auth_header, db_session):
    owner = create_user()
    job = create_job(user=owner)
    _create_episode(db_session, job, episode_number=1)
    _create_episode(db_session, job, episode_number=2)
    headers, _ = auth_header(user=owner)

    response = test_client.get(f"/episodes/job/{job.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["total"] == 2
    assert len(body["episodes"]) == 2


def test_list_job_episodes_allows_admin(test_client, create_job, create_user, auth_header, db_session):
    owner = create_user()
    job = create_job(user=owner)
    _create_episode(db_session, job)
    admin = create_user(is_admin=True)
    headers, _ = auth_header(user=admin)

    response = test_client.get(f"/episodes/job/{job.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK


def test_get_episode_requires_auth(test_client, create_job, create_user, db_session):
    owner = create_user()
    job = create_job(user=owner)
    episode = _create_episode(db_session, job)

    response = test_client.get(f"/episodes/{episode.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_episode_rejects_other_user(test_client, create_job, create_user, auth_header, db_session):
    owner = create_user()
    job = create_job(user=owner)
    episode = _create_episode(db_session, job)
    other = create_user()
    headers, _ = auth_header(user=other)

    response = test_client.get(f"/episodes/{episode.id}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_episode_allows_owner(test_client, create_job, create_user, auth_header, db_session):
    owner = create_user()
    job = create_job(user=owner)
    episode = _create_episode(db_session, job)
    headers, _ = auth_header(user=owner)

    response = test_client.get(f"/episodes/{episode.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(episode.id)


def test_get_episode_allows_admin(test_client, create_job, create_user, auth_header, db_session):
    owner = create_user()
    job = create_job(user=owner)
    episode = _create_episode(db_session, job)
    admin = create_user(is_admin=True)
    headers, _ = auth_header(user=admin)

    response = test_client.get(f"/episodes/{episode.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
