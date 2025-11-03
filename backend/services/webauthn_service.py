"""
WebAuthn service for passkey registration and authentication.

Provides:
- Passkey registration challenge generation
- Passkey authentication challenge generation
- Credential verification
- Credential storage and retrieval
"""

import base64
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
from uuid import uuid4

from pywebauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    RelyingParty,
)
from pywebauthn.helpers import bytes_to_base64url, base64url_to_bytes

from backend.config import get_settings
from backend.models.passkey import Passkey
from backend.models.user import User
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

settings = get_settings()


class WebAuthnService:
    """Service for WebAuthn passkey operations."""

    def __init__(self):
        """Initialize WebAuthn service with relying party configuration."""
        # Get origin from frontend URL or default to localhost
        origin = settings.frontend_url or "http://localhost:4173"
        if origin.endswith("/"):
            origin = origin[:-1]

        self.rp = RelyingParty(
            name="Codebase Audiobook",
            id=origin.replace("https://", "").replace("http://", "").split(":")[0],
            origin=origin,
        )
        logger.info(f"Initialized WebAuthn service with RP ID: {self.rp.id}, Origin: {origin}")

    def generate_registration_options(
        self, user: User, existing_passkeys: list[Passkey]
    ) -> Dict:
        """
        Generate registration options for passkey creation.

        Args:
            user: User registering the passkey
            existing_passkeys: List of existing passkeys for this user

        Returns:
            Dictionary with registration options (challenge, etc.)
        """
        # Exclude existing credential IDs to prevent duplicate registrations
        exclude_credentials = [
            {
                "id": base64url_to_bytes(pk.credential_id),
                "type": "public-key",
                "transports": ["internal", "usb", "nfc", "ble"],
            }
            for pk in existing_passkeys
            if pk.is_active
        ]

        options = generate_registration_options(
            rp=self.rp,
            user={
                "id": str(user.id).encode(),
                "name": user.email,
                "display_name": user.name or user.email,
            },
            challenge_length=32,
            exclude_credentials=exclude_credentials,
            authenticator_selection={
                "authenticator_attachment": "platform",  # Can be "platform" or "cross-platform"
                "user_verification": "preferred",
                "require_resident_key": True,
            },
        )

        return {
            "challenge": bytes_to_base64url(options.challenge),
            "rp": {
                "name": options.rp.name,
                "id": options.rp.id,
            },
            "user": {
                "id": bytes_to_base64url(options.user.id),
                "name": options.user.name,
                "display_name": options.user.display_name,
            },
            "pub_key_cred_params": [
                {
                    "type": param.type,
                    "alg": param.alg,
                }
                for param in options.pub_key_cred_params
            ],
            "authenticator_selection": {
                "authenticator_attachment": options.authenticator_selection.authenticator_attachment,
                "user_verification": options.authenticator_selection.user_verification,
                "require_resident_key": options.authenticator_selection.require_resident_key,
            },
            "timeout": options.timeout,
            "exclude_credentials": [
                {
                    "id": bytes_to_base64url(cred.id),
                    "type": cred.type,
                    "transports": cred.transports,
                }
                for cred in options.exclude_credentials
            ],
        }

    def verify_registration(
        self, registration_response: Dict, challenge: str, user: User
    ) -> Tuple[str, str]:
        """
        Verify passkey registration response and extract credential.

        Args:
            registration_response: Registration response from client
            challenge: Original challenge from registration options
            user: User registering the passkey

        Returns:
            Tuple of (credential_id, public_key) as base64 strings

        Raises:
            ValueError: If verification fails
        """
        try:
            # Convert challenge from base64url to bytes
            challenge_bytes = base64url_to_bytes(challenge)

            # Verify the registration response
            verification = verify_registration_response(
                rp=self.rp,
                expected_challenge=challenge_bytes,
                expected_origin=self.rp.origin,
                expected_rp_id=self.rp.id,
                registration_response=registration_response,
                expected_user_id=str(user.id).encode(),
            )

            # Extract credential data
            credential_id = bytes_to_base64url(verification.credential_id)
            public_key = json.dumps(verification.credential_public_key)

            logger.info(f"Successfully verified passkey registration for user {user.id}")
            return credential_id, public_key

        except Exception as e:
            logger.error(f"Passkey registration verification failed: {e}")
            raise ValueError(f"Registration verification failed: {str(e)}")

    def generate_authentication_options(
        self, user: User, passkeys: list[Passkey]
    ) -> Dict:
        """
        Generate authentication options for passkey login.

        Args:
            user: User authenticating
            passkeys: List of user's active passkeys

        Returns:
            Dictionary with authentication options (challenge, etc.)
        """
        # Include allowed credentials
        allow_credentials = [
            {
                "id": base64url_to_bytes(pk.credential_id),
                "type": "public-key",
                "transports": ["internal", "usb", "nfc", "ble"],
            }
            for pk in passkeys
            if pk.is_active
        ]

        options = generate_authentication_options(
            rp_id=self.rp.id,
            challenge_length=32,
            allow_credentials=allow_credentials,
            user_verification="preferred",
        )

        return {
            "challenge": bytes_to_base64url(options.challenge),
            "timeout": options.timeout,
            "rp_id": options.rp_id,
            "allow_credentials": [
                {
                    "id": bytes_to_base64url(cred.id),
                    "type": cred.type,
                    "transports": cred.transports,
                }
                for cred in options.allow_credentials
            ],
            "user_verification": options.user_verification,
        }

    def verify_authentication(
        self,
        authentication_response: Dict,
        challenge: str,
        passkey: Passkey,
    ) -> bool:
        """
        Verify passkey authentication response.

        Args:
            authentication_response: Authentication response from client
            challenge: Original challenge from authentication options
            passkey: Passkey being used for authentication

        Returns:
            True if verification succeeds

        Raises:
            ValueError: If verification fails
        """
        try:
            # Convert challenge and credential ID from base64url to bytes
            challenge_bytes = base64url_to_bytes(challenge)
            credential_id_bytes = base64url_to_bytes(passkey.credential_id)

            # Parse public key from JSON
            public_key = json.loads(passkey.public_key)

            # Verify the authentication response
            verification = verify_authentication_response(
                rp=self.rp,
                expected_challenge=challenge_bytes,
                expected_origin=self.rp.origin,
                expected_rp_id=self.rp.id,
                authentication_response=authentication_response,
                credential_public_key=public_key,
                credential_current_sign_count=passkey.counter,
            )

            # Update passkey counter and last_used_at
            # This will be saved by the caller
            passkey.counter = verification.new_sign_count
            passkey.last_used_at = datetime.utcnow()

            logger.info(f"Successfully verified passkey authentication for passkey {passkey.id}")
            return True

        except Exception as e:
            logger.error(f"Passkey authentication verification failed: {e}")
            raise ValueError(f"Authentication verification failed: {str(e)}")


# Global service instance
webauthn_service = WebAuthnService()

