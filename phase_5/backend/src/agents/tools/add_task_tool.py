"""MCP Tool for adding tasks.
Constitution compliance: Enforces user_id ownership validation through service layer.
All operations go through MCP tools exclusively as required by constitution.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.task import TaskCreate
from ...services.task_service import TaskService


async def add_task(user_id: str, title: str, description: str = None, priority: str = "medium", session: AsyncSession = None) -> Dict[str, Any]:
    """Add a new task for a user.

    Args:
        user_id: ID of the authenticated user creating the task
        title: Title of the task (required)
        description: Optional description of the task
        priority: Priority level for the task (optional) - values: high, medium, low (default: medium)
        session: Database session (required for proper session management)

    Returns:
        Dictionary containing the created task details

    Constitution compliance:
    - Validates user_id ownership through service layer
    - Uses MCP tools exclusively for database operations
    - Maintains multi-user data isolation
    """
    task_service = TaskService()

    # Create the task data
    task_data = TaskCreate(
        title=title,
        description=description,
        priority=priority  # Use provided priority or default to "medium"
    )

    # Create the task - service layer enforces user_id validation
    created_task = await task_service.create_task(session, task_data, user_id)

    return {
        "task_id": created_task.id,
        "status": "created",
        "title": created_task.title,
        "description": created_task.description,
        "is_complete": created_task.is_complete,
        "priority": created_task.priority
    }