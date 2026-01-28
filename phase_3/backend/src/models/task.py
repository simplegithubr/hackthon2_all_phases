"""Task SQLModel definitions"""
from datetime import datetime
from typing import Literal, Optional

from sqlmodel import Field, SQLModel


# Priority levels for tasks
PriorityLevel = Literal["high", "medium", "low"]


class TaskBase(SQLModel):
    """Base Task model with shared fields"""

    title: str = Field(index=True, max_length=200, description="Task title (required)")
    description: Optional[str] = Field(default=None, description="Task description (optional)")
    priority: str = Field(default="medium", max_length=10, description="Task priority (high/medium/low)")


class TaskCreate(TaskBase):
    """Request model for creating a task"""

    pass  # Inherits title (required) and description (optional)


class TaskUpdate(SQLModel):
    """Request model for updating a task"""

    title: Optional[str] = Field(default=None, max_length=200, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    priority: Optional[str] = Field(default=None, max_length=10, description="Task priority")


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
