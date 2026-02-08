"""Create users table migration

This migration creates the users table with:
- id (UUID primary key)
- username (unique, indexed)
- hashed_password
"""
import asyncio
import sys
from pathlib import Path

# Add backend/src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import text
from db import engine


async def run_migration():
    """Create users table"""
    async with engine.begin() as conn:
        # Create users table
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL
                );
                """
            )
        )

        # Create index on username for faster lookups
        await conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                """
            )
        )

    print("✅ Users table created successfully")


if __name__ == "__main__":
    asyncio.run(run_migration())
