"""
WebAuthn service for passkey registration and authentication.

Provides:
- Passkey registration challenge generation
- Passkey authentication challenge generation
- Credential verification
- Credential storage and retrieval

Uses the webauthn library for WebAuthn operations.
"""

import base64
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    COSEAlgorithmIdentifier,
)
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url

from backend.config import get_settings
from backend.models.passkey import Passkey
from backend.models.user import User

logger = logging.getLogger(__name__)

settings = get_settings()


class WebAuthnService:
    """Service for WebAuthn passkey operations using webauthn library."""

    def __init__(self):
        """Initialize WebAuthn service with relying party configuration."""
        # Get origin from frontend URL or default to localhost
        origin = settings.frontend_url or "http://localhost:4173"
        if origin.endswith("/"):
            origin = origin[:-1]

        # Extract RP ID from origin (domain without protocol)
        self.rp_id = origin.replace("https://", "").replace("http://", "").split(":")[0]
        self.rp_name = "Codebase Audiobook"
        self.origin = origin

        logger.info(f"Initialized WebAuthn service with RP ID: {self.rp_id}, Origin: {origin}")

    def _base64url_to_bytes(self, data: str) -> bytes:
        """Convert base64url string to bytes."""
        return base64url_to_bytes(data)

    def _bytes_to_base64url(self, data: bytes) -> str:
        """Convert bytes to base64url string."""
        return bytes_to_base64url(data)

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
        # Exclude existing credential IDs
        exclude_credentials = [
            PublicKeyCredentialDescriptor(
                id=self._base64url_to_bytes(pk.credential_id),
                type=PublicKeyCredentialType.PUBLIC_KEY,
            )
            for pk in existing_passkeys
            if pk.is_active
        ]

        # Generate registration options
        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=str(user.id).encode("utf-8"),
            user_name=user.email,
            user_display_name=user.name or user.email,
            exclude_credentials=exclude_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                user_verification=UserVerificationRequirement.PREFERRED,
                resident_key=ResidentKeyRequirement.REQUIRED,
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PSS_SHA_256,
            ],
        )

        # Convert options to dict (webauthn returns Pydantic models)
        # Try .model_dump() first (Pydantic v2), then .dict() (Pydantic v1), then fallback
        if hasattr(options, 'model_dump'):
            return options.model_dump(mode='json')
        elif hasattr(options, 'dict'):
            return options.dict()
        else:
            # Fallback: return as-is if already serializable
            return options

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
            # Verify the registration response
            verification = verify_registration_response(
                response=registration_response,
                expected_challenge=challenge,
                expected_origin=self.origin,
                expected_rp_id=self.rp_id,
                require_user_verification=True,
            )

            # Extract credential data
            credential_id = self._bytes_to_base64url(verification.credential_id)
            # Serialize the public key (COSE key dict)
            public_key_dict = verification.credential_public_key
            public_key_json = json.dumps(public_key_dict)

            logger.info(f"Successfully verified passkey registration for user {user.id}")
            return credential_id, public_key_json

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
            PublicKeyCredentialDescriptor(
                id=self._base64url_to_bytes(pk.credential_id),
                type=PublicKeyCredentialType.PUBLIC_KEY,
            )
            for pk in passkeys
            if pk.is_active
        ]

        # Generate authentication options
        options = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.PREFERRED,
        )

        # Convert options to dict (webauthn returns Pydantic models)
        # Try .model_dump() first (Pydantic v2), then .dict() (Pydantic v1), then fallback
        if hasattr(options, 'model_dump'):
            return options.model_dump(mode='json')
        elif hasattr(options, 'dict'):
            return options.dict()
        else:
            # Fallback: return as-is if already serializable
            return options

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
            # Parse public key from JSON
            public_key_dict = json.loads(passkey.public_key)

            # Verify the authentication
            verification = verify_authentication_response(
                response=authentication_response,
                expected_challenge=challenge,
                expected_origin=self.origin,
                expected_rp_id=self.rp_id,
                credential_public_key=public_key_dict,
                credential_current_sign_count=passkey.counter,
                require_user_verification=True,
            )

            # Update passkey counter and last_used_at
            passkey.counter = verification.new_sign_count
            passkey.last_used_at = datetime.utcnow()

            logger.info(f"Successfully verified passkey authentication for passkey {passkey.id}")
            return True

        except Exception as e:
            logger.error(f"Passkey authentication verification failed: {e}")
            raise ValueError(f"Authentication verification failed: {str(e)}")


# Global service instance
webauthn_service = WebAuthnService()
