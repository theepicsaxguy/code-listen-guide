"""
Authentication routes for user registration, login, and token management.

Provides endpoints for:
- User registration with password hashing
- Login with JWT token generation
- Token refresh
- Current user retrieval
- Logout (token invalidation placeholder)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, limiter, oauth2_scheme
from backend.api.schemas.user import (
    TokenRefreshRequest,
    UserCreate,
    UserResponse,
    TokenResponse,
)
from backend.db.session import get_db
from backend.models.user import User
from backend.config import get_settings
from backend.utils.auth import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_access_token,
    verify_token_type,
    ACCESS_TOKEN_EXPIRE_DAYS,
)
from backend.utils.validators import validate_email_format, validate_password_strength

settings = get_settings()

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user.

    Creates a new user account with:
    - Email validation
    - Password hashing
    - Default free tier subscription
    - Initial credits

    Args:
        user_data: User registration data (email, password, name)
        db: Database session

    Returns:
        UserResponse with user data (password excluded)

    Raises:
        HTTPException: 400 if email already exists or validation fails
    """
    # Normalize email to lowercase for case-insensitive handling
    normalized_email = user_data.email.strip().lower()

    # Validate email format (use original case-insensitive form)
    if not validate_email_format(normalized_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    # Check if user already exists
    # Case-insensitive uniqueness check (handles legacy mixed-case rows)
    stmt = select(User).where(func.lower(User.email) == normalized_email)
    existing_user = db.scalars(stmt).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create new user
    new_user = User(
        email=normalized_email,
        hashed_password=hashed_password,
        name=user_data.name or normalized_email.split("@")[0],
        subscription_tier="free",
        subscription_status="active",
        credits_remaining=100,  # Default free credits
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login user and return JWT tokens.

    Authenticates user with email and password, returns access and refresh tokens.
    Also sets tokens in httpOnly cookies for browser-based authentication.

    Args:
        form_data: OAuth2 form data with username (email) and password
        db: Database session
        response: Response object to set cookies

    Returns:
        TokenResponse with access_token, refresh_token, and metadata

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email (username field in OAuth2 form)
    # Case-insensitive login: normalize provided username (email)
    login_email = form_data.username.strip().lower()
    stmt = select(User).where(func.lower(User.email) == login_email)
    user = db.scalars(stmt).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id), "is_admin": user.is_admin})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set tokens in httpOnly cookies for browser-based authentication
    # secure=True only in production (HTTPS), allow HTTP in development
    is_production = settings.environment.lower() in ("production", "prod")
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7 days
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        max_age=30 * 24 * 60 * 60,  # 30 days
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Convert to seconds
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    token: str = Depends(oauth2_scheme),
):
    """
    Logout user (invalidate token).

    Clears authentication cookies and optionally blacklists the token.

    Args:
        token: JWT access token
        response: Response object to clear cookies

    Returns:
        Success message

    Note: Token blacklisting with Redis can be added for enhanced security.
    """
    # Optional: Implement token blacklisting with Redis
    # redis_client.setex(f"blacklist:{token}", ACCESS_TOKEN_EXPIRE_MINUTES * 60, "1")

    # Clear authentication cookies
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(request: Request, current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        UserResponse with current user data
    """
    return current_user


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    payload: TokenRefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.

    Generates a new access token from a valid refresh token.
    Optionally rotates refresh token for enhanced security.

    Args:
        payload: TokenRefreshRequest containing the refresh token
        db: Database session

    Returns:
        TokenResponse with new access_token and refresh_token

    Raises:
        HTTPException: 401 if refresh token is invalid
    """
    # Verify token type
    refresh_token = payload.refresh_token

    if not verify_token_type(refresh_token, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    try:
        # Decode refresh token
        payload = decode_access_token(refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        # Verify user exists
        stmt = select(User).where(User.id == user_id)
        user = db.scalars(stmt).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        # Generate new tokens
        new_access_token = create_access_token(data={"sub": str(user.id), "is_admin": user.is_admin})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
