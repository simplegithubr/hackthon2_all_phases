"""Database connection and session management for Neon PostgreSQL"""
import os
from pathlib import Path
from typing import AsyncGenerator

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
# from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Get the absolute path to the .env file and load it explicitly
# This file is at backend/src/db.py, so .env should be at project root
PROJECT_ROOT = Path(__file__).parent.parent.parent  # Go up from src/ to backend/ to project root
ENV_FILE = PROJECT_ROOT / ".env"

# Load .env explicitly FIRST - this populates os.environ
load_dotenv(ENV_FILE, override=True)

class Settings(BaseSettings):
    """Application settings from environment variables

    Pydantic settings will read from os.environ which was populated by load_dotenv above
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )

    DATABASE_URL: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    JWT_SECRET: str = Field(default_factory=lambda: os.getenv("JWT_SECRET", ""))
    NEON_DATABASE_URL: str = Field(default_factory=lambda: os.getenv("NEON_DATABASE_URL", ""))
    DEBUG: bool = Field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")


settings = Settings()

# Create async SQLAlchemy engine for Neon PostgreSQL with asyncpg
# asyncpg requires SSL to be configured via connect_args, NOT via URL parameters
# Neon requires SSL, so we pass ssl='require' (string) to asyncpg
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={
        "ssl": "require",  # asyncpg accepts 'require' as string for SSL mode
    },
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session

    Yields:
        AsyncSession: Async database session
    """
    async with async_session_maker() as session:
        yield session
