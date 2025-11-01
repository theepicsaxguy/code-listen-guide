"""Comprehensive API route tests with deterministic expectations."""

import json
import uuid
from datetime import datetime

import pytest
from fastapi import status

from backend.models.agent_registry import AgentRegistry
from backend.models.chapter import Chapter
from backend.models.deliverable import Deliverable
from backend.models.job import Job
from backend.models.outline import Outline
from backend.models.payment import Payment
from backend.models.tool_registry import ToolRegistry
from backend.models.workflow_definition import WorkflowDefinition
from backend.models.workflow_instance import WorkflowInstance
from backend.models.workflow_revision import WorkflowRevision
from backend.models.workflow_step import WorkflowStep
from backend.utils.auth import create_access_token


def _make_admin_headers(create_user):
    admin = create_user(is_admin=True)
    token = create_access_token({"sub": str(admin.id), "is_admin": True})
    return {"Authorization": f"Bearer {token}"}, admin


@pytest.mark.api
@pytest.mark.unit
class TestAuthRoutes:
    """Authentication endpoint coverage."""

    def test_register_user_returns_created_user(self, test_client):
        payload = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User",
        }
        response = test_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["subscription_tier"] == "free"
        assert data["credits_remaining"] == 100

    def test_register_duplicate_email_returns_400(self, test_client, create_user):
        email = "existing@example.com"
        create_user(email=email)
        response = test_client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "SecurePass123!", "name": "Dup"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Email already registered"}

    def test_login_returns_tokens_for_valid_credentials(self, test_client, create_user):
        email = "login@example.com"
        password = "SecurePass123!"
        create_user(email=email, password=password)
        response = test_client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str) and body["access_token"]
        assert isinstance(body["refresh_token"], str) and body["refresh_token"]

    def test_login_rejects_invalid_credentials(self, test_client, create_user):
        email = "login-fail@example.com"
        create_user(email=email, password="SecurePass123!")
        response = test_client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": "WrongPass999"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect email or password"

    def test_get_current_user_returns_profile(self, test_client, auth_header):
        headers, user = auth_header()
        response = test_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        profile = response.json()
        assert profile["id"] == str(user.id)
        assert profile["email"] == user.email

    def test_get_current_user_without_token_returns_401(self, test_client):
        response = test_client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"


@pytest.mark.api
@pytest.mark.unit
class TestJobRoutes:
    """Job management endpoint coverage."""

    def test_create_job_returns_job_response(self, test_client, auth_header):
        headers, user = auth_header()
        payload = {
            "repo_url": "https://github.com/user/test-repo",
            "depth_tier": "standard",
            "git_ref": "main",
        }
        response = test_client.post("/api/v1/jobs", json=payload, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        job = response.json()
        assert job["user_id"] == str(user.id)
        assert job["repo_url"] == payload["repo_url"]
        assert job["status"] == "pending"

    def test_create_job_without_token_returns_401(self, test_client):
        payload = {
            "repo_url": "https://github.com/user/test-repo",
            "depth_tier": "standard",
            "git_ref": "main",
        }
        response = test_client.post("/api/v1/jobs", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_list_jobs_returns_paginated_result(
        self, test_client, auth_header, create_job
    ):
        headers, user = auth_header()
        create_job(user=user, repo_url="https://github.com/user/alpha")
        create_job(
            user=user, repo_url="https://github.com/user/beta", status="completed"
        )
        response = test_client.get("/api/v1/jobs", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["total"] == 2
        assert len(payload["jobs"]) == 2
        assert {item["user_id"] for item in payload["jobs"]} == {str(user.id)}

    def test_get_job_not_found_returns_404(self, test_client, auth_header):
        headers, _ = auth_header()
        response = test_client.get(f"/api/v1/jobs/{uuid.uuid4()}", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Job not found"

    def test_delete_job_removes_record(
        self, test_client, auth_header, create_job, test_db
    ):
        headers, user = auth_header()
        job = create_job(user=user)
        response = test_client.delete(f"/api/v1/jobs/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert test_db.query(Job).filter(Job.id == job.id).first() is None

    def test_start_job_returns_202(self, test_client, auth_header, create_job):
        headers, user = auth_header()
        job = create_job(user=user, status="pending")
        response = test_client.post(f"/api/v1/jobs/{job.id}/start", headers=headers)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json() == {"accepted": True}

    def test_start_job_invalid_status_returns_400(
        self, test_client, auth_header, create_job
    ):
        headers, user = auth_header()
        job = create_job(user=user, status="completed")
        response = test_client.post(f"/api/v1/jobs/{job.id}/start", headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Job cannot be started in current status"

    def test_start_job_without_auth_returns_401(self, test_client, create_job):
        job = create_job()
        response = test_client.post(f"/api/v1/jobs/{job.id}/start")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_estimate_job_cost_accepts_json_body(self, test_client, auth_header):
        headers, _ = auth_header()
        payload = {
            "repo_url": "https://github.com/example/project",
            "depth_tier": "survey",
        }
        response = test_client.post(
            "/api/v1/jobs/estimate", json=payload, headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        body = response.json()
        assert body["depth_tier"] == payload["depth_tier"]


@pytest.mark.api
@pytest.mark.unit
class TestOutlineRoutes:
    """Outline workflow endpoint coverage."""

    def test_generate_outline_creates_record(
        self,
        test_client,
        test_db,
        create_job,
        sample_outline_data,
        auth_header,
        monkeypatch,
    ):
        headers, user = auth_header()
        job = create_job(user=user)

        async def fake_generate_outline(**_kwargs):
            from backend.agents.schemas import OutlineAgentResponse

            return OutlineAgentResponse.model_validate(sample_outline_data)

        monkeypatch.setattr(
            "backend.api.routes.outlines.run_outline_generator",
            fake_generate_outline,
        )

        response = test_client.post(
            f"/api/v1/jobs/{job.id}/outline",
            json={"analysis_data": {"structure": {"file_count": 50}}},
            headers=headers,
        )
        assert response.status_code == status.HTTP_201_CREATED
        body = response.json()
        assert body["job_id"] == str(job.id)
        outline = test_db.query(Outline).filter(Outline.job_id == job.id).one()
        assert outline.user_approved is False
        assert outline.outline_data["total_chapters"] == 2
        test_db.refresh(job)
        assert job.status == "waiting_approval"

    def test_generate_outline_missing_job_returns_404(self, test_client, auth_header):
        headers, _ = auth_header()
        response = test_client.post(
            f"/api/v1/jobs/{uuid.uuid4()}/outline",
            json={"analysis_data": {}},
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Job not found"

    def test_update_outline_persists_changes(
        self,
        test_client,
        test_db,
        create_job,
        sample_outline_data,
        auth_header,
    ):
        headers, user = auth_header()
        job = create_job(user=user)
        outline = Outline(job_id=job.id, outline_data=sample_outline_data)
        test_db.add(outline)
        test_db.commit()
        test_db.refresh(outline)
        update_payload = {
            "outline_data": {
                "chapters": sample_outline_data["chapters"],
                "total_estimated_duration_minutes": 45,
                "total_chapters": 2,
            },
            "user_modifications": {"notes": "Add more detail"},
        }
        response = test_client.put(
            f"/api/v1/jobs/{job.id}/outline",
            json=update_payload,
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["outline_data"]["total_estimated_duration_minutes"] == 45
        test_db.refresh(outline)
        assert outline.user_modifications == {"notes": "Add more detail"}
        assert outline.user_approved is False

    def test_approve_outline_creates_payment_intent(
        self,
        test_client,
        test_db,
        create_job,
        sample_outline_data,
        auth_header,
        monkeypatch,
    ):
        headers, user = auth_header()
        job = create_job(user=user)
        outline = Outline(job_id=job.id, outline_data=sample_outline_data)
        test_db.add(outline)
        test_db.commit()
        test_db.refresh(outline)

        class DummyIntent:
            def __init__(self):
                self.id = "pi_test_123"
                self.client_secret = "secret"
                self.amount = 4900
                self.currency = "usd"
                self.status = "requires_payment_method"

        async def fake_create_payment_intent(**_kwargs):
            return DummyIntent()

        monkeypatch.setattr(
            "backend.api.routes.outlines.create_payment_intent",
            fake_create_payment_intent,
        )

        response = test_client.post(
            f"/api/v1/jobs/{job.id}/outline/approve",
            json={"outline_id": str(outline.id)},
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["payment_intent_id"] == "pi_test_123"
        test_db.refresh(outline)
        assert outline.user_approved is True
        payment = test_db.query(Payment).filter(Payment.job_id == job.id).one()
        assert payment.amount_cents == 4900

    def test_approve_outline_missing_outline_returns_404(
        self, test_client, create_job, auth_header
    ):
        headers, user = auth_header()
        job = create_job(user=user)
        response = test_client.post(
            f"/api/v1/jobs/{job.id}/outline/approve",
            json={"outline_id": str(uuid.uuid4())},
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Outline not found"


@pytest.mark.api
@pytest.mark.unit
class TestPaymentRoutes:
    """Payment endpoint coverage."""

    def test_create_payment_intent_returns_details(
        self, test_client, create_job, auth_header, monkeypatch
    ):
        headers, user = auth_header()
        job = create_job(user=user, status="pending")

        class DummyIntent:
            def __init__(self):
                self.id = "pi_123"
                self.client_secret = "secret"
                self.amount = 4900
                self.currency = "usd"
                self.status = "requires_payment_method"

        async def fake_create_payment_intent(**_kwargs):
            return DummyIntent()

        class DummyStripeService:
            async def create_customer(self, **_kwargs):
                return "cus_test"

        monkeypatch.setattr(
            "backend.api.routes.payments.get_stripe_service",
            lambda: DummyStripeService(),
        )

        monkeypatch.setattr(
            "backend.api.routes.payments.create_payment_intent",
            fake_create_payment_intent,
        )

        response = test_client.post(
            "/api/v1/payments/create-intent",
            json={"job_id": str(job.id), "amount_cents": 4900},
            headers=headers,
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["payment_intent_id"] == "pi_123"
        assert data["amount_cents"] == 4900

    def test_create_payment_intent_for_completed_job_returns_400(
        self, test_client, create_job, auth_header
    ):
        headers, user = auth_header()
        job = create_job(user=user, status="completed")
        response = test_client.post(
            "/api/v1/payments/create-intent",
            json={"job_id": str(job.id)},
            headers=headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Job already completed"

    def test_create_payment_intent_requires_authentication(
        self, test_client, create_job
    ):
        job = create_job()
        response = test_client.post(
            "/api/v1/payments/create-intent",
            json={"job_id": str(job.id)},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Not authenticated"

    def test_stripe_webhook_updates_payment_and_job(
        self, test_client, test_db, create_job, monkeypatch
    ):
        job = create_job(status="pending")
        payment = Payment(
            user_id=job.user_id,
            job_id=job.id,
            stripe_payment_intent_id="pi_existing",
            amount_cents=4900,
            currency="usd",
            status="requires_payment_method",
        )
        test_db.add(payment)
        test_db.commit()

        class DummyStripeService:
            def verify_webhook_signature(self, payload, sig):
                return {
                    "type": "payment_intent.succeeded",
                    "data": {
                        "object": {
                            "id": "pi_existing",
                            "metadata": {"job_id": str(job.id)},
                            "latest_charge": "ch_123",
                            "payment_method_types": ["card"],
                        }
                    },
                }

        def dummy_get_service():
            return DummyStripeService()

        monkeypatch.setattr(
            "backend.api.routes.payments.get_stripe_service", dummy_get_service
        )

        monkeypatch.setattr(
            "backend.api.routes.payments.stripe.Charge.retrieve",
            lambda charge_id: {"receipt_url": f"https://stripe.example/{charge_id}"},
        )

        payload = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_existing",
                    "metadata": {"job_id": str(job.id)},
                    "latest_charge": "ch_123",
                    "payment_method_types": ["card"],
                }
            },
        }
        response = test_client.post(
            "/api/v1/payments/webhook",
            data=json.dumps(payload),
            headers={"Stripe-Signature": "signature"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"received": True}
        test_db.refresh(payment)
        test_db.refresh(job)
        assert payment.status == "succeeded"
        assert job.status == "paid"

    def test_payment_history_returns_user_payments(
        self, test_client, create_job, auth_header, test_db
    ):
        headers, user = auth_header()
        job = create_job(user=user)
        payment = Payment(
            user_id=user.id,
            job_id=job.id,
            stripe_payment_intent_id="pi_test",
            amount_cents=4900,
            currency="usd",
            status="succeeded",
        )
        test_db.add(payment)
        test_db.commit()
        response = test_client.get("/api/v1/payments/history", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["total"] == 1
        assert payload["payments"][0]["stripe_payment_intent_id"] == "pi_test"


@pytest.mark.api
@pytest.mark.unit
class TestPlayerRoutes:
    """Audiobook player endpoint coverage."""

    def test_get_player_data_returns_job_and_chapters(
        self, test_client, create_job, test_db
    ):
        job = create_job(status="completed")
        chapter = Chapter(
            job_id=job.id,
            chapter_number=1,
            title="Intro",
            description="Overview",
            files_covered=["README.md"],
            topics_covered=["setup"],
            status="completed",
            audio_duration_seconds=120,
        )
        deliverable = Deliverable(
            job_id=job.id,
            file_type="full",
            file_url="https://codebase-audiobooks.s3.amazonaws.com/full.mp3",
        )
        test_db.add_all([chapter, deliverable])
        test_db.commit()
        response = test_client.get(f"/api/v1/player/{job.id}")
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["job"]["id"] == str(job.id)
        assert payload["chapters"]["total_chapters"] == 1
        assert payload["deliverables"][0]["file_type"] == "full"

    def test_get_player_data_missing_job_returns_404(self, test_client):
        response = test_client.get(f"/api/v1/player/{uuid.uuid4()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Job not found"

    def test_download_deliverable_returns_signed_url(
        self, test_client, create_job, test_db, monkeypatch
    ):
        job = create_job(status="completed")
        deliverable = Deliverable(
            job_id=job.id,
            file_type="full",
            file_url="https://test-bucket.s3.amazonaws.com/full.mp3",
        )
        test_db.add(deliverable)
        test_db.commit()

        async def fake_generate_presigned_url(key: str) -> str:
            return f"https://signed.example.com/{key}"

        monkeypatch.setattr(
            "backend.api.routes.player.generate_presigned_url",
            fake_generate_presigned_url,
        )

        response = test_client.get(f"/api/v1/player/{job.id}/download/full")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["download_url"].startswith("https://signed.example.com/")

    def test_download_deliverable_missing_record_returns_404(
        self, test_client, create_job
    ):
        job = create_job()
        response = test_client.get(f"/api/v1/player/{job.id}/download/full")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Deliverable not found"


@pytest.mark.api
@pytest.mark.unit
class TestAdminRegistryRoutes:
    def test_agent_registry_returns_paginated_metadata(
        self,
        test_client,
        test_db,
        create_user,
    ):
        headers, _ = _make_admin_headers(create_user)
        tool = ToolRegistry(
            name="test-tool",
            module_path="backend.tools.example",
            function_name="run",
            description="Example",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        test_db.add(tool)
        test_db.flush()
        agent = AgentRegistry(
            name="test-agent",
            module_path="backend.agents.sample",
            factory_function="build",
            description="Demo agent",
            config_schema={"level": "basic"},
            tools=[str(tool.id)],
        )
        test_db.add(agent)
        test_db.commit()

        response = test_client.get("/api/v1/admin/agents/registry", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["total"] == 1
        assert payload["page"] == 1
        assert payload["page_size"] == 20
        assert payload["agents"][0]["name"] == "test-agent"
        assert payload["agents"][0]["tools"] == [str(tool.id)]

    def test_agent_registry_requires_admin(self, test_client, auth_header):
        headers, _ = auth_header()
        response = test_client.get("/api/v1/admin/agents/registry", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_tool_registry_returns_paginated_metadata(
        self,
        test_client,
        test_db,
        create_user,
    ):
        headers, _ = _make_admin_headers(create_user)
        tool = ToolRegistry(
            name="alpha-tool",
            module_path="backend.tools.alpha",
            function_name="execute",
            description="Alpha",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
        )
        test_db.add(tool)
        test_db.commit()

        response = test_client.get("/api/v1/admin/tools/registry", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["total"] == 1
        assert payload["tools"][0]["name"] == "alpha-tool"
        assert payload["tools"][0]["description"] == "Alpha"

    def test_tool_registry_requires_admin(self, test_client, auth_header):
        headers, _ = auth_header()
        response = test_client.get("/api/v1/admin/tools/registry", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.api
@pytest.mark.unit
class TestTraceRoutes:
    def _create_workflow(self, test_db, job):
        definition = WorkflowDefinition(
            name=f"trace-workflow-{job.id}", description="Test workflow"
        )
        test_db.add(definition)
        test_db.commit()
        revision = WorkflowRevision(
            workflow_definition_id=definition.id,
            version=1,
            is_published=True,
            revision_metadata={},
        )
        test_db.add(revision)
        test_db.commit()
        definition.current_revision_id = revision.id
        test_db.commit()
        steps = [
            WorkflowStep(
                revision_id=revision.id,
                step_order=1,
                step_name="analysis",
                execution_mode="sequential",
                input_mapping={},
                output_mapping={},
                checkpoint_enabled=True,
                retry_policy=None,
                step_config={},
            ),
            WorkflowStep(
                revision_id=revision.id,
                step_order=2,
                step_name="outline",
                execution_mode="sequential",
                input_mapping={},
                output_mapping={},
                checkpoint_enabled=True,
                retry_policy=None,
                step_config={},
            ),
            WorkflowStep(
                revision_id=revision.id,
                step_order=3,
                step_name="audio",
                execution_mode="sequential",
                input_mapping={},
                output_mapping={},
                checkpoint_enabled=True,
                retry_policy=None,
                step_config={},
            ),
        ]
        test_db.add_all(steps)
        test_db.commit()
        instance = WorkflowInstance(
            id=job.id,
            job_id=job.id,
            revision_id=revision.id,
            current_step_id=steps[1].id,
            instance_state={
                "revision_id": str(revision.id),
                "job": {"id": str(job.id)},
                "steps": {
                    "analysis": {
                        "tool_calls": [
                            {
                                "tool": "analyzer",
                                "called_at": "2024-01-01T00:00:00Z",
                                "duration_ms": 1250,
                                "status": "ok",
                            }
                        ],
                        "updated_at": "2024-01-01T00:00:01Z",
                    }
                },
            },
            started_at=datetime.utcnow(),
            status="running",
        )
        test_db.add(instance)
        test_db.commit()

    def test_get_job_trace_returns_stages_for_owner(
        self,
        test_client,
        test_db,
        create_user,
        create_job,
        auth_header,
    ):
        owner = create_user()
        job = create_job(user=owner, status="running")
        job.current_stage = "outline"
        job.started_at = datetime.utcnow()
        test_db.commit()
        self._create_workflow(test_db, job)
        headers, _ = auth_header(user=owner)

        response = test_client.get(f"/api/v1/traces/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["id"] == str(job.id)
        assert len(payload["stages"]) == 3
        analysis_stage = next(stage for stage in payload["stages"] if stage["name"] == "analysis")
        outline_stage = next(stage for stage in payload["stages"] if stage["name"] == "outline")
        audio_stage = next(stage for stage in payload["stages"] if stage["name"] == "audio")
        assert analysis_stage["status"] == "completed"
        assert outline_stage["status"] in {"running", "completed"}
        assert audio_stage["status"] == "pending"
        assert payload["tool_traces"]["analysis"][0]["status"] == "ok"

    def test_get_job_trace_rejects_non_owner(
        self,
        test_client,
        create_user,
        create_job,
        auth_header,
    ):
        owner = create_user()
        other = create_user(email="other@example.com")
        job = create_job(user=owner)
        headers, _ = auth_header(user=other)
        response = test_client.get(f"/api/v1/traces/{job.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_replay_stage_records_request(
        self,
        test_client,
        test_db,
        create_user,
        create_job,
    ):
        owner = create_user()
        job = create_job(user=owner, status="running")
        job.current_stage = "analysis"
        test_db.commit()
        self._create_workflow(test_db, job)
        headers, _ = _make_admin_headers(create_user)
        response = test_client.post(
            f"/api/v1/traces/{job.id}/stages/analysis/replay",
            headers=headers,
        )
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        assert data["success"] is True
        test_db.refresh(job)
        history = job.metadata_json.get("replay_requests", []) if job.metadata_json else []
        assert len(history) == 1
        assert history[0]["stage"] == "analysis"

    def test_replay_stage_requires_admin(
        self,
        test_client,
        test_db,
        create_user,
        create_job,
        auth_header,
    ):
        owner = create_user()
        job = create_job(user=owner, status="running")
        self._create_workflow(test_db, job)
        headers, _ = auth_header(user=owner)
        response = test_client.post(
            f"/api/v1/traces/{job.id}/stages/analysis/replay",
            headers=headers,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
