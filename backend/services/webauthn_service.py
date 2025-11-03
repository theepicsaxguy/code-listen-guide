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
            options_dict = options.model_dump(mode='json')
        elif hasattr(options, 'dict'):
            options_dict = options.dict()
        else:
            # Fallback: try to convert to dict
            try:
                options_dict = dict(options) if hasattr(options, '__iter__') else {}
            except Exception:
                logger.error(f"Failed to convert options to dict, type: {type(options)}")
                options_dict = {}
        
        # Log the structure for debugging
        logger.debug(f"Options dict type: {type(options_dict)}, keys: {list(options_dict.keys()) if isinstance(options_dict, dict) else 'not a dict'}")
        if isinstance(options_dict, dict):
            # Log specific fields we care about
            logger.debug(f"  - pubKeyCredParams exists: {'pubKeyCredParams' in options_dict}")
            logger.debug(f"  - pub_key_cred_params exists: {'pub_key_cred_params' in options_dict}")
            if 'pubKeyCredParams' in options_dict:
                logger.debug(f"  - pubKeyCredParams type: {type(options_dict['pubKeyCredParams'])}, value: {options_dict['pubKeyCredParams']}")
            if 'pub_key_cred_params' in options_dict:
                logger.debug(f"  - pub_key_cred_params type: {type(options_dict['pub_key_cred_params'])}, value: {options_dict['pub_key_cred_params']}")
        
        # Ensure we have a dict
        if not isinstance(options_dict, dict):
            logger.error(f"Options dict is not a dict, type: {type(options_dict)}, value: {options_dict}")
            raise ValueError(f"Invalid options format: expected dict, got {type(options_dict)}")
        
        # Check if challenge exists (might be nested or have different name)
        challenge = None
        if 'challenge' in options_dict:
            challenge = options_dict['challenge']
        elif hasattr(options, 'challenge'):
            # Fallback: try to get from original object
            challenge = getattr(options, 'challenge', None)
            if challenge:
                options_dict['challenge'] = challenge
        
        # Ensure challenge is a string (might be bytes or base64url)
        if challenge is not None:
            # If challenge is bytes, convert to base64url string
            if isinstance(challenge, bytes):
                options_dict['challenge'] = self._bytes_to_base64url(challenge)
            # If challenge is already a string, ensure it's base64url format
            elif not isinstance(challenge, str):
                options_dict['challenge'] = str(challenge)
        else:
            logger.warning(f"Challenge not found in options_dict. Keys: {list(options_dict.keys())}")
            # Try to extract from publicKeyCredentialCreationOptions if nested
            if 'publicKey' in options_dict:
                pub_key = options_dict['publicKey']
                if isinstance(pub_key, dict) and 'challenge' in pub_key:
                    challenge = pub_key['challenge']
                    if isinstance(challenge, bytes):
                        options_dict['challenge'] = self._bytes_to_base64url(challenge)
                    else:
                        options_dict['challenge'] = str(challenge)
                    logger.info("Found challenge in nested publicKey structure")
            else:
                # If still no challenge, this is an error
                logger.error(f"No challenge found in options. Available keys: {list(options_dict.keys())}")
                raise ValueError("Challenge not found in registration options")
        
        # Ensure user field exists and has proper structure
        if 'user' not in options_dict:
            # Try to get from original object
            if hasattr(options, 'user'):
                user_obj = getattr(options, 'user', None)
                if user_obj:
                    if hasattr(user_obj, 'model_dump'):
                        options_dict['user'] = user_obj.model_dump(mode='json')
                    elif hasattr(user_obj, 'dict'):
                        options_dict['user'] = user_obj.dict()
                    elif isinstance(user_obj, dict):
                        options_dict['user'] = user_obj
                    else:
                        # Try to convert to dict
                        try:
                            options_dict['user'] = {
                                'id': getattr(user_obj, 'id', None),
                                'name': getattr(user_obj, 'name', None),
                                'displayName': getattr(user_obj, 'display_name', None) or getattr(user_obj, 'displayName', None),
                            }
                        except Exception as e:
                            logger.error(f"Failed to extract user from object: {e}")
                            options_dict['user'] = {}
            else:
                logger.warning("User field not found in options_dict and not in original object")
                options_dict['user'] = {}
        
        # Ensure user.id is base64url-encoded string (webauthn expects this)
        if 'user' in options_dict and isinstance(options_dict['user'], dict):
            user_data = options_dict['user']
            if 'id' in user_data:
                user_id = user_data['id']
                # If user_id is bytes, convert to base64url string
                if isinstance(user_id, bytes):
                    options_dict['user']['id'] = self._bytes_to_base64url(user_id)
                elif not isinstance(user_id, str):
                    # Convert UUID or other types to base64url-encoded bytes
                    user_id_bytes = str(user_id).encode('utf-8')
                    options_dict['user']['id'] = self._bytes_to_base64url(user_id_bytes)
            
            # Ensure user.name and user.displayName exist (frontend expects display_name)
            if 'displayName' not in options_dict['user'] and 'display_name' in options_dict['user']:
                options_dict['user']['displayName'] = options_dict['user']['display_name']
            if 'displayName' not in options_dict['user']:
                # Fallback to name if displayName not found
                options_dict['user']['displayName'] = options_dict['user'].get('name', '')
            
            # Ensure display_name is also set (some frontend code might use snake_case)
            if 'display_name' not in options_dict['user']:
                options_dict['user']['display_name'] = options_dict['user'].get('displayName', '')
        
        # Ensure exclude_credentials have base64url-encoded IDs
        if 'excludeCredentials' in options_dict:
            exclude_creds = options_dict['excludeCredentials']
            if isinstance(exclude_creds, list):
                for cred in exclude_creds:
                    if isinstance(cred, dict) and 'id' in cred:
                        cred_id = cred['id']
                        if isinstance(cred_id, bytes):
                            cred['id'] = self._bytes_to_base64url(cred_id)
        
        # Convert camelCase field names to snake_case for frontend compatibility
        # Frontend expects: pub_key_cred_params, authenticator_selection, exclude_credentials
        field_mapping = {
            'pubKeyCredParams': 'pub_key_cred_params',
            'authenticatorSelection': 'authenticator_selection',
            'excludeCredentials': 'exclude_credentials',
            'userVerification': 'user_verification',
            'authenticatorAttachment': 'authenticator_attachment',
            'requireResidentKey': 'require_resident_key',
            'displayName': 'display_name',  # For user object
        }
        
        # Convert top-level fields (convert camelCase to snake_case)
        converted_dict = {}
        for key, value in options_dict.items():
            new_key = field_mapping.get(key, key)
            # Always use the snake_case version for frontend compatibility
            converted_dict[new_key] = value
            # Keep original key too if it's different (for backwards compatibility)
            if new_key != key and key not in converted_dict:
                # Don't duplicate if already converted
                pass
        
        # Convert nested user object fields
        if 'user' in converted_dict and isinstance(converted_dict['user'], dict):
            user_dict = {}
            for key, value in converted_dict['user'].items():
                new_key = field_mapping.get(key, key)
                user_dict[new_key] = value
            converted_dict['user'] = user_dict
        
        # Convert nested authenticator_selection fields
        if 'authenticator_selection' in converted_dict and isinstance(converted_dict['authenticator_selection'], dict):
            auth_sel_dict = {}
            for key, value in converted_dict['authenticator_selection'].items():
                new_key = field_mapping.get(key, key)
                auth_sel_dict[new_key] = value
            converted_dict['authenticator_selection'] = auth_sel_dict
        
        # Ensure pub_key_cred_params exists and is properly formatted as an array
        if 'pub_key_cred_params' not in converted_dict:
            # Try camelCase version from original dict
            if 'pubKeyCredParams' in options_dict:
                converted_dict['pub_key_cred_params'] = options_dict['pubKeyCredParams']
            else:
                logger.error("pub_key_cred_params not found in options")
                logger.error(f"Available keys in options_dict: {list(options_dict.keys())}")
                logger.error(f"Available keys in converted_dict: {list(converted_dict.keys())}")
                # Try to get from original object
                if hasattr(options, 'pub_key_cred_params'):
                    pub_key_params = getattr(options, 'pub_key_cred_params', [])
                    # Check if it's actually a list/tuple, not just iterable
                    if isinstance(pub_key_params, (list, tuple)):
                        # Convert Pydantic models to dicts if needed
                        converted_dict['pub_key_cred_params'] = [
                            param.model_dump(mode='json') if hasattr(param, 'model_dump') else
                            param.dict() if hasattr(param, 'dict') else
                            dict(param) if hasattr(param, '__dict__') and not isinstance(param, dict) else param
                            for param in pub_key_params
                        ]
                    elif pub_key_params:
                        # Single object, wrap in list
                        param = pub_key_params
                        converted_dict['pub_key_cred_params'] = [{
                            'type': getattr(param, 'type', 'public-key'),
                            'alg': getattr(param, 'alg', -7),
                        }]
                    else:
                        converted_dict['pub_key_cred_params'] = []
                elif hasattr(options, 'pubKeyCredParams'):
                    pub_key_params = getattr(options, 'pubKeyCredParams', [])
                    if isinstance(pub_key_params, (list, tuple)):
                        converted_dict['pub_key_cred_params'] = [
                            param.model_dump(mode='json') if hasattr(param, 'model_dump') else
                            param.dict() if hasattr(param, 'dict') else
                            dict(param) if hasattr(param, '__dict__') and not isinstance(param, dict) else param
                            for param in pub_key_params
                        ]
                    elif pub_key_params:
                        # Single object, wrap in list
                        param = pub_key_params
                        converted_dict['pub_key_cred_params'] = [{
                            'type': getattr(param, 'type', 'public-key'),
                            'alg': getattr(param, 'alg', -7),
                        }]
                    else:
                        converted_dict['pub_key_cred_params'] = []
                else:
                    logger.error("Could not find pub_key_cred_params in any form")
                    # Set empty array as fallback
                    converted_dict['pub_key_cred_params'] = []
        
        # Ensure pub_key_cred_params is a list and each item is a dict
        if 'pub_key_cred_params' in converted_dict:
            pub_key_params = converted_dict['pub_key_cred_params']
            if not isinstance(pub_key_params, (list, tuple)):
                logger.warning(f"pub_key_cred_params is not a list, type: {type(pub_key_params)}, value: {pub_key_params}")
                # Try to convert single object to list
                if pub_key_params:
                    # Check if it's a Pydantic model or dict-like
                    if hasattr(pub_key_params, 'model_dump'):
                        param_dict = pub_key_params.model_dump(mode='json')
                    elif hasattr(pub_key_params, 'dict'):
                        param_dict = pub_key_params.dict()
                    elif hasattr(pub_key_params, '__dict__'):
                        param_dict = dict(pub_key_params.__dict__)
                    elif isinstance(pub_key_params, dict):
                        param_dict = pub_key_params
                    else:
                        # Try to extract type and alg
                        param_dict = {
                            'type': getattr(pub_key_params, 'type', 'public-key'),
                            'alg': getattr(pub_key_params, 'alg', -7),
                        }
                    converted_dict['pub_key_cred_params'] = [param_dict]
                else:
                    converted_dict['pub_key_cred_params'] = []
            else:
                # Ensure each item is a dict (not a Pydantic model)
                converted_list = []
                for param in pub_key_params:
                    if isinstance(param, dict):
                        converted_list.append(param)
                    elif hasattr(param, 'model_dump'):
                        converted_list.append(param.model_dump(mode='json'))
                    elif hasattr(param, 'dict'):
                        converted_list.append(param.dict())
                    elif hasattr(param, '__dict__'):
                        converted_list.append(dict(param.__dict__))
                    else:
                        # Try to extract type and alg
                        converted_list.append({
                            'type': getattr(param, 'type', 'public-key'),
                            'alg': getattr(param, 'alg', -7),
                        })
                converted_dict['pub_key_cred_params'] = converted_list
        
        # Ensure exclude_credentials exists
        if 'exclude_credentials' not in converted_dict:
            if 'excludeCredentials' in options_dict:
                converted_dict['exclude_credentials'] = options_dict['excludeCredentials']
        
        # Final verification - ensure required fields exist
        required_fields = ['challenge', 'rp', 'user', 'pub_key_cred_params']
        missing_fields = [field for field in required_fields if field not in converted_dict]
        if missing_fields:
            logger.error(f"Missing required fields in registration options: {missing_fields}")
            logger.error(f"Available keys: {list(converted_dict.keys())}")
            # Don't raise here - let the frontend handle it, but log the issue
        
        # Log final structure for debugging
        logger.debug(f"Returning registration options:")
        logger.debug(f"  - challenge: {converted_dict.get('challenge')}")
        logger.debug(f"  - user exists: {'user' in converted_dict}")
        if 'user' in converted_dict:
            user_keys = list(converted_dict['user'].keys()) if isinstance(converted_dict['user'], dict) else 'not a dict'
            logger.debug(f"  - user keys: {user_keys}")
        logger.debug(f"  - rp exists: {'rp' in converted_dict}")
        logger.debug(f"  - pub_key_cred_params exists: {'pub_key_cred_params' in converted_dict}")
        if 'pub_key_cred_params' in converted_dict:
            pub_params = converted_dict['pub_key_cred_params']
            logger.debug(f"  - pub_key_cred_params type: {type(pub_params)}")
            if isinstance(pub_params, list):
                logger.debug(f"  - pub_key_cred_params length: {len(pub_params)}")
                if len(pub_params) > 0:
                    logger.debug(f"  - pub_key_cred_params[0] type: {type(pub_params[0])}")
                    logger.debug(f"  - pub_key_cred_params[0]: {pub_params[0]}")
            else:
                logger.warning(f"  - pub_key_cred_params is not a list: {pub_params}")
        logger.debug(f"  - All keys in converted_dict: {list(converted_dict.keys())}")
        
        return converted_dict

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

    def generate_conditional_authentication_options(self) -> Dict:
        """
        Generate authentication options for conditional UI (no email required).

        Returns:
            Dictionary with authentication options (challenge, etc.)
            Without allow_credentials, so browser shows all available passkeys.
        """
        # Generate authentication options without allow_credentials
        # This enables conditional UI where browser shows all passkeys for the domain
        options = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=None,  # None enables conditional UI
            user_verification=UserVerificationRequirement.PREFERRED,
        )

        # Convert options to dict
        if hasattr(options, 'model_dump'):
            return options.model_dump(mode='json')
        elif hasattr(options, 'dict'):
            return options.dict()
        else:
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
