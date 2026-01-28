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

# DEBUG: Print the path being used to load .env
print(f"DEBUG: Attempting to load .env from: {ENV_FILE.absolute()}")

# Check if the .env file exists
if ENV_FILE.exists():
    print(f"DEBUG: .env file found at: {ENV_FILE.absolute()}")
else:
    print(f"DEBUG: .env file NOT FOUND at: {ENV_FILE.absolute()}")
    print(f"DEBUG: Current working directory: {Path.cwd().absolute()}")
    # Look for .env in other possible locations
    possible_locations = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",  # backend/.env
        Path(__file__).parent.parent.parent / ".env",  # project root
    ]
    for loc in possible_locations:
        if loc.exists():
            print(f"DEBUG: Found .env at alternative location: {loc.absolute()}")
            ENV_FILE = loc
            break

# Load .env explicitly FIRST - this populates os.environ
load_dotenv(ENV_FILE, override=True)

# DEBUG: Print the value of OPENROUTER_API_KEY being read
openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
print(f"DEBUG: OPENROUTER_API_KEY read from environment: {'SET' if openrouter_key else 'NOT SET'}")
# if openrouter_key and openrouter_key != "<<ENTER_YOUR_OPENROUTER_API_KEY_HERE>>":
#     print(f"DEBUG: OPENROUTER_API_KEY length: {len(openrouter_key)}")
# else:
#     print(f"DEBUG: OPENROUTER_API_KEY is placeholder or empty")
if openrouter_key and len(openrouter_key.strip()) > 20:
    print(f"DEBUG: OPENROUTER_API_KEY loaded correctly, length: {len(openrouter_key)}")
else:
    print("DEBUG: OPENROUTER_API_KEY missing or invalid")




from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    DATABASE_URL: str
    JWT_SECRET: str
    NEON_DATABASE_URL: str
    OPENROUTER_API_KEY: str
    DEBUG: bool = False
    USE_AI_SERVICES: bool = True

settings = Settings()

# DEBUG check
print(f"DEBUG: OPENROUTER_API_KEY = {settings.OPENROUTER_API_KEY!r}")  # should not be placeholder

if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != "<<ENTER_YOUR_OPENROUTER_API_KEY_HERE>>":
    print(f"DEBUG: Settings OPENROUTER_API_KEY length: {len(settings.OPENROUTER_API_KEY)}")
else:
    print(f"DEBUG: Settings OPENROUTER_API_KEY is placeholder or empty")
api_key = settings.OPENROUTER_API_KEY.strip() if settings.OPENROUTER_API_KEY else ""

if api_key and api_key != "<<ENTER_YOUR_OPENROUTER_API_KEY_HERE>>":
    print(f"DEBUG: OPENROUTER_API_KEY loaded correctly, length: {len(api_key)}")
else:
    print(f"DEBUG: OPENROUTER_API_KEY is placeholder or empty")
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





