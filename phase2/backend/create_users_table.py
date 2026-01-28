"""Simple script to create users table"""
import asyncio
import sys
from pathlib import Path

# Add backend/src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text
from db import engine


async def create_users_table():
    """Create users table if it doesn't exist"""
    async with engine.begin() as conn:
        # Drop existing table if any
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))

        # Create users table
        await conn.execute(
            text(
                """
                CREATE TABLE users (
                    id VARCHAR(36) PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL
                );
                """
            )
        )

        # Create index on username
        await conn.execute(
            text("CREATE INDEX idx_users_username ON users(username);")
        )

        print("Users table created successfully!")


if __name__ == "__main__":
    asyncio.run(create_users_table())
