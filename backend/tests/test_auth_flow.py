"""Basic auth flow tests: register -> login -> me.

Sets required environment variables for Settings before importing the app.
Uses sqlite in test environment (allowed because environment begins with 'test').
"""

import os
import uuid
from fastapi.testclient import TestClient


# Minimal required env vars for backend.config.Settings
REQUIRED_ENV = {
    "DATABASE_URL": "sqlite:///./test_auth.db",
    "CHECKPOINT_DATABASE_URL": "sqlite:///./test_checkpoint.db",
    "ANTHROPIC_API_KEY": "test-anthropic",
    "STRIPE_SECRET_KEY": "sk_test_dummy",
    "STRIPE_WEBHOOK_SECRET": "whsec_test_dummy",
    "STRIPE_PUBLISHABLE_KEY": "pk_test_dummy",
    "AWS_ACCESS_KEY_ID": "dummy",
    "AWS_SECRET_ACCESS_KEY": "dummy",
    "S3_BUCKET_NAME": "dummy-bucket",
    "S3_REGION": "us-east-1",
    "JWT_SECRET": "super-secret-test-key",
    "API_BASE_URL": "http://localhost:8000/api/v1",
    "REDIS_URL": "redis://localhost:6379/0",
    "ENVIRONMENT": "test",
}

for k, v in REQUIRED_ENV.items():
    os.environ.setdefault(k, v)


from backend.main import app  # noqa: E402 (import after env setup)

client = TestClient(app)


def test_register_login_me_flow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "StrongPassw0rd!"

    # Register
    r = client.post("/api/v1/auth/register", json={"email": email, "password": password, "name": "Tester"})
    assert r.status_code == 201, r.text
    user_id = r.json()["id"]
    assert user_id

    # Login (form encoded)
    r_login = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r_login.status_code == 200, r_login.text
    token_data = r_login.json()
    assert "access_token" in token_data
    access = token_data["access_token"]

    # /me with Authorization header
    r_me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r_me.status_code == 200, r_me.text
    me = r_me.json()
    assert me["email"] == email

    # Logout should succeed
    r_logout = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r_logout.status_code == 200, r_logout.text
