"""User SQLModel definitions"""
from typing import Optional

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base User model with shared fields"""

    username: str = Field(unique=True, index=True, max_length=50, description="Username (unique)")


class UserCreate(SQLModel):
    """Request model for user signup"""

    username: str = Field(max_length=50, description="Username")
    password: str = Field(min_length=6, description="Password (minimum 6 characters)")


class UserLogin(SQLModel):
    """Request model for user login"""

    username: str
    password: str


class User(UserBase, table=True):
    """Database table model for User"""

    id: Optional[str] = Field(default=None, primary_key=True, description="User ID (UUID)")
    hashed_password: str = Field(description="Bcrypt hashed password")

    __tablename__ = "users"


class UserRead(UserBase):
    """Response model for reading a user (without password)"""

    id: str


class TokenResponse(SQLModel):
    """Response model for login endpoint"""

    access_token: str
    token_type: str = "bearer"
