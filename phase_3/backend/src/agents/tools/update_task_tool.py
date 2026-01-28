"""MCP Tool for updating tasks.
Constitution compliance: Enforces user_id ownership validation through service layer.
All operations go through MCP tools exclusively as required by constitution.
"""
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ...models.task import TaskCreate, TaskUpdate
from ...services.task_service import TaskService


async def update_task(user_id: str, task_id: int, title: str = None, description: str = None, priority: str = None, session: AsyncSession = None) -> Dict[str, Any]:
    """Update a task.

    Args:
        user_id: ID of the user who owns the task
        task_id: ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
        priority: New priority for the task (optional) - values: high, medium, low
        session: Database session (required for proper session management)

    Returns:
        Dictionary containing the updated task details

    Constitution compliance:
    - Validates user_id ownership through service layer
    - Uses MCP tools exclusively for database operations
    - Maintains multi-user data isolation
    """
    task_service = TaskService()

    # First, get all user tasks to validate that the task exists and belongs to the user
    try:
        all_user_tasks = await task_service.get_user_tasks(session, user_id)
        task_exists = any(task.id == task_id for task in all_user_tasks)
        
       
        if not task_exists:
            raise ValueError("Task not found or access denied")
       
   

    except ValueError:
        # If user has no tasks at all
        raise ValueError("Task not found or access denied")
 
    # ya raise, ya log, ya custom handling


    # Create a TaskCreate object with the current values and the updates
    # We'll get the current task details by filtering the user's tasks
    user_tasks = await task_service.get_user_tasks(session, user_id)
    current_task = next((task for task in user_tasks if task.id == task_id), None)

    if not current_task:
        raise ValueError("Task not found or access denied")

    # Prepare the update data - use existing values if not provided
    update_title = title if title is not None else current_task.title
    update_description = description if description is not None else current_task.description
    update_priority = priority if priority is not None else current_task.priority

    # Create a TaskUpdate object with the updated data
    task_update_data = TaskUpdate(
        title=update_title,
        description=update_description,
        priority=update_priority
    )

    # Update the task using the service layer
    updated_task = await task_service.update_task(session, task_id, task_update_data, user_id)

    # Return the updated task
    return {
        "task_id": updated_task.id,
        "status": "updated",
        "title": updated_task.title,
        "description": updated_task.description,
        "is_complete": updated_task.is_complete,
        "priority": updated_task.priority
    }