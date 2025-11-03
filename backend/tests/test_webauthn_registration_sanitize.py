import json
import uuid
from typing import Any

import pytest

from backend.models.user import User
from backend.services.webauthn_service import webauthn_service


class FakeVerification:
    def __init__(self):
        # Simulate library returning raw bytes for credential_id & nested bytes in COSE key
        self.credential_id = b"abc123"  # raw bytes that must be base64url encoded
        self.credential_public_key = {
            "kty": b"OKP",  # becomes base64url
            "x": b"\x01\x02\x03",  # arbitrary bytes
            "nested": [b"a", {"inner": b"b"}],  # deep nesting to exercise sanitizer
        }


@pytest.fixture()
def user(db_session):  # type: ignore[arg-type]
    # Minimal user instance persisted so we have an id (matches pattern used in other tests)
    u = User(
        email="tester@example.com",
        name="Tester",
        hashed_password="dummy-hash",  # satisfy NOT NULL constraint; hashing logic not needed for this test
        subscription_tier="free",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


def _walk(obj: Any):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)
    else:
        yield obj


def test_verify_registration_public_key_sanitized(monkeypatch, user):
    """verify_registration must recursively base64url encode all bytes in credential_public_key."""

    # Monkeypatch parse + verify functions used internally so we don't need a real WebAuthn ceremony
    from backend.services import webauthn_service as svc_module  # module import for patching

    def fake_parse_registration_credential_json(registration_response):  # noqa: D401
        # Return the raw dict; verify_registration_response won't inspect it in our fake
        return registration_response

    def fake_verify_registration_response(**kwargs):  # noqa: D401
        return FakeVerification()

    monkeypatch.setattr(
        "backend.services.webauthn_service.parse_registration_credential_json",
        fake_parse_registration_credential_json,
    )
    monkeypatch.setattr(
        "backend.services.webauthn_service.verify_registration_response",
        fake_verify_registration_response,
    )

    # Minimal client registration response structure
    registration_response = {
        "id": "dummy",  # Normally base64url
        "rawId": "dummy",
        "response": {"attestationObject": "", "clientDataJSON": ""},
        "type": "public-key",
    }

    # Challenge (base64url for bytes 0x01 0x02 0x03)
    challenge = "AQID"

    credential_id, public_key_json = webauthn_service.verify_registration(
        registration_response=registration_response,
        challenge=challenge,
        user=user,
    )

    assert isinstance(credential_id, str)
    # Raw bytes marker should not appear in serialized JSON
    assert "b'" not in public_key_json, "Raw Python bytes repr leaked into JSON"

    # Parse JSON and ensure no value remains as bytes and all leaves are JSON primitives
    public_key_dict = json.loads(public_key_json)
    for leaf in _walk(public_key_dict):
        assert not isinstance(leaf, bytes), f"Found bytes leaf after sanitization: {leaf!r}"
        # Ensure leaf values are JSON safe types
        assert isinstance(leaf, (str, int, float, bool, type(None))), (
            f"Unexpected non-JSON primitive type after sanitization: {type(leaf)}"
        )

    # Ensure expected keys preserved
    assert "nested" in public_key_dict
    assert isinstance(public_key_dict["nested"], list)

    # Ensure top-level original byte values were transformed ("OKP" should become base64url "T0tQ")
    assert public_key_dict.get("kty") == "T0tQ"

