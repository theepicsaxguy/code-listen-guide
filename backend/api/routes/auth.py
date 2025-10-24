"""
Authentication routes for user registration, login, and token management.

TODO: Implementation steps:
1. Implement POST /register endpoint
2. Implement POST /login endpoint with JWT generation
3. Implement POST /logout endpoint
4. Implement GET /me endpoint for current user
5. Implement POST /refresh endpoint for token refresh
6. Add password hashing with passlib
7. Add JWT token creation and validation
8. Implement rate limiting for auth endpoints
9. Add email verification (optional)
10. Integrate with Clerk/Supabase if using external auth
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from backend.api.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from backend.db.session import get_db
from backend.models.user import User
from backend.utils.auth import create_access_token, create_refresh_token, verify_password, get_password_hash

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    TODO:
    1. Check if email already exists
    2. Hash password with passlib
    3. Create new user in database
    4. Return user data (exclude password)
    5. Optionally send verification email
    6. Create Stripe customer
    """
    # TODO: Implement
    pass


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login user and return JWT tokens.

    TODO:
    1. Find user by email
    2. Verify password
    3. Generate access and refresh tokens
    4. Return tokens with expiration
    5. Log login event
    """
    # TODO: Implement
    pass


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """
    Logout user (invalidate token).

    TODO:
    1. Add token to blacklist (Redis)
    2. Return success message
    """
    # TODO: Implement
    pass


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Get current authenticated user.

    TODO:
    1. Verify JWT token
    2. Extract user ID from token
    3. Fetch user from database
    4. Return user data
    """
    # TODO: Implement
    pass


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.

    TODO:
    1. Verify refresh token
    2. Generate new access token
    3. Optionally rotate refresh token
    4. Return new tokens
    """
    # TODO: Implement
    pass
