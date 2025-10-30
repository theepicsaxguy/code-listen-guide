"""
Shared dependencies for API routes.

Provides:
- get_current_user(): Extract and validate JWT token, return user
- get_current_active_user(): Ensure user account is active
- require_subscription(): Check user subscription tier
"""

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.config import get_settings
from backend.db.session import get_db
from backend.models.user import User
from backend.utils.auth import decode_access_token

class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """
    OAuth2 scheme that accepts tokens from both Authorization header and cookies.

    This allows Swagger UI to work seamlessly with browser-based authentication
    while still supporting API clients using Authorization headers.
    """
    async def __call__(self, request: Request) -> Optional[str]:
        # First try to get token from Authorization header
        authorization: str = request.headers.get("Authorization")
        if authorization:
            scheme, param = authorization.split()
            if scheme.lower() == "bearer":
                return param

        # Fall back to cookie if no Authorization header
        token = request.cookies.get("access_token")
        if token:
            return token

        # If neither found, raise exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/auth/login")

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    storage_uri=settings.rate_limit_storage_uri,
    storage_options=settings.rate_limit_storage_options,
)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        token: JWT access token from Authorization header
        db: Database session

    Returns:
        User object for the authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id_value = payload.get("sub")
        is_admin = payload.get("is_admin", False) # Extract is_admin from token
        if user_id_value is None:
            raise credentials_exception
        user_id = uuid.UUID(str(user_id_value))
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    user.is_admin = is_admin # Set is_admin on the user object
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and check if active.

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User object if active

    Raises:
        HTTPException: 403 if user account is inactive

    Note:
        Currently returns all users as active.
        Uncomment the check below when is_active field is added to User model.
    """
    # Uncomment when User.is_active field is added:
    # if hasattr(current_user, 'is_active') and not current_user.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Inactive user account"
    #     )
    return current_user


def require_subscription(tier: str):
    """
    Dependency factory for requiring specific subscription tier.

    Usage:
        @app.get("/premium-feature")
        def premium_feature(user: User = Depends(require_subscription("professional"))):
            ...

    Args:
        tier: Required subscription tier

    Returns:
        Dependency function that validates subscription tier
    """
    tier_hierarchy = {"free": 0, "professional": 1, "team": 2, "enterprise": 3}

    async def _require_subscription(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_tier_level = tier_hierarchy.get(current_user.subscription_tier, 0)
        required_tier_level = tier_hierarchy.get(tier, 0)

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {tier} subscription or higher",
            )

        return current_user

    return _require_subscription


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency for requiring admin privileges.

    Usage:
        @app.get("/admin/users")
        def list_all_users(user: User = Depends(require_admin)):
            ...

    Args:
        current_user: Authenticated user from get_current_user

    Returns:
        User object if user is admin

    Raises:
        HTTPException: 403 if user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return current_user
