"""
Shared dependencies for API routes.

TODO: Implementation steps:
1. Implement get_current_user() dependency
2. Implement verify_api_key() dependency (if using API keys)
3. Add rate limiting dependency
4. Add permission checking dependencies
5. Add request validation dependencies
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

    TODO:
    1. Decode JWT token
    2. Extract user ID from token
    3. Query user from database
    4. Check if user is active
    5. Return user object
    6. Raise 401 if invalid token or user not found
    """
    # TODO: Implement
    # try:
    #     payload = decode_access_token(token)
    #     user_id = payload.get("sub")
    #     if not user_id:
    #         raise HTTPException(status_code=401, detail="Invalid token")
    #
    #     user = db.query(User).filter(User.id == user_id).first()
    #     if not user:
    #         raise HTTPException(status_code=401, detail="User not found")
    #
    #     return user
    # except Exception:
    #     raise HTTPException(status_code=401, detail="Could not validate credentials")
    pass


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and check if active.

    TODO:
    - Add is_active field to User model
    - Check if user is active
    - Raise 403 if inactive
    """
    # TODO: Implement
    # if not current_user.is_active:
    #     raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


def require_subscription(tier: str):
    """
    Dependency factory for requiring specific subscription tier.

    Usage:
        @app.get("/premium-feature")
        def premium_feature(user: User = Depends(require_subscription("professional"))):
            ...

    TODO:
    - Create dependency that checks user subscription tier
    - Raise 403 if insufficient tier
    """
    async def _require_subscription(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # TODO: Implement tier checking
        # if current_user.subscription_tier < tier:
        #     raise HTTPException(status_code=403, detail="Insufficient subscription tier")
        return current_user

    return _require_subscription
