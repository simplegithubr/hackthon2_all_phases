"""Task service layer for business logic and orchestration

This service layer coordinates between API routes and the repository layer,
providing business logic and input validation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate
from ..repositories.task_repository import TaskRepository
from .kafka_publisher import kafka_publisher


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

        # Publish event after successful creation
        try:
            task_dict = created_task.__dict__.copy()
            task_dict['id'] = str(task_dict.get('id', ''))
            await kafka_publisher.publish_task_created(user_id, task_dict)
        except Exception as e:
            # Log the error but don't fail the main operation
            print(f"Warning: Failed to publish task.created event: {str(e)}")

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
        # Get original task to compare for event
        original_task = await self.repository.get_by_id_and_user(session, task_id, user_id)

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

        # Publish event after successful update
        try:
            # Compare original and updated to identify changed fields
            original_dict = original_task.__dict__ if original_task else {}
            updated_dict = updated_task.__dict__

            changed_fields = {}
            for field in ['title', 'description', 'priority']:
                if field in updated_dict and original_dict.get(field) != updated_dict[field]:
                    changed_fields[field] = updated_dict[field]

            # Also include completion status if it changed
            if hasattr(updated_task, 'completed') and original_dict.get('completed') != getattr(updated_task, 'completed'):
                changed_fields['completed'] = getattr(updated_task, 'completed')

            await kafka_publisher.publish_task_updated(user_id, task_id, changed_fields)
        except Exception as e:
            # Log the error but don't fail the main operation
            print(f"Warning: Failed to publish task.updated event: {str(e)}")

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

        # Publish event after successful deletion
        try:
            await kafka_publisher.publish_task_deleted(user_id, task_id)
        except Exception as e:
            # Log the error but don't fail the main operation
            print(f"Warning: Failed to publish task.deleted event: {str(e)}")

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

        # Publish event after successful completion toggle
        try:
            if hasattr(updated_task, 'completed') and getattr(updated_task, 'completed'):
                await kafka_publisher.publish_task_completed(user_id, task_id)
        except Exception as e:
            # Log the error but don't fail the main operation
            print(f"Warning: Failed to publish task.completed event: {str(e)}")

        return TaskRead.model_validate(updated_task)
