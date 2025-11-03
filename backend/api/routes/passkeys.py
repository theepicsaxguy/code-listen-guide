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
    # Get user's existing passkeys
    stmt = select(Passkey).where(
        Passkey.user_id == current_user.id,
        Passkey.is_active == True  # noqa: E712
    )
    existing_passkeys = list(db.scalars(stmt).all())

    # Generate registration options
    options = webauthn_service.generate_registration_options(
        user=current_user,
        existing_passkeys=existing_passkeys,
    )

    # Store challenge for verification
    challenge = options["challenge"]
    challenge_key = f"reg:{current_user.id}:{challenge}"
    await challenge_store.store(
        challenge_key,
        {
            "user_id": str(current_user.id),
            "challenge": challenge,
        },
    )

    return PasskeyRegistrationOptionsResponse(
        options=options,
        challenge=challenge,
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
    """
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

    # Generate authentication options
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

    # Verify challenge
    challenge_key = f"auth:{passkey.user_id}:{auth_data.challenge}"
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

