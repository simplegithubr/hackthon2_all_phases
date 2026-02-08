"""
Notification Service - Consumes task events and sends notifications
Phase 5 - Consumer Microservice
"""
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, Request
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service", version="1.0.0")


class CloudEvent(BaseModel):
    """Dapr CloudEvent format"""
    id: str
    source: str
    type: str
    specversion: str
    datacontenttype: str
    data: Dict[str, Any]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint - tells Dapr which topics to subscribe to
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task"
        }
    ]
    logger.info(f"Dapr subscription configured: {subscriptions}")
    return subscriptions


@app.post("/events/task")
async def handle_task_event(request: Request):
    """
    Handle incoming task events from Kafka via Dapr
    """
    try:
        # Parse the CloudEvent
        body = await request.json()
        logger.info(f"Received event: {body}")

        # Extract event data
        event_data = body.get("data", {})
        event_type = event_data.get("event_type")
        user_id = event_data.get("user_id")
        task_id = event_data.get("task_id")

        # Process based on event type
        if event_type == "task.created":
            await send_task_created_notification(user_id, task_id, event_data)
        elif event_type == "task.updated":
            await send_task_updated_notification(user_id, task_id, event_data)
        elif event_type == "task.completed":
            await send_task_completed_notification(user_id, task_id, event_data)
        elif event_type == "reminder.triggered":
            await send_reminder_notification(user_id, task_id, event_data)
        else:
            logger.info(f"Ignoring event type: {event_type}")

        # Return success to Dapr
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        # Return DROP to avoid retries for malformed events
        return {"status": "DROP"}


async def send_task_created_notification(user_id: str, task_id: str, event_data: Dict[str, Any]):
    """Send notification when a task is created"""
    title = event_data.get("title", "Untitled")
    logger.info(f"📧 NOTIFICATION: User {user_id} - New task created: '{title}' (ID: {task_id})")
    # TODO: Integrate with email/SMS/push notification service
    # For now, just log it


async def send_task_updated_notification(user_id: str, task_id: str, event_data: Dict[str, Any]):
    """Send notification when a task is updated"""
    updated_fields = event_data.get("updated_fields", {})
    logger.info(f"📧 NOTIFICATION: User {user_id} - Task {task_id} updated: {updated_fields}")
    # TODO: Integrate with notification service


async def send_task_completed_notification(user_id: str, task_id: str, event_data: Dict[str, Any]):
    """Send notification when a task is completed"""
    completion_time = event_data.get("completion_time")
    logger.info(f"🎉 NOTIFICATION: User {user_id} - Task {task_id} completed at {completion_time}")
    # TODO: Integrate with notification service


async def send_reminder_notification(user_id: str, task_id: str, event_data: Dict[str, Any]):
    """Send reminder notification"""
    task_title = event_data.get("task_title", "Task")
    due_date = event_data.get("due_date")
    logger.info(f"⏰ REMINDER: User {user_id} - '{task_title}' is due at {due_date}")
    # TODO: Integrate with notification service


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
