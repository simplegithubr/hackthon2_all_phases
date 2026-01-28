"""Task service layer for business logic and orchestration

This service layer coordinates between API routes and the repository layer,
providing business logic and input validation.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate
from ..repositories.task_repository import TaskRepository


class TaskService:
    """Service for Task business operations"""

    def __init__(self) -> None:
        """Initialize task service with repository"""
        self.repository = TaskRepository()

    async def get_user_tasks(self, session: AsyncSession, user_id: str) -> List[TaskRead]:
        """Get all tasks for a user

        Args:
            session: Database session
            user_id: ID of user to fetch tasks for

        Returns:
            List[TaskRead]: List of tasks belonging to the user

        Raises:
            ValueError: If user has no tasks
        """
        tasks = await self.repository.get_by_user(session, user_id)

        if not tasks:
            raise ValueError("No tasks found for user")

        return [TaskRead.model_validate(task) for task in tasks]

    async def create_task(
        self, session: AsyncSession, task_data: TaskCreate, user_id: str
    ) -> TaskRead:
        """Create a new task for a user

        Args:
            session: Database session
            task_data: Task data from request
            user_id: ID of user creating the task

        Returns:
            TaskRead: Created task

        Raises:
            ValueError: If title is empty or too long
        """
        # Validate title
        if not task_data.title or task_data.title.strip() == "":
            raise ValueError("Task title is required")

        if len(task_data.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")

        # Create task with user_id
        task = Task(**task_data.model_dump(), user_id=user_id)
        created_task = await self.repository.create(session, task)

        return TaskRead.model_validate(created_task)

    async def update_task(
        self, session: AsyncSession, task_id: int, task_data: TaskUpdate, user_id: str
    ) -> TaskRead:
        """Update an existing task

        Args:
            session: Database session
            task_id: ID of task to update
            task_data: Updated task data
            user_id: ID of user attempting update

        Returns:
            TaskRead: Updated task

        Raises:
            ValueError: If title is empty or too long
            ValueError: If task not found or access denied
        """
        # Validate title if provided
        if task_data.title is not None:
            if not task_data.title or task_data.title.strip() == "":
                raise ValueError("Task title is required")

            if len(task_data.title) > 200:
                raise ValueError("Task title cannot exceed 200 characters")

        # Update task (repository validates ownership)
        updated_task = await self.repository.update(
            session,
            task_id,
            title=task_data.title,
            description=task_data.description,
            priority=task_data.priority,
            user_id=user_id
        )

        return TaskRead.model_validate(updated_task)

    async def delete_task(self, session: AsyncSession, task_id: int, user_id: str) -> None:
        """Delete a task

        Args:
            session: Database session
            task_id: ID of task to delete
            user_id: ID of user attempting deletion

        Returns:
            None

        Raises:
            ValueError: If task not found or access denied
        """
        await self.repository.delete(session, task_id, user_id)
        return None

    async def toggle_task_complete(
        self, session: AsyncSession, task_id: int, user_id: str
    ) -> TaskRead:
        """Toggle task completion status

        Args:
            session: Database session
            task_id: ID of task to toggle
            user_id: ID of user attempting toggle

        Returns:
            TaskRead: Updated task with toggled completion status

        Raises:
            ValueError: If task not found or access denied
        """
        updated_task = await self.repository.toggle_complete(session, task_id, user_id)

        return TaskRead.model_validate(updated_task)
