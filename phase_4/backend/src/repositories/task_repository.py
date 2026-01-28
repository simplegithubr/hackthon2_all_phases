"""Task repository for database access with multi-user isolation

All queries enforce user_id filtering at repository layer
to prevent cross-user data access.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.task import Task


class TaskRepository:
    """Repository for Task database operations with user_id isolation"""

    async def get_by_user(self, session: AsyncSession, user_id: str) -> List[Task]:
        """Get all tasks belonging to a specific user

        IMPORTANT: This method enforces multi-user data isolation
        by filtering ALL results by user_id. This is the single
        source of truth for user data filtering.

        Args:
            session: Database session
            user_id: ID of user to fetch tasks for

        Returns:
            List[Task]: List of tasks belonging to the user,
                      sorted by creation date (newest first)
        """
        result = await session.execute(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, task: Task) -> Task:
        """Create a new task in database

        Note: user_id should already be set on task object
        before calling this method.

        Args:
            session: Database session
            task: Task object to create

        Returns:
            Task: Created task with id populated
        """
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def update(
        self, session: AsyncSession, task_id: int, title: str = None, description: str = None, priority: str = None, user_id: str = None
    ) -> Optional[Task]:
        """Update an existing task

        CRITICAL: Validates task belongs to user by checking user_id
        in WHERE clause. This prevents cross-user updates.

        Args:
            session: Database session
            task_id: ID of task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            user_id: ID of user attempting update

        Returns:
            Optional[Task]: Updated task if found and owned by user, None otherwise

        Raises:
            ValueError: If task not found or belongs to another user
        """
        result = await session.execute(
            select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
        )
        existing_task = result.scalar_one_or_none()

        if not existing_task:
            raise ValueError("Task not found or access denied")

        # Update fields only if provided
        if title is not None:
            existing_task.title = title
        if description is not None:
            existing_task.description = description
        if priority is not None:
            existing_task.priority = priority

        # Update timestamp
        from datetime import datetime
        existing_task.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(existing_task)
        return existing_task

    async def delete(self, session: AsyncSession, task_id: int, user_id: str) -> bool:
        """Delete a task

        CRITICAL: Validates task belongs to user by checking user_id
        in WHERE clause. This prevents cross-user deletions.

        Args:
            session: Database session
            task_id: ID of task to delete
            user_id: ID of user attempting deletion

        Returns:
            bool: True if deleted, False if not found or access denied

        Raises:
            ValueError: If task not found or belongs to another user
        """
        result = await session.execute(
            select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError("Task not found or access denied")

        await session.delete(task)
        await session.commit()
        return True

    async def toggle_complete(
        self, session: AsyncSession, task_id: int, user_id: str
    ) -> Optional[Task]:
        """Toggle task completion status

        CRITICAL: Validates task belongs to user by checking user_id
        in WHERE clause. This prevents cross-user toggles.

        Args:
            session: Database session
            task_id: ID of task to toggle
            user_id: ID of user attempting toggle

        Returns:
            Optional[Task]: Updated task if found and owned by user, None otherwise

        Raises:
            ValueError: If task not found or belongs to another user
        """
        result = await session.execute(
            select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
        )
        task = result.scalar_one_or_none()

        if not task:
            raise ValueError("Task not found or access denied")

        # Toggle completion status
        task.is_complete = not task.is_complete

        await session.commit()
        await session.refresh(task)
        return task
