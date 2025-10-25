"""
Authentication routes for user registration, login, and token management.

Provides endpoints for:
- User registration with password hashing
- Login with JWT token generation
- Token refresh
- Current user retrieval
- Logout (token invalidation placeholder)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user, limiter
from backend.api.schemas.user import (
    TokenRefreshRequest,
    UserCreate,
    UserResponse,
    TokenResponse,
)
from backend.db.session import get_db
from backend.models.user import User
from backend.utils.auth import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    decode_access_token,
    verify_token_type,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.utils.validators import validate_email_format, validate_password_strength

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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
    # Validate email format
    if not validate_email_format(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name or user_data.email.split("@")[0],
        subscription_tier="free",
        subscription_status="active",
        credits_remaining=100  # Default free credits
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login user and return JWT tokens.

    Authenticates user with email and password, returns access and refresh tokens.

    Args:
        form_data: OAuth2 form data with username (email) and password
        db: Database session

    Returns:
        TokenResponse with access_token, refresh_token, and metadata

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by email (username field in OAuth2 form)
    user = db.query(User).filter(User.email == form_data.username).first()

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
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/logout")
async def logout(request: Request, token: str = Depends(oauth2_scheme)):
    """
    Logout user (invalidate token).

    Note: Currently a placeholder. In production, you would:
    1. Add token to Redis blacklist
    2. Set expiration to match token expiration

    Args:
        token: JWT access token

    Returns:
        Success message

    Note: Token blacklisting with Redis can be added for enhanced security.
    """
    # Optional: Implement token blacklisting with Redis
    # redis_client.setex(f"blacklist:{token}", ACCESS_TOKEN_EXPIRE_MINUTES * 60, "1")

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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    try:
        # Decode refresh token
        payload = decode_access_token(refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Generate new tokens
        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
