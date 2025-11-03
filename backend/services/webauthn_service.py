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
        # Use JSON serialization to ensure all nested Pydantic models are converted
        import json
        
        def serialize_pydantic_model(obj):
            """Recursively serialize Pydantic models to plain dicts."""
            if hasattr(obj, 'model_dump_json'):
                # Use model_dump_json to get JSON string, then parse back
                # This ensures all nested models are serialized
                return json.loads(obj.model_dump_json())
            elif hasattr(obj, 'model_dump'):
                # Try model_dump with mode='json', but it might not be recursive enough
                dumped = obj.model_dump(mode='json')
                # Recursively process the result to catch any remaining Pydantic models
                return serialize_pydantic_model(dumped) if isinstance(dumped, dict) else dumped
            elif hasattr(obj, 'dict'):
                # Pydantic v1
                dumped = obj.dict()
                return serialize_pydantic_model(dumped) if isinstance(dumped, dict) else dumped
            elif isinstance(obj, dict):
                # Recursively process dict values
                return {k: serialize_pydantic_model(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                # Recursively process list items
                return [serialize_pydantic_model(item) for item in obj]
            else:
                return obj
        
        try:
            # Try to serialize the entire options object
            if hasattr(options, 'model_dump_json'):
                # Best approach: use JSON serialization which handles nested models
                options_json = options.model_dump_json()
                options_dict = json.loads(options_json)
                logger.debug(f"Options serialized via model_dump_json, keys: {list(options_dict.keys())}")
            elif hasattr(options, 'model_dump'):
                # Fallback: use model_dump and recursively process
                options_dict = serialize_pydantic_model(options)
            elif hasattr(options, 'dict'):
                options_dict = serialize_pydantic_model(options)
            else:
                # Fallback: try to convert to dict
                try:
                    options_dict = dict(options) if hasattr(options, '__iter__') else {}
                except Exception:
                    logger.error(f"Failed to convert options to dict, type: {type(options)}")
                    options_dict = {}
        except Exception as e:
            logger.error(f"Failed to serialize options object: {e}", exc_info=True)
            # Last resort: try basic conversion
            if hasattr(options, 'model_dump'):
                options_dict = options.model_dump(mode='json')
            elif hasattr(options, 'dict'):
                options_dict = options.dict()
            else:
                options_dict = {}
        
        # CRITICAL: Immediately serialize pubKeyCredParams BEFORE any iteration
        # This prevents "'PublicKeyCredentialParameters' object is not iterable" errors
        # The error happens when Python tries to iterate over a Pydantic model
        if isinstance(options_dict, dict) and 'pubKeyCredParams' in options_dict:
            pub_key_params = options_dict['pubKeyCredParams']
            logger.debug(f"Processing pubKeyCredParams: type={type(pub_key_params)}, is_list={isinstance(pub_key_params, (list, tuple))}")
            
            # CRITICAL: Check if it's a Pydantic model BEFORE any iteration attempts
            # Pydantic models can have __iter__ but aren't actually iterable in the way we need
            # The error "'PublicKeyCredentialParameters' object is not iterable" happens when
            # Python tries to iterate over a Pydantic model object
            if not isinstance(pub_key_params, (list, tuple, dict)):
                # It's not a list, tuple, or dict - might be a Pydantic model
                try:
                    # First, check if it's a Pydantic model by trying to serialize it
                    if hasattr(pub_key_params, 'model_dump_json'):
                        # Use JSON serialization to ensure it's converted
                        param_json = pub_key_params.model_dump_json()
                        param_dict = json.loads(param_json)
                        pub_key_params = [param_dict] if isinstance(param_dict, dict) else param_dict
                    elif hasattr(pub_key_params, 'model_dump'):
                        # Pydantic v2 model
                        param_dict = pub_key_params.model_dump(mode='json')
                        pub_key_params = [param_dict] if isinstance(param_dict, dict) else param_dict
                    elif hasattr(pub_key_params, 'dict'):
                        # Pydantic v1 model
                        param_dict = pub_key_params.dict()
                        pub_key_params = [param_dict] if isinstance(param_dict, dict) else param_dict
                    else:
                        # Not a Pydantic model, try to extract attributes
                        try:
                            pub_key_params = [{
                                'type': getattr(pub_key_params, 'type', 'public-key'),
                                'alg': int(getattr(pub_key_params, 'alg', -7)),
                            }]
                        except Exception:
                            # Fallback: default params
                            pub_key_params = [{'type': 'public-key', 'alg': -7}]
                except Exception as e:
                    logger.error(f"Failed to convert pubKeyCredParams object: {e}", exc_info=True)
                    logger.error(f"  Object type: {type(pub_key_params)}")
                    logger.error(f"  Object attributes: {dir(pub_key_params)}")
                    # Fallback: default params
                    pub_key_params = [{'type': 'public-key', 'alg': -7}]
            
            # Now check if it's a list/tuple that might contain Pydantic models
            if isinstance(pub_key_params, (list, tuple)):
                serialized_params = []
                try:
                    for param in pub_key_params:
                        if isinstance(param, dict):
                            # Already a dict, but ensure it's plain types
                            serialized_params.append(param)
                        elif hasattr(param, 'model_dump'):
                            # Pydantic v2 model
                            param_dict = param.model_dump(mode='json')
                            serialized_params.append(param_dict)
                        elif hasattr(param, 'dict'):
                            # Pydantic v1 model
                            param_dict = param.dict()
                            serialized_params.append(param_dict)
                        else:
                            # Extract type and alg from any object
                            try:
                                serialized_params.append({
                                    'type': getattr(param, 'type', 'public-key'),
                                    'alg': int(getattr(param, 'alg', -7)),
                                })
                            except Exception as e:
                                logger.warning(f"Failed to serialize pubKeyCredParam: {e}, using fallback")
                                serialized_params.append({'type': 'public-key', 'alg': -7})
                except Exception as e:
                    logger.error(f"Failed to iterate over pubKeyCredParams: {e}", exc_info=True)
                    # Fallback: create default params
                    serialized_params = [{'type': 'public-key', 'alg': -7}]
                options_dict['pubKeyCredParams'] = serialized_params
            elif pub_key_params is not None:
                # Single object (could be Pydantic model, dict, or other object)
                if isinstance(pub_key_params, dict):
                    # Already a dict, use as-is but wrap in list
                    options_dict['pubKeyCredParams'] = [pub_key_params]
                elif hasattr(pub_key_params, 'model_dump'):
                    # Pydantic v2 model
                    param_dict = pub_key_params.model_dump(mode='json')
                    options_dict['pubKeyCredParams'] = [param_dict]
                elif hasattr(pub_key_params, 'dict'):
                    # Pydantic v1 model
                    param_dict = pub_key_params.dict()
                    options_dict['pubKeyCredParams'] = [param_dict]
                else:
                    # Try to extract type and alg from object
                    try:
                        param_dict = {
                            'type': getattr(pub_key_params, 'type', 'public-key'),
                            'alg': int(getattr(pub_key_params, 'alg', -7)),
                        }
                        options_dict['pubKeyCredParams'] = [param_dict]
                    except Exception as e:
                        logger.error(f"Failed to extract pubKeyCredParam fields: {e}")
                        options_dict['pubKeyCredParams'] = [{'type': 'public-key', 'alg': -7}]
            else:
                # None or empty, set to empty list
                options_dict['pubKeyCredParams'] = []
        
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
        
        # Ensure exclude_credentials are properly serialized and have base64url-encoded IDs
        if 'excludeCredentials' in options_dict:
            exclude_creds = options_dict['excludeCredentials']
            # Serialize if it contains Pydantic models
            if isinstance(exclude_creds, (list, tuple)):
                serialized_creds = []
                for cred in exclude_creds:
                    if isinstance(cred, dict):
                        # Already a dict, just ensure ID is base64url
                        cred_copy = cred.copy()
                        if 'id' in cred_copy:
                            cred_id = cred_copy['id']
                            if isinstance(cred_id, bytes):
                                cred_copy['id'] = self._bytes_to_base64url(cred_id)
                        serialized_creds.append(cred_copy)
                    elif hasattr(cred, 'model_dump'):
                        # Pydantic model - serialize it
                        cred_dict = cred.model_dump(mode='json')
                        if 'id' in cred_dict and isinstance(cred_dict['id'], bytes):
                            cred_dict['id'] = self._bytes_to_base64url(cred_dict['id'])
                        serialized_creds.append(cred_dict)
                    elif hasattr(cred, 'dict'):
                        # Pydantic v1 model
                        cred_dict = cred.dict()
                        if 'id' in cred_dict and isinstance(cred_dict['id'], bytes):
                            cred_dict['id'] = self._bytes_to_base64url(cred_dict['id'])
                        serialized_creds.append(cred_dict)
                    else:
                        # Try to extract fields
                        try:
                            cred_dict = {
                                'id': self._bytes_to_base64url(getattr(cred, 'id', b'')) if isinstance(getattr(cred, 'id', None), bytes) else getattr(cred, 'id', ''),
                                'type': getattr(cred, 'type', 'public-key'),
                            }
                            if hasattr(cred, 'transports'):
                                cred_dict['transports'] = getattr(cred, 'transports', [])
                            serialized_creds.append(cred_dict)
                        except Exception as e:
                            logger.warning(f"Failed to serialize exclude credential: {e}")
                options_dict['excludeCredentials'] = serialized_creds
            elif exclude_creds and not isinstance(exclude_creds, dict):
                # Single Pydantic model object
                if hasattr(exclude_creds, 'model_dump'):
                    cred_dict = exclude_creds.model_dump(mode='json')
                    if 'id' in cred_dict and isinstance(cred_dict['id'], bytes):
                        cred_dict['id'] = self._bytes_to_base64url(cred_dict['id'])
                    options_dict['excludeCredentials'] = [cred_dict]
                elif hasattr(exclude_creds, 'dict'):
                    cred_dict = exclude_creds.dict()
                    if 'id' in cred_dict and isinstance(cred_dict['id'], bytes):
                        cred_dict['id'] = self._bytes_to_base64url(cred_dict['id'])
                    options_dict['excludeCredentials'] = [cred_dict]
                else:
                    # Fallback
                    cred_id = getattr(exclude_creds, 'id', b'')
                    if isinstance(cred_id, bytes):
                        cred_id = self._bytes_to_base64url(cred_id)
                    options_dict['excludeCredentials'] = [{
                        'id': cred_id,
                        'type': getattr(exclude_creds, 'type', 'public-key'),
                    }]
        
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
        
        # Final JSON serialization to ensure everything is plain Python types
        # This prevents any Pydantic models from slipping through
        def ensure_serializable(obj):
            """Recursively convert objects to JSON-serializable types."""
            if isinstance(obj, dict):
                return {k: ensure_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [ensure_serializable(item) for item in obj]
            elif hasattr(obj, 'model_dump'):
                # Pydantic v2 model
                return ensure_serializable(obj.model_dump(mode='json'))
            elif hasattr(obj, 'dict'):
                # Pydantic v1 model
                return ensure_serializable(obj.dict())
            elif hasattr(obj, '__dict__') and not isinstance(obj, (str, bytes, int, float, bool, type(None))):
                # Other object with __dict__
                return ensure_serializable(dict(obj.__dict__))
            elif isinstance(obj, bytes):
                # Convert bytes to base64url string
                return self._bytes_to_base64url(obj)
            elif isinstance(obj, (str, int, float, bool)) or obj is None:
                # Already serializable
                return obj
            else:
                # Fallback: convert to string
                logger.warning(f"Converting non-serializable object to string: {type(obj)}")
                return str(obj)
        
        # Ensure everything is serializable
        final_dict = ensure_serializable(converted_dict)
        
        # Double-check that pub_key_cred_params is a list
        if 'pub_key_cred_params' in final_dict:
            if not isinstance(final_dict['pub_key_cred_params'], list):
                logger.error(f"pub_key_cred_params is still not a list after serialization: {type(final_dict['pub_key_cred_params'])}")
                # Force it to be a list
                if final_dict['pub_key_cred_params']:
                    final_dict['pub_key_cred_params'] = [final_dict['pub_key_cred_params']]
                else:
                    final_dict['pub_key_cred_params'] = []
        
        # Log final structure for debugging
        logger.debug(f"Returning registration options:")
        logger.debug(f"  - challenge: {final_dict.get('challenge')}")
        logger.debug(f"  - user exists: {'user' in final_dict}")
        if 'user' in final_dict:
            user_keys = list(final_dict['user'].keys()) if isinstance(final_dict['user'], dict) else 'not a dict'
            logger.debug(f"  - user keys: {user_keys}")
        logger.debug(f"  - rp exists: {'rp' in final_dict}")
        logger.debug(f"  - pub_key_cred_params exists: {'pub_key_cred_params' in final_dict}")
        if 'pub_key_cred_params' in final_dict:
            pub_params = final_dict['pub_key_cred_params']
            logger.debug(f"  - pub_key_cred_params type: {type(pub_params)}")
            if isinstance(pub_params, list):
                logger.debug(f"  - pub_key_cred_params length: {len(pub_params)}")
                if len(pub_params) > 0:
                    logger.debug(f"  - pub_key_cred_params[0] type: {type(pub_params[0])}")
                    logger.debug(f"  - pub_key_cred_params[0]: {pub_params[0]}")
            else:
                logger.warning(f"  - pub_key_cred_params is not a list: {pub_params}")
        logger.debug(f"  - All keys in final_dict: {list(final_dict.keys())}")
        
        return final_dict

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
