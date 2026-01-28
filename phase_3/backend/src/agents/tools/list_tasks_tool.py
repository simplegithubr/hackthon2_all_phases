"""MCP Tool for listing tasks.
Constitution compliance: Enforces user_id ownership validation through service layer.
All operations go through MCP tools exclusively as required by constitution.
"""
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.task import TaskRead
from ...services.task_service import TaskService


async def list_tasks(user_id: str, status: str = "all", session: AsyncSession = None) -> Dict[str, Any]:
    """List tasks for a user with optional filtering.

    Args:
        user_id: ID of the user whose tasks to list
        status: Filter by status ('all', 'pending', 'completed')
        session: Database session (required for proper session management)

    Returns:
        Dictionary containing the list of tasks

    Constitution compliance:
    - Validates user_id ownership through service layer
    - Uses MCP tools exclusively for database operations
    - Maintains multi-user data isolation
    """
    task_service = TaskService()

    try:
        # Get all tasks for the user - service layer enforces user_id validation
        tasks = await task_service.get_user_tasks(session, user_id)

        # Filter based on status if specified
        filtered_tasks = tasks
        if status == "pending":
            filtered_tasks = [task for task in tasks if not task.is_complete]
        elif status == "completed":
            filtered_tasks = [task for task in tasks if task.is_complete]

        # Format the tasks for the response
        task_list = []
        for task in filtered_tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete,
                "priority": task.priority,
                "created_at": task.created_at.isoformat() if task.created_at else None
            })

        return {
            "tasks": task_list,
            "total_count": len(task_list),
            "filter_status": status
        }
    except ValueError as e:
        # Handle case where user has no tasks
        if "No tasks found for user" in str(e):
            return {
                "tasks": [],
                "total_count": 0,
                "filter_status": status
            }
        else:
            raise e