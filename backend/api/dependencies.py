"""
Shared dependencies for API routes.

Provides:
- get_current_user(): Extract and validate JWT token, return user
- get_current_active_user(): Ensure user account is active
- require_subscription(): Check user subscription tier
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from backend.db.session import get_db
from backend.models.user import User
from backend.utils.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
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
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
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
    tier_hierarchy = {
        "free": 0,
        "professional": 1,
        "team": 2,
        "enterprise": 3
    }

    async def _require_subscription(
        current_user: User = Depends(get_current_user)
    ) -> User:
        user_tier_level = tier_hierarchy.get(current_user.subscription_tier, 0)
        required_tier_level = tier_hierarchy.get(tier, 0)

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {tier} subscription or higher"
            )

        return current_user

    return _require_subscription
