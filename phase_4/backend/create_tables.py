"""Create database tables using SQLModel

This script creates all tables defined in the models.
Run with: python create_tables.py
"""
import asyncio
from sqlalchemy import text
from sqlmodel import SQLModel

from src.db import engine
from src.models.task import Task  # Import models to register them


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")

    async with engine.begin() as conn:
        # First create users table (referenced by tasks foreign key)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("[OK] Users table created/verified")

        # Then create tasks table using SQLModel
        # We need to drop and recreate the foreign key constraint to avoid issues
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                is_complete BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_tasks_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        print("[OK] Tasks table created/verified")

        # Create indexes for performance
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title)"))
        print("[OK] Indexes created")

    print("\n[SUCCESS] All tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - tasks (with foreign key to users)")
    print("  - indexes: user_id, created_at, title")


async def main():
    await create_tables()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
