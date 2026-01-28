"""Database migration script for tasks table

Run with: alembic upgrade head
"""
from sqlmodel import SQLModel


def upgrade() -> None:
    """Create tasks table with indexes

    This migration creates the tasks table with user_id foreign key
    and indexes on user_id and created_at for performance.
    """
    from sqlalchemy import text

    # Create tasks table
    text("""
    CREATE TABLE tasks (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        title VARCHAR(200) NOT NULL,
        description TEXT,
        is_complete BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # Create indexes
    text("""
    CREATE INDEX idx_tasks_user_id ON tasks(user_id);
    """)

    text("""
    CREATE INDEX idx_tasks_created_at ON tasks(created_at);
    """)


def downgrade() -> None:
    """Drop tasks table"""
    from sqlalchemy import text

    text("DROP INDEX IF EXISTS idx_tasks_created_at;")
    text("DROP INDEX IF EXISTS idx_tasks_user_id;")
    text("DROP TABLE IF EXISTS tasks;")
