"""Tests for WebAuthn option generation ensuring no raw bytes leak into JSON responses.

These tests focus on guaranteeing our usage of options_to_json() correctly
serializes credential IDs and challenge values to base64url strings so FastAPI
can JSON encode them without failure.
"""

import json
from backend.services.webauthn_service import webauthn_service
from backend.models.user import User
from backend.models.passkey import Passkey


def _dummy_user() -> User:
    return User(email="user@example.com", hashed_password="x", name="User")


def _dummy_passkey(user_id) -> Passkey:
    return Passkey(user_id=user_id, credential_id="ZmFrZUNyZWRJRA", public_key="{}", name="Test")


def test_generate_authentication_options_serialization():
    """Authentication options should contain only JSON-serializable primitives."""
    user = _dummy_user()
    passkey = _dummy_passkey(user.id)
    opts = webauthn_service.generate_authentication_options(user=user, passkeys=[passkey])

    # Ensure challenge present and is a string
    assert isinstance(opts["challenge"], str)

    # Ensure allowCredentials ids are strings (base64url), not bytes
    allow = opts.get("allowCredentials") or []
    for cred in allow:
        assert isinstance(cred["id"], str), "Credential id should be base64url string"

    # JSON round-trip should succeed
    encoded = json.dumps(opts)
    decoded = json.loads(encoded)
    assert decoded["challenge"] == opts["challenge"]


def test_generate_conditional_authentication_options_serialization():
    """Conditional options should also serialize cleanly and omit allowCredentials."""
    opts = webauthn_service.generate_conditional_authentication_options()
    assert isinstance(opts["challenge"], str)
    assert "allowCredentials" not in opts or opts.get("allowCredentials") in (None, [])
    # JSON round-trip
    encoded = json.dumps(opts)
    assert isinstance(encoded, str)