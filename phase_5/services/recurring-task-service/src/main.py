"""
Recurring Task Service - Creates next task when a recurring task is completed
Phase 5 - Consumer Microservice
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recurring Task Service", version="1.0.0")

# Backend API URL (Phase 4 backend)
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")


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
    return {"status": "healthy", "service": "recurring-task-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint - subscribe to task.completed events
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-completed"
        }
    ]
    logger.info(f"Dapr subscription configured: {subscriptions}")
    return subscriptions


@app.post("/events/task-completed")
async def handle_task_completed(request: Request):
    """
    Handle task.completed events and create next recurring task if needed
    """
    try:
        # Parse the CloudEvent
        body = await request.json()
        logger.info(f"Received event: {body}")

        # Extract event data
        event_data = body.get("data", {})
        event_type = event_data.get("event_type")

        # Only process task.completed events
        if event_type != "task.completed":
            logger.debug(f"Ignoring event type: {event_type}")
            return {"status": "SUCCESS"}

        user_id = event_data.get("user_id")
        task_id = event_data.get("task_id")

        # Check if this task has a recurrence pattern
        # We need to fetch the task details from the backend
        task_details = await fetch_task_details(user_id, task_id)

        if task_details and task_details.get("recurrence_pattern"):
            await create_next_recurring_task(user_id, task_details)
        else:
            logger.info(f"Task {task_id} has no recurrence pattern, skipping")

        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        # Return RETRY to retry processing
        return {"status": "RETRY"}


async def fetch_task_details(user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
    """Fetch task details from backend via Dapr service invocation"""
    try:
        logger.info(f"Fetching task details for task {task_id} via Dapr")

        dapr_url = f"http://localhost:3500/v1.0/invoke/backend/method/api/tasks/{task_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                dapr_url,
                headers={
                    "dapr-app-id": "backend",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch task: {response.status_code}")
                return None

    except Exception as e:
        logger.error(f"Error fetching task details: {str(e)}")
        return None


async def create_next_recurring_task(user_id: str, task_details: Dict[str, Any]):
    """
    Create the next task in the recurrence series
    """
    try:
        recurrence_pattern = task_details.get("recurrence_pattern", {})
        frequency = recurrence_pattern.get("frequency")  # daily, weekly, monthly
        interval = recurrence_pattern.get("interval", 1)

        # Calculate next due date
        original_due_date = task_details.get("due_date")
        if not original_due_date:
            logger.warning("No due date found, cannot create recurring task")
            return

        # Parse due date and calculate next occurrence
        next_due_date = calculate_next_due_date(original_due_date, frequency, interval)

        # Prepare new task data
        new_task_data = {
            "title": task_details.get("title"),
            "description": task_details.get("description"),
            "due_date": next_due_date.isoformat(),
            "priority": task_details.get("priority"),
            "tags": task_details.get("tags"),
            "recurrence_pattern": recurrence_pattern,
            "reminder_time": task_details.get("reminder_time")
        }

        logger.info(f"🔄 Creating next recurring task for user {user_id}: {new_task_data['title']}")

        # Create task via Dapr service invocation
        success = await create_task_via_dapr(user_id, new_task_data)

        if success:
            logger.info(f"✅ Next recurring task created successfully")
        else:
            logger.error(f"Failed to create recurring task")

    except Exception as e:
        logger.error(f"Error creating recurring task: {str(e)}", exc_info=True)


async def create_task_via_dapr(user_id: str, task_data: Dict[str, Any]) -> bool:
    """Create next recurring task via Dapr service invocation"""
    try:
        logger.info(f"Creating next recurring task for user {user_id} via Dapr")

        dapr_url = f"http://localhost:3500/v1.0/invoke/backend/method/api/tasks"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                dapr_url,
                json=task_data,
                headers={
                    "dapr-app-id": "backend",
                    "Content-Type": "application/json"
                },
                timeout=10.0
            )

            if response.status_code in [200, 201]:
                logger.info(f"✓ Created next recurring task")
                return True
            else:
                logger.error(f"Failed to create task: {response.status_code}")
                return False

    except Exception as e:
        logger.error(f"Error creating recurring task: {str(e)}")
        return False


def calculate_next_due_date(current_due_date: str, frequency: str, interval: int) -> datetime:
    """
    Calculate the next due date based on recurrence pattern
    """
    # Parse the current due date
    if isinstance(current_due_date, str):
        current_date = datetime.fromisoformat(current_due_date.replace('Z', '+00:00'))
    else:
        current_date = current_due_date

    # Calculate next date based on frequency
    if frequency == "daily":
        next_date = current_date + timedelta(days=interval)
    elif frequency == "weekly":
        next_date = current_date + timedelta(weeks=interval)
    elif frequency == "monthly":
        # Approximate: add 30 days per month
        next_date = current_date + timedelta(days=30 * interval)
    elif frequency == "yearly":
        next_date = current_date + timedelta(days=365 * interval)
    else:
        # Default to daily
        next_date = current_date + timedelta(days=interval)

    return next_date


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
