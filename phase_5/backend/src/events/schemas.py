"""Event schemas for task operations in event-driven architecture"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel


class EventType(str, Enum):
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    REMINDER_TRIGGERED = "reminder.triggered"
    RECURRING_TASK_GENERATED = "recurring_task.generated"


class TaskEventBase(BaseModel):
    """Base class for all task events"""
    event_type: EventType
    user_id: str
    timestamp: datetime


class TaskCreatedEvent(TaskEventBase):
    """Event published when a task is created"""
    event_type: EventType = EventType.TASK_CREATED
    task_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    reminder_time: Optional[str] = None


class TaskUpdatedEvent(TaskEventBase):
    """Event published when a task is updated"""
    event_type: EventType = EventType.TASK_UPDATED
    task_id: str
    updated_fields: Dict[str, Any]


class TaskCompletedEvent(TaskEventBase):
    """Event published when a task is completed"""
    event_type: EventType = EventType.TASK_COMPLETED
    task_id: str
    completion_time: datetime


class ReminderTriggeredEvent(TaskEventBase):
    """Event published when a reminder is triggered"""
    event_type: EventType = EventType.REMINDER_TRIGGERED
    task_id: str
    task_title: str
    due_date: Optional[datetime] = None
    reminder_time: Optional[str] = None
    target_channel: str = "push"  # email, push, sms


class RecurringTaskGeneratedEvent(TaskEventBase):
    """Event published when a recurring task is generated"""
    event_type: EventType = EventType.RECURRING_TASK_GENERATED
    original_task_id: str
    new_task_id: str
    parent_recurrence_id: str
    occurrence_number: int
    scheduled_date: datetime