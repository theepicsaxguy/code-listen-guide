"""
Passkey (WebAuthn) authentication routes.

Provides endpoints for:
- Passkey registration (create new passkey)
- Passkey authentication (login with passkey)
- Passkey management (list, delete passkeys)
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, limiter
from backend.api.schemas.user import (
    PasskeyRegistrationOptionsResponse,
    PasskeyRegistrationRequest,
    PasskeyRegistrationResponse,
    PasskeyAuthenticationOptionsRequest,
    PasskeyAuthenticationOptionsResponse,
    PasskeyAuthenticationRequest,
    PasskeyResponse,
    TokenResponse,
)
from backend.db.session import get_db
from backend.models.passkey import Passkey
from backend.models.user import User
from backend.services.webauthn_service import webauthn_service
from webauthn.helpers import bytes_to_base64url
from backend.utils.auth import create_access_token, create_refresh_token, ACCESS_TOKEN_EXPIRE_DAYS
from backend.utils.challenge_store import challenge_store

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth/passkeys", tags=["passkeys"])


@router.post(
    "/registration/options",
    operation_id="getPasskeyRegistrationOptions",
    response_model=PasskeyRegistrationOptionsResponse,
)
@limiter.limit("10/minute")
async def get_passkey_registration_options(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate passkey registration options.

    Returns challenge and options for creating a new passkey.
    """
    try:
        # Get user's existing passkeys
        stmt = select(Passkey).where(
            Passkey.user_id == current_user.id,
            Passkey.is_active == True  # noqa: E712
        )
        existing_passkeys = list(db.scalars(stmt).all())

        logger.info(f"Generating registration options for user {current_user.id} with {len(existing_passkeys)} existing passkeys")

        # Generate registration options
        options = webauthn_service.generate_registration_options(
            user=current_user,
            existing_passkeys=existing_passkeys,
        )

        logger.debug(f"Generated options keys: {list(options.keys()) if isinstance(options, dict) else 'not a dict'}")

        # Extract challenge from options
        if not isinstance(options, dict):
            logger.error(f"Options is not a dict, type: {type(options)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid registration options format",
            )

        challenge = options.get("challenge")
        if not challenge:
            logger.error(f"Challenge not found in options. Options keys: {list(options.keys())}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Challenge not found in registration options",
            )

        # Force JSON serialization to ensure all nested objects are plain dicts
        # This prevents Pydantic models from slipping through FastAPI's serialization
        try:
            # Recursively serialize to ensure everything is plain Python types
            # Use a custom function to handle bytes and Pydantic models
            def make_serializable(obj):
                """Recursively make object JSON serializable."""
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [make_serializable(item) for item in obj]
                elif isinstance(obj, bytes):
                    # Convert bytes to base64url string
                    return bytes_to_base64url(obj)
                elif hasattr(obj, 'model_dump'):
                    # Pydantic v2 model
                    return make_serializable(obj.model_dump(mode='json'))
                elif hasattr(obj, 'dict'):
                    # Pydantic v1 model
                    return make_serializable(obj.dict())
                elif isinstance(obj, (str, int, float, bool)) or obj is None:
                    return obj
                else:
                    # Fallback: convert to string for unknown types
                    logger.warning(f"Converting non-serializable object to string: {type(obj)}")
                    return str(obj)
            
            options_serialized = make_serializable(options)
            logger.debug(f"Options serialized successfully, keys: {list(options_serialized.keys())}")
            
            # Verify pub_key_cred_params is a list
            if 'pub_key_cred_params' in options_serialized:
                pub_params = options_serialized['pub_key_cred_params']
                if not isinstance(pub_params, list):
                    logger.error(f"pub_key_cred_params is still not a list after serialization: {type(pub_params)}")
                    options_serialized['pub_key_cred_params'] = [pub_params] if pub_params else []
        except Exception as e:
            logger.error(f"Failed to serialize options: {e}", exc_info=True)
            # If JSON serialization fails, log the structure for debugging
            logger.error(f"Options structure: {type(options)}, keys: {list(options.keys()) if isinstance(options, dict) else 'not a dict'}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to serialize registration options: {str(e)}",
            )

        # Store challenge for verification
        challenge_key = f"reg:{current_user.id}:{challenge}"
        try:
            await challenge_store.store(
                challenge_key,
                {
                    "user_id": str(current_user.id),
                    "challenge": challenge,
                },
            )
        except Exception as e:
            logger.error(f"Failed to store challenge: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to store challenge: {str(e)}",
            )

        # Final validation: ensure the response can be serialized by FastAPI
        # Log the structure to help debug if there are still issues
        logger.debug(f"Final options structure check:")
        logger.debug(f"  - Type: {type(options_serialized)}")
        logger.debug(f"  - Keys: {list(options_serialized.keys()) if isinstance(options_serialized, dict) else 'not a dict'}")
        if isinstance(options_serialized, dict) and 'pub_key_cred_params' in options_serialized:
            pub_params = options_serialized['pub_key_cred_params']
            logger.debug(f"  - pub_key_cred_params type: {type(pub_params)}")
            logger.debug(f"  - pub_key_cred_params is list: {isinstance(pub_params, list)}")
            if isinstance(pub_params, list) and len(pub_params) > 0:
                logger.debug(f"  - pub_key_cred_params[0] type: {type(pub_params[0])}")
                logger.debug(f"  - pub_key_cred_params[0]: {pub_params[0]}")
        
        # Return JSONResponse directly to bypass Pydantic serialization
        # This ensures all nested objects remain as plain dicts/lists
        try:
            # Double-check: ensure pub_key_cred_params is definitely a list
            if 'pub_key_cred_params' in options_serialized:
                if not isinstance(options_serialized['pub_key_cred_params'], list):
                    logger.error(f"CRITICAL: pub_key_cred_params is still not a list! Type: {type(options_serialized['pub_key_cred_params'])}")
                    logger.error(f"Value: {options_serialized['pub_key_cred_params']}")
                    # Force it to be a list
                    if options_serialized['pub_key_cred_params']:
                        options_serialized['pub_key_cred_params'] = [dict(options_serialized['pub_key_cred_params']) if hasattr(options_serialized['pub_key_cred_params'], '__dict__') else options_serialized['pub_key_cred_params']]
                    else:
                        options_serialized['pub_key_cred_params'] = []
            
            # Force a JSON round-trip to ensure everything is plain Python types
            # This is the final guarantee that no Pydantic models remain
            import json
            try:
                # Custom JSON encoder that handles bytes by converting to base64url
                def json_encoder(obj):
                    if isinstance(obj, bytes):
                        return bytes_to_base64url(obj)
                    elif hasattr(obj, 'model_dump_json'):
                        return json.loads(obj.model_dump_json())
                    elif hasattr(obj, 'model_dump'):
                        return obj.model_dump(mode='json')
                    elif hasattr(obj, 'dict'):
                        return obj.dict()
                    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
                
                # Serialize to JSON and parse back - this ensures all objects are plain dicts/lists
                json_str = json.dumps(options_serialized, default=json_encoder)
                options_final = json.loads(json_str)
                
                # Verify pub_key_cred_params one more time
                if 'pub_key_cred_params' in options_final:
                    if not isinstance(options_final['pub_key_cred_params'], list):
                        logger.error(f"FINAL CHECK FAILED: pub_key_cred_params is not a list after JSON round-trip!")
                        options_final['pub_key_cred_params'] = []
                
                response_data = {
                    "options": options_final,
                    "challenge": challenge,
                }
                logger.debug("Returning JSONResponse with fully serialized data")
                return JSONResponse(content=response_data)
            except Exception as json_error:
                logger.error(f"JSON round-trip failed: {json_error}", exc_info=True)
                # Fallback: return as-is but log the error
                response_data = {
                    "options": options_serialized,
                    "challenge": challenge,
                }
                return JSONResponse(content=response_data)
        except Exception as e:
            logger.error(f"Failed to create response: {e}", exc_info=True)
            logger.error(f"Options structure: {options_serialized}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create response: {str(e)}",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating passkey registration options: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate registration options: {str(e)}",
        )


@router.post(
    "/registration",
    operation_id="registerPasskey",
    response_model=PasskeyRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def register_passkey(
    request: Request,
    registration_data: PasskeyRegistrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Complete passkey registration.

    Verifies the registration response and stores the passkey credential.
    """
    # Verify challenge
    challenge_key = f"reg:{current_user.id}:{registration_data.challenge}"
    stored_challenge = await challenge_store.get(challenge_key)
    if not stored_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired challenge",
        )

    # Remove challenge after use
    await challenge_store.delete(challenge_key)

    # Verify registration
    try:
        credential_id, public_key = webauthn_service.verify_registration(
            registration_response=registration_data.registration_response,
            challenge=registration_data.challenge,
            user=current_user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Check if credential already exists
    existing = db.query(Passkey).filter(
        Passkey.credential_id == credential_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Passkey already registered",
        )

    # Create passkey record
    passkey = Passkey(
        user_id=current_user.id,
        credential_id=credential_id,
        public_key=public_key,
        name=registration_data.name or "Unnamed Passkey",
        counter=0,
    )

    db.add(passkey)
    db.commit()
    db.refresh(passkey)

    logger.info(f"Passkey {passkey.id} registered for user {current_user.id}")

    return PasskeyRegistrationResponse(
        passkey_id=passkey.id,
        name=passkey.name,
    )


@router.post(
    "/authentication/options",
    operation_id="getPasskeyAuthenticationOptions",
    response_model=PasskeyAuthenticationOptionsResponse,
)
@limiter.limit("20/minute")
async def get_passkey_authentication_options(
    request: Request,
    auth_data: PasskeyAuthenticationOptionsRequest,
    db: Session = Depends(get_db),
):
    """
    Generate passkey authentication options.

    Returns challenge and options for authenticating with a passkey.
    Supports conditional UI (no email required) when email is not provided.
    """
    # If email is provided, use traditional flow
    if auth_data.email:
        # Find user by email
        stmt = select(User).where(User.email == auth_data.email.lower())
        user = db.scalars(stmt).first()

        if not user:
            # Don't reveal if user exists (security best practice)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )

        # Get user's active passkeys
        stmt = select(Passkey).where(
            Passkey.user_id == user.id,
            Passkey.is_active == True  # noqa: E712
        )
        passkeys = list(db.scalars(stmt).all())

        if not passkeys:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No passkeys registered for this user",
            )

        # Generate authentication options with specific credentials
        options = webauthn_service.generate_authentication_options(
            user=user,
            passkeys=passkeys,
        )

        # Store challenge for verification
        challenge = options["challenge"]
        challenge_key = f"auth:{user.id}:{challenge}"
        await challenge_store.store(
            challenge_key,
            {
                "user_id": str(user.id),
                "challenge": challenge,
            },
        )
    else:
        # Conditional UI flow - no email, no specific credentials
        # Browser will show all available passkeys for this domain
        options = webauthn_service.generate_conditional_authentication_options()

        # Store challenge without user_id (will be determined from credential)
        challenge = options["challenge"]
        challenge_key = f"auth:conditional:{challenge}"
        await challenge_store.store(
            challenge_key,
            {
                "challenge": challenge,
            },
        )

    return PasskeyAuthenticationOptionsResponse(
        options=options,
        challenge=challenge,
    )


@router.post(
    "/authentication",
    operation_id="authenticatePasskey",
    response_model=TokenResponse,
)
@limiter.limit("20/minute")
async def authenticate_passkey(
    request: Request,
    response: Response,
    auth_data: PasskeyAuthenticationRequest,
    db: Session = Depends(get_db),
):
    """
    Complete passkey authentication.

    Verifies the authentication response and returns JWT tokens.
    Supports both traditional (with email) and conditional UI flows.
    """
    # Find passkey by credential ID
    passkey = db.query(Passkey).filter(
        Passkey.credential_id == auth_data.credential_id,
        Passkey.is_active == True  # noqa: E712
    ).first()

    if not passkey:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )

    # Try to verify challenge - check both traditional and conditional UI keys
    challenge_key = f"auth:{passkey.user_id}:{auth_data.challenge}"
    stored_challenge = await challenge_store.get(challenge_key)
    
    # If not found, try conditional UI challenge
    if not stored_challenge:
        challenge_key = f"auth:conditional:{auth_data.challenge}"
        stored_challenge = await challenge_store.get(challenge_key)
    
    if not stored_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired challenge",
        )

    # Remove challenge after use
    await challenge_store.delete(challenge_key)

    # Verify authentication
    try:
        webauthn_service.verify_authentication(
            authentication_response=auth_data.authentication_response,
            challenge=auth_data.challenge,
            passkey=passkey,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    # Update passkey (counter and last_used_at)
    db.commit()

    # Get user
    user = db.query(User).filter(User.id == passkey.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Generate tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "is_admin": user.is_admin}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set tokens in httpOnly cookies
    from backend.config import get_settings
    settings = get_settings()
    is_production = settings.environment.lower() in ("production", "prod")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=is_production,
        max_age=30 * 24 * 60 * 60,
    )

    logger.info(f"User {user.id} authenticated with passkey {passkey.id}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )


@router.get(
    "",
    operation_id="listPasskeys",
    response_model=List[PasskeyResponse],
)
async def list_passkeys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List user's passkeys.
    """
    stmt = select(Passkey).where(Passkey.user_id == current_user.id)
    passkeys = list(db.scalars(stmt).all())

    return passkeys


@router.delete(
    "/{passkey_id}",
    operation_id="deletePasskey",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_passkey(
    passkey_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a passkey.

    Soft deletes by setting is_active to False.
    """
    from uuid import UUID

    try:
        pk_id = UUID(passkey_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid passkey ID",
        )

    passkey = db.query(Passkey).filter(
        Passkey.id == pk_id,
        Passkey.user_id == current_user.id,
    ).first()

    if not passkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passkey not found",
        )

    # Soft delete
    passkey.is_active = False
    db.commit()

    logger.info(f"Passkey {passkey_id} deleted for user {current_user.id}")

    return None

