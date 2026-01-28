"""Pytest fixtures for backend tests"""
import pytest
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from sqlmodel import SQLModel

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session", autouse=True)
def mock_settings():
    """Mock JWT_SECRET for all tests"""
    from src.db import settings

    with patch.object(settings, 'JWT_SECRET', 'test-secret'):
        yield


@pytest.fixture(scope="function")
async def test_session():
    """Create test database session

    Creates an in-memory SQLite database and yields an async session.
    """
    from sqlalchemy import text

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # Create tables
    async with engine.begin() as conn:
        # Create users table first (required by tasks foreign key)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Create all SQLModel tables
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def mock_user_id():
    """Mock user ID for testing"""
    return "test-user-123"


@pytest.fixture
def mock_jwt_token(mock_user_id):
    """Mock valid JWT token"""
    from jose import jwt

    payload = {"sub": mock_user_id}
    return jwt.encode(payload, "test-secret", algorithm="HS256")
