"""Dapr-based Kafka publisher service for task lifecycle events"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel

from ..events.schemas import (
    TaskCreatedEvent,
    TaskUpdatedEvent,
    TaskCompletedEvent,
    ReminderTriggeredEvent,
    RecurringTaskGeneratedEvent
)

logger = logging.getLogger(__name__)


class KafkaPublisherService:
    """Service to interact with Dapr pub/sub API for Kafka event publishing"""

    def __init__(self, dapr_http_endpoint: Optional[str] = None, pubsub_name: str = "kafka-pubsub"):
        """
        Initialize Kafka publisher service

        Args:
            dapr_http_endpoint: Dapr HTTP endpoint (defaults to http://localhost:3500)
            pubsub_name: Name of the Dapr pub/sub component for Kafka
        """
        self.dapr_http_endpoint = dapr_http_endpoint or "http://localhost:3500"
        self.pubsub_name = pubsub_name
        self.client = httpx.AsyncClient(timeout=30.0)  # 30 second timeout
        self.topic_name = "task-events"
        self.task_updates_topic = "task-updates"

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _publish_to_topic(self, topic: str, event: BaseModel, event_type: str) -> bool:
        """
        Publish an event to a specific Kafka topic via Dapr pub/sub

        Args:
            topic: Kafka topic name
            event: Event object to publish
            event_type: Type of event (for logging purposes)

        Returns:
            bool: True if successfully published, False otherwise
        """
        try:
            # Prepare the event data
            event_data = event.model_dump()
            event_json = json.dumps(event_data, default=str)  # Handle datetime serialization

            # Create the Dapr publish request
            publish_url = f"{self.dapr_http_endpoint}/v1.0/publish/{self.pubsub_name}/{topic}"

            headers = {
                "Content-Type": "application/json",
                "dapr-event-type": event_type,
                "dapr-event-time": datetime.utcnow().isoformat() + "Z"
            }

            logger.info(f"Publishing {event_type} event to Kafka topic: {topic}")

            # Make the request to Dapr
            response = await self.client.post(
                publish_url,
                content=event_json,
                headers=headers
            )

            if response.status_code in [200, 204]:
                logger.info(f"✓ Published {event_type} to {topic}")
                return True
            else:
                logger.error(f"Failed to publish {event_type} event to {topic}. Status: {response.status_code}, Body: {response.text}")
                return False

        except httpx.TimeoutException:
            logger.error(f"Timeout publishing {event_type} event to {topic}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Request error publishing {event_type} event to {topic}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing {event_type} event to {topic}: {str(e)}")
            return False

    async def _publish_to_both_topics(self, event: BaseModel, event_type: str) -> bool:
        """
        Publish an event to both task-events and task-updates topics

        Args:
            event: Event object to publish
            event_type: Type of event (for logging purposes)

        Returns:
            bool: True if successfully published to both topics, False otherwise
        """
        # Publish to both topics
        result1 = await self._publish_to_topic(self.topic_name, event, event_type)
        result2 = await self._publish_to_topic(self.task_updates_topic, event, event_type)

        return result1 and result2

    async def publish_task_created(self, user_id: str, task_data: Dict[str, Any]) -> bool:
        """Publish task created event"""
        event = TaskCreatedEvent(
            event_type="task.created",
            user_id=user_id,
            timestamp=datetime.utcnow(),
            task_id=task_data.get('id', ''),
            title=task_data.get('title', ''),
            description=task_data.get('description'),
            due_date=task_data.get('due_date'),
            priority=task_data.get('priority'),
            tags=task_data.get('tags'),
            recurrence_pattern=task_data.get('recurrence_pattern'),
            reminder_time=task_data.get('reminder_time')
        )
        return await self._publish_to_both_topics(event, "task.created")

    async def publish_task_updated(self, user_id: str, task_id: int, updated_fields: Dict[str, Any]) -> bool:
        """Publish task updated event"""
        event = TaskUpdatedEvent(
            event_type="task.updated",
            user_id=user_id,
            timestamp=datetime.utcnow(),
            task_id=str(task_id),
            updated_fields=updated_fields
        )
        return await self._publish_to_both_topics(event, "task.updated")

    async def publish_task_completed(self, user_id: str, task_id: int) -> bool:
        """Publish task completed event"""
        event = TaskCompletedEvent(
            event_type="task.completed",
            user_id=user_id,
            timestamp=datetime.utcnow(),
            task_id=str(task_id),
            completion_time=datetime.utcnow()
        )
        return await self._publish_to_both_topics(event, "task.completed")

    async def publish_task_deleted(self, user_id: str, task_id: int) -> bool:
        """Publish task deleted event"""
        from ..events.schemas import EventType

        event_data = {
            "event_type": "task.deleted",
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "task_id": str(task_id)
        }
        event = type('TaskDeletedEvent', (BaseModel,), {})(**event_data)
        event.__class__.__annotations__ = {'event_type': str, 'user_id': str, 'timestamp': datetime, 'task_id': str}
        return await self._publish_to_both_topics(event, "task.deleted")


# Global instance for use in other services
kafka_publisher = KafkaPublisherService()