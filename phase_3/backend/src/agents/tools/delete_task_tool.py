"""MCP Tool for deleting tasks.
Constitution compliance: Enforces user_id ownership validation through service layer.
All operations go through MCP tools exclusively as required by constitution.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from ...services.task_service import TaskService


async def delete_task(user_id: str, task_id: int, session: AsyncSession = None) -> Dict[str, Any]:
    """Delete a task.

    Args:
        user_id: ID of the user who owns the task
        task_id: ID of the task to delete
        session: Database session (required for proper session management)

    Returns:
        Dictionary confirming the deletion

    Constitution compliance:
    - Validates user_id ownership through service layer
    - Uses MCP tools exclusively for database operations
    - Maintains multi-user data isolation
    """
    task_service = TaskService()

    # Delete the task - service layer validates ownership
    await task_service.delete_task(session, task_id, user_id)

    return {
        "task_id": task_id,
        "status": "deleted",
        "message": f"Task {task_id} has been deleted"
    }