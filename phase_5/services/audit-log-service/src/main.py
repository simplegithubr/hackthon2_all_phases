"""
Audit Log Service - Logs all task events for compliance and history
Phase 5 - Consumer Microservice
"""
import logging
import json
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

app = FastAPI(title="Audit Log Service", version="1.0.0")

# In-memory audit log storage (in production, use a database)
audit_logs = []


class CloudEvent(BaseModel):
    """Dapr CloudEvent format"""
    id: str
    source: str
    type: str
    specversion: str
    datacontenttype: str
    data: Dict[str, Any]


class AuditLogEntry(BaseModel):
    """Audit log entry model"""
    timestamp: datetime
    event_id: str
    event_type: str
    user_id: str
    task_id: str
    action: str
    details: Dict[str, Any]
    source: str


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "audit-log-service"}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint - subscribe to ALL task events
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/audit"
        }
    ]
    logger.info(f"Dapr subscription configured: {subscriptions}")
    return subscriptions


@app.post("/events/audit")
async def handle_audit_event(request: Request):
    """
    Handle ALL task events and store them in audit log
    """
    try:
        # Parse the CloudEvent
        body = await request.json()
        logger.info(f"Received event for audit: {body}")

        # Extract event data
        event_data = body.get("data", {})
        event_type = event_data.get("event_type")
        user_id = event_data.get("user_id")
        task_id = event_data.get("task_id", "N/A")
        timestamp = event_data.get("timestamp")

        # Create audit log entry
        audit_entry = AuditLogEntry(
            timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if timestamp else datetime.utcnow(),
            event_id=body.get("id", "unknown"),
            event_type=event_type,
            user_id=user_id,
            task_id=task_id,
            action=map_event_to_action(event_type),
            details=event_data,
            source=body.get("source", "unknown")
        )

        # Store audit log (in production, save to database)
        await store_audit_log(audit_entry)

        # Log to console
        logger.info(f"📝 AUDIT LOG: {audit_entry.action} - User: {user_id}, Task: {task_id}, Type: {event_type}")

        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Error processing audit event: {str(e)}", exc_info=True)
        # Return RETRY to ensure audit logs are not lost
        return {"status": "RETRY"}


async def store_audit_log(entry: AuditLogEntry):
    """
    Store audit log entry
    In production, this would write to a database (PostgreSQL, MongoDB, etc.)
    """
    # For now, store in memory
    audit_logs.append(entry.model_dump())

    # Also write to a file for persistence (simple approach)
    try:
        with open("/tmp/audit_logs.jsonl", "a") as f:
            f.write(json.dumps(entry.model_dump(), default=str) + "\n")
    except Exception as e:
        logger.error(f"Error writing audit log to file: {str(e)}")

    logger.debug(f"Audit log stored: {entry.event_id}")


def map_event_to_action(event_type: str) -> str:
    """
    Map event type to human-readable action
    """
    action_map = {
        "task.created": "TASK_CREATED",
        "task.updated": "TASK_UPDATED",
        "task.completed": "TASK_COMPLETED",
        "task.deleted": "TASK_DELETED",
        "reminder.triggered": "REMINDER_SENT",
        "recurring_task.generated": "RECURRING_TASK_CREATED"
    }
    return action_map.get(event_type, "UNKNOWN_ACTION")


@app.get("/audit-logs")
async def get_audit_logs(user_id: str = None, limit: int = 100):
    """
    Retrieve audit logs (for admin/compliance purposes)
    """
    filtered_logs = audit_logs

    # Filter by user_id if provided
    if user_id:
        filtered_logs = [log for log in audit_logs if log.get("user_id") == user_id]

    # Return most recent logs
    return {
        "total": len(filtered_logs),
        "logs": filtered_logs[-limit:]
    }


@app.get("/audit-logs/stats")
async def get_audit_stats():
    """
    Get audit log statistics
    """
    if not audit_logs:
        return {"total_events": 0, "events_by_type": {}}

    # Count events by type
    events_by_type = {}
    for log in audit_logs:
        event_type = log.get("event_type", "unknown")
        events_by_type[event_type] = events_by_type.get(event_type, 0) + 1

    return {
        "total_events": len(audit_logs),
        "events_by_type": events_by_type,
        "unique_users": len(set(log.get("user_id") for log in audit_logs))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
