"""
Migration 003: Add priority column to tasks table

This migration adds a priority column to the tasks table with default value 'medium'
Uses asyncpg directly since it's already installed
"""
from datetime import datetime, timezone
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def upgrade():
    """Add priority column to tasks table"""
    import asyncpg

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", os.getenv("NEON_DATABASE_URL"))
    if not database_url:
        raise ValueError("DATABASE_URL or NEON_DATABASE_URL not found in environment variables")

    # Convert async URL to sync URL for asyncpg
    clean_url = database_url.replace("+asyncpg", "")

    # Connect to database
    conn = await asyncpg.connect(clean_url)
    now = datetime.now(timezone.utc)

    try:
        # Add priority column
        await conn.execute("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS priority VARCHAR(10) NOT NULL DEFAULT 'medium';
        """)

        # Create index on priority
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
        """)

        # Commit
        await conn.execute("COMMIT")

        print(f"[{now}] [SUCCESS] Migration 003: Added priority column to tasks table")
    finally:
        await conn.close()


async def downgrade():
    """Remove priority column from tasks table"""
    import asyncpg

    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL", os.getenv("NEON_DATABASE_URL"))
    if not database_url:
        raise ValueError("DATABASE_URL or NEON_DATABASE_URL not found in environment variables")

    # Convert async URL to sync URL for asyncpg
    clean_url = database_url.replace("+asyncpg", "")

    # Connect to database
    conn = await asyncpg.connect(clean_url)
    now = datetime.now(timezone.utc)

    try:
        # Drop index
        await conn.execute("DROP INDEX IF EXISTS idx_tasks_priority;")

        # Drop column
        await conn.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS priority;")

        # Commit
        await conn.execute("COMMIT")

        print(f"[{now}] [SUCCESS] Migration 003: Removed priority column from tasks table")
    finally:
        await conn.close()


if __name__ == "__main__":
    import sys

    # Run migration or rollback
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())
