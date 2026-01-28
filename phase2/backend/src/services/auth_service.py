"""JWT authentication and user extraction service"""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import bcrypt

from ..db import settings

# Security scheme for FastAPI OpenAPI
security = HTTPBearer()

# JWT settings
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours


def hash_password(password: str) -> str:
    """Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        str: Bcrypt hashed password
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash

    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password

    Returns:
        bool: True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(user_id: str) -> str:
    """Create a JWT access token for a user

    Args:
        user_id: User ID to encode in token

    Returns:
        str: JWT access token

    Raises:
        HTTPException: If JWT_SECRET is not configured
    """
    if not settings.JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET not configured",
        )

    expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expires_at,
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token


def decode_jwt_token(token: str) -> dict:
    """Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        dict: Decoded JWT payload with claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    if not settings.JWT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET not configured",
        )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """Extract user_id from JWT token

    This dependency extracts the user_id from the JWT claims
    and makes it available to route handlers.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        str: user_id from JWT claims

    Raises:
        HTTPException: If token is invalid, expired, or missing user_id
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = decode_jwt_token(credentials.credentials)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user_id claim",
        )

    return user_id
