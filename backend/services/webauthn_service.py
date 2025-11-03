"""
WebAuthn service for passkey registration and authentication.

Provides:
- Passkey registration challenge generation
- Passkey authentication challenge generation
- Credential verification
- Credential storage and retrieval

Uses the webauthn library for WebAuthn operations.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Tuple

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers import parse_registration_credential_json, parse_authentication_credential_json
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
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

        logger.info("Initialized WebAuthn service with RP ID: %s, Origin: %s", self.rp_id, origin)

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

        Uses the library's options_to_json() helper to ensure spec-conformant
        serialization with proper array handling for pubKeyCredParams.

        Args:
            user: User registering the passkey
            existing_passkeys: List of existing passkeys for this user

        Returns:
            Dictionary with registration options (challenge, etc.) in camelCase
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

        # Generate registration options (Pydantic model)
        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=str(user.id).encode("utf-8"),
            user_name=user.email,
            user_display_name=user.name or user.email,
            exclude_credentials=exclude_credentials if exclude_credentials else None,
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

        # Use library's options_to_json() for spec-conformant serialization
        # This ensures pubKeyCredParams is always an array and bytes are base64url-encoded
        options_json = options_to_json(options)
        
        # Parse JSON string to dict
        options_dict = json.loads(options_json)
        
        logger.debug("Generated registration options with keys: %s", list(options_dict.keys()))
        if 'pubKeyCredParams' in options_dict:
            _pk = options_dict['pubKeyCredParams']
            logger.debug(
                "pubKeyCredParams type: %s length: %s",
                type(_pk),
                len(_pk) if isinstance(_pk, list) else 'N/A'
            )
        
        return options_dict

    def verify_registration(
        self, registration_response: Dict, challenge: str, user: User
    ) -> Tuple[str, str]:
        """
        Verify passkey registration response and extract credential.

        Uses the library's parse_registration_credential_json() to parse client JSON
        and verify_registration_response() with correct parameter names.

        Args:
            registration_response: Registration response JSON from client
            challenge: Original challenge from registration options (base64url string)
            user: User registering the passkey

        Returns:
            Tuple of (credential_id, public_key) as base64 strings

        Raises:
            ValueError: If verification fails
        """
        try:
            # Parse client JSON into RegistrationCredential
            credential = parse_registration_credential_json(registration_response)
            
            # Convert challenge from base64url string to bytes
            expected_challenge_bytes = self._base64url_to_bytes(challenge)
            
            # Verify the registration response using correct parameter names
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=expected_challenge_bytes,
                expected_origin=self.origin,
                expected_rp_id=self.rp_id,
                require_user_verification=True,
            )

            # Extract credential data
            credential_id = self._bytes_to_base64url(verification.credential_id)
            # Serialize the public key (COSE key dict)
            public_key_dict = verification.credential_public_key
            public_key_json = json.dumps(public_key_dict)

            logger.info("Successfully verified passkey registration for user %s", user.id)
            return credential_id, public_key_json

        except Exception as e:
            logger.error("Passkey registration verification failed: %s", e, exc_info=True)
            raise ValueError(f"Registration verification failed: {str(e)}") from e

    def generate_authentication_options(
        self, user: User, passkeys: list[Passkey]
    ) -> Dict:
        """Generate authentication options for passkey login.

        Uses the library's options_to_json() helper to ensure all bytes values
        (credential IDs, challenge) are base64url encoded and safe for JSON transport.

        Args:
            user: User authenticating
            passkeys: List of user's active passkeys

        Returns:
            Dict containing properly serialized authentication options.
        """
        # Build allow list from stored base64url credential ids -> bytes for library
        allow_credentials = [
            PublicKeyCredentialDescriptor(
                id=self._base64url_to_bytes(pk.credential_id),
                type=PublicKeyCredentialType.PUBLIC_KEY,
            )
            for pk in passkeys
            if pk.is_active
        ] or None

        opts = generate_authentication_options(
            rp_id=self.rp_id,
            user_verification=UserVerificationRequirement.PREFERRED,
            allow_credentials=allow_credentials,
        )

        # Serialize with helper (returns JSON string) then load to dict
        return json.loads(options_to_json(opts))

    def generate_conditional_authentication_options(self) -> Dict:
        """Generate authentication options for conditional UI.

        No allow_credentials list is provided so the browser can surface all
        available platform credentials for the RP domain.
        """
        opts = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=None,
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        return json.loads(options_to_json(opts))

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

            # Parse client JSON into AuthenticationCredential
            credential = parse_authentication_credential_json(authentication_response)
            
            # Convert challenge from base64url string to bytes
            expected_challenge_bytes = self._base64url_to_bytes(challenge)
            
            # Verify the authentication using correct parameter names
            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=expected_challenge_bytes,
                expected_origin=self.origin,
                expected_rp_id=self.rp_id,
                credential_public_key=public_key_dict,
                credential_current_sign_count=passkey.counter,
                require_user_verification=True,
            )

            # Update passkey counter and last_used_at
            passkey.counter = verification.new_sign_count
            passkey.last_used_at = datetime.utcnow()

            logger.info("Successfully verified passkey authentication for passkey %s", passkey.id)
            return True

        except Exception as e:
            logger.error("Passkey authentication verification failed: %s", e)
            raise ValueError(f"Authentication verification failed: {str(e)}") from e


# Global service instance
webauthn_service = WebAuthnService()
