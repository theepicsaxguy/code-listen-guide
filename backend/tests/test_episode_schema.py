import uuid

from fastapi.testclient import TestClient

from fastapi import status

from backend.models.episode import Episode, EpisodeStatus


def test_episode_response_minimal(db_session, create_user, create_job):
    user = create_user()
    job = create_job(user=user)
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


def test_episode_planning_fields_defaults(db_session, create_user, create_job):
    user = create_user()
    job = create_job(user=user)
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


def test_plan_episodes_endpoint_requires_scope(
    test_client, create_job, create_user, auth_header
):
    owner = create_user()
    job = create_job(user=owner)
    headers, _ = auth_header(user=owner)

    response = test_client.post(f"/episodes/job/{job.id}/plan", headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_job_episodes_endpoint(test_client, create_job, create_user, auth_header):
    owner = create_user()
    job = create_job(user=owner)
    headers, _ = auth_header(user=owner)

    response = test_client.get(f"/episodes/job/{job.id}", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert "episodes" in body
    assert body["total"] == 0
