"""Task CRUD API endpoints"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...api.dependencies import get_current_user
from ...models.task import Task, TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskRead])
async def get_tasks(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> List[TaskRead]:
    """Get all tasks belonging to authenticated user

    Args:
        user_id: ID of authenticated user from JWT
        session: Database session

    Returns:
        List[TaskRead]: List of user's tasks

    Raises:
        HTTPException: 404 if user has no tasks
    """
    result = await session.execute(
        select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
    )
    tasks = result.scalars().all()

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tasks found for user",
        )

    return tasks


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Create a new task for authenticated user

    Args:
        task_data: Task data from request body
        user_id: ID of authenticated user from JWT
        session: Database session

    Returns:
        TaskRead: Created task

    Raises:
        HTTPException: 400 if title is empty or too long
    """
    # Validate title
    if not task_data.title or task_data.title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title is required",
        )

    if len(task_data.title) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot exceed 200 characters",
        )

    # Create task
    task = Task(**task_data.model_dump(), user_id=user_id)
    session.add(task)
    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Get a specific task by ID

    Args:
        task_id: Task ID
        user_id: ID of authenticated user from JWT
        session: Database session

    Returns:
        TaskRead: Task details

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if task belongs to another user
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task",
        )

    return TaskRead.model_validate(task)


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Update an existing task

    Args:
        task_id: Task ID
        task_data: Updated task data
        user_id: ID of authenticated user from JWT
        session: Database session

    Returns:
        TaskRead: Updated task

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if task belongs to another user
        HTTPException: 400 if title is empty or too long
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task",
        )

    # Update fields if provided
    if task_data.title is not None:
        if not task_data.title or task_data.title.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title is required",
            )
        if len(task_data.title) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title cannot exceed 200 characters",
            )
        task.title = task_data.title

    if task_data.description is not None:
        task.description = task_data.description

    if task_data.priority is not None:
        task.priority = task_data.priority

    # Update timestamp
    from datetime import datetime
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)


@router.patch("/{task_id}/complete", response_model=TaskRead)
async def toggle_task_complete(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> TaskRead:
    """Toggle task completion status

    Args:
        task_id: Task ID
        user_id: ID of authenticated user from JWT
        session: Database session

    Returns:
        TaskRead: Updated task with toggled completion status

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if task belongs to another user
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task",
        )

    # Toggle completion status
    task.is_complete = not task.is_complete

    # Update timestamp
    from datetime import datetime
    task.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Delete a task

    Args:
        task_id: Task ID
        user_id: ID of authenticated user from JWT
        session: Database session

    Returns:
        None: 204 No Content

    Raises:
        HTTPException: 404 if task not found
        HTTPException: 403 if task belongs to another user
    """
    result = await session.execute(
        select(Task).where((Task.id == task_id) & (Task.user_id == user_id))
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task",
        )

    await session.delete(task)
    await session.commit()

    return None
