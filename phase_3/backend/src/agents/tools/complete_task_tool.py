"""MCP Tool for completing tasks.
Constitution compliance: Enforces user_id ownership validation through service layer.
All operations go through MCP tools exclusively as required by constitution.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...services.task_service import TaskService


async def complete_task(user_id: str, task_id: int, session: AsyncSession = None) -> Dict[str, Any]:
    """Mark a task as completed.

    Args:
        user_id: ID of the user who owns the task
        task_id: ID of the task to complete
        session: Database session (required for proper session management)

    Returns:
        Dictionary containing the updated task details

    Constitution compliance:
    - Validates user_id ownership through service layer
    - Uses MCP tools exclusively for database operations
    - Maintains multi-user data isolation
    """
    task_service = TaskService()

    # Toggle the task completion status - service layer validates ownership
    updated_task = await task_service.toggle_task_complete(session, task_id, user_id)

    return {
        "task_id": updated_task.id,
        "status": "completed" if updated_task.is_complete else "reactivated",
        "title": updated_task.title,
        "is_complete": updated_task.is_complete
    }