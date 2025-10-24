"""
Authentication utilities for JWT token management and password hashing.

TODO: Implementation steps:
1. Implement create_access_token()
2. Implement create_refresh_token()
3. Implement decode_access_token()
4. Implement password hashing with passlib
5. Implement password verification
6. Add token expiration handling
7. Add token blacklist support
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# from backend.config import get_settings

# TODO: Get from settings
SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    TODO:
    - Use passlib to hash password
    - Return hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    TODO:
    - Use passlib to verify password
    - Return True if match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Dictionary with user data (must include 'sub' for user ID)
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token

    TODO:
    1. Copy data to encode
    2. Add expiration time
    3. Encode JWT with secret key
    4. Return token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict) -> str:
    """
    Create JWT refresh token.

    TODO:
    - Similar to access token but with longer expiration
    - Add 'type': 'refresh' to payload
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict:
    """
    Decode and validate JWT token.

    Returns:
        Decoded payload dictionary

    Raises:
        JWTError: If token is invalid or expired

    TODO:
    1. Decode JWT with secret key
    2. Validate expiration
    3. Return payload
    4. Raise error if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    Verify token is of expected type (access or refresh).

    TODO:
    - Decode token
    - Check 'type' field matches expected_type
    - Return True/False
    """
    try:
        payload = decode_access_token(token)
        return payload.get("type") == expected_type
    except JWTError:
        return False
