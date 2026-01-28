"""Authentication API endpoints for signup and login"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...models.user import User, UserCreate, UserLogin, UserRead, TokenResponse
from ...services.auth_service import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    """Register a new user

    Args:
        user_data: Username and password
        session: Database session

    Returns:
        UserRead: Created user (without password)

    Raises:
        HTTPException: 400 if username already exists
        HTTPException: 400 if username/password validation fails
    """
    # Validate username
    if not user_data.username or len(user_data.username.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is required",
        )

    if len(user_data.username) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot exceed 50 characters",
        )

    # Validate password
    if not user_data.password or len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )

    # Check if username already exists
    result = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Create new user with hashed password
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)

    user = User(
        id=user_id,
        username=user_data.username,
        hashed_password=hashed_password,
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return UserRead(id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Authenticate user and return JWT token

    Args:
        credentials: Username and password
        session: Database session

    Returns:
        TokenResponse: JWT access token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find user by username
    result = await session.execute(
        select(User).where(User.username == credentials.username)
    )
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Create JWT token
    access_token = create_access_token(user.id)

    return TokenResponse(access_token=access_token, token_type="bearer")
