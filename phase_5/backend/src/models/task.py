"""Task SQLModel definitions"""
from datetime import datetime
from typing import Literal, Optional
import json

from sqlmodel import Field, SQLModel


# Priority levels for tasks
PriorityLevel = Literal["high", "medium", "low", "urgent"]


class TaskBase(SQLModel):
    """Base Task model with shared fields"""

    title: str = Field(index=True, max_length=200, description="Task title (required)")
    description: Optional[str] = Field(default=None, description="Task description (optional)")
    priority: str = Field(default="medium", max_length=20, description="Task priority (high/medium/low/urgent)")
    due_date: Optional[datetime] = Field(default=None, description="Date/time the task is due")
    tags: Optional[str] = Field(default=None, description="JSON array of tag strings for categorization")  # Stored as JSON string
    recurrence_pattern: Optional[str] = Field(default=None, description="JSON object defining recurrence rules")  # Stored as JSON string
    reminder_time: Optional[str] = Field(default=None, description="ISO 8601 duration format before due_date")
    next_occurrence: Optional[datetime] = Field(default=None, description="For recurring tasks - when next instance occurs")


class TaskCreate(TaskBase):
    """Request model for creating a task"""

    pass  # Inherits title (required) and description (optional)


class TaskUpdate(SQLModel):
    """Request model for updating a task"""

    title: Optional[str] = Field(default=None, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    priority: Optional[str] = Field(default=None, max_length=20, description="Task priority (high/medium/low/urgent)")
    due_date: Optional[datetime] = Field(default=None, description="Date/time the task is due")
    tags: Optional[str] = Field(default=None, description="JSON array of tag strings for categorization")  # Stored as JSON string
    recurrence_pattern: Optional[str] = Field(default=None, description="JSON object defining recurrence rules")  # Stored as JSON string
    reminder_time: Optional[str] = Field(default=None, description="ISO 8601 duration format before due_date")
    next_occurrence: Optional[datetime] = Field(default=None, description="For recurring tasks - when next instance occurs")
    is_complete: Optional[bool] = Field(default=None, description="Task completion status")


class Task(TaskBase, table=True):
    """Database table model for Task"""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, description="ID of user who owns this task")
    is_complete: bool = Field(default=False, description="Task completion status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when task was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when task was last updated")

    __tablename__ = "tasks"


class TaskRead(TaskBase):
    """Response model for reading a task"""

    id: int
    user_id: str
    is_complete: bool
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    tags: Optional[str]  # JSON string
    recurrence_pattern: Optional[str]  # JSON string
    reminder_time: Optional[str]
    next_occurrence: Optional[datetime]
