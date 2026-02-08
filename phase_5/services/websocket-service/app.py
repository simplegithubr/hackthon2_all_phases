"""
WebSocket Service - Real-time Task Updates
Bridges Kafka events to WebSocket connections for live frontend updates
"""
import asyncio
import logging
import json
from datetime import datetime
from typing import Set, Dict
from flask import Flask, request
from flask_sock import Sock
from cloudevents.http import from_http
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
sock = Sock(app)

# Store active WebSocket connections by user_id
active_connections: Dict[str, Set] = {}

# Dapr configuration
DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"
TOPIC_NAME = "task-updates"


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "websocket-service", "connections": len(active_connections)}, 200


@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    """Dapr subscription endpoint - subscribe to task-updates topic"""
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/task-updates"
        }
    ]
    logger.info(f"Dapr subscription configured: {subscriptions}")
    return subscriptions, 200


@app.route('/task-updates', methods=['POST'])
def handle_task_update():
    """
    Handle task update events from Kafka and broadcast to WebSocket clients
    """
    try:
        # Parse CloudEvent
        event = from_http(request.headers, request.get_data())
        event_data = json.loads(event.data)

        event_type = event_data.get("event_type")
        user_id = event_data.get("user_id")

        logger.info(f"📡 Received {event_type} for user {user_id}")

        # Broadcast to all WebSocket connections for this user
        if user_id in active_connections:
            broadcast_to_user(user_id, event_data)
        else:
            logger.debug(f"No active connections for user {user_id}")

        return {"status": "SUCCESS"}, 200

    except Exception as e:
        logger.error(f"Error processing task update: {str(e)}", exc_info=True)
        return {"status": "DROP"}, 200


@sock.route('/ws')
def websocket_handler(ws):
    """
    WebSocket connection handler
    Clients connect with: ws://localhost:8004/ws?user_id=<user_id>&token=<jwt_token>
    """
    try:
        # Get user_id from query params
        user_id = request.args.get('user_id')
        token = request.args.get('token')

        if not user_id:
            logger.warning("WebSocket connection rejected: missing user_id")
            ws.close(reason="Missing user_id")
            return

        # TODO: Verify JWT token
        # For now, we'll accept any connection with a user_id

        # Register connection
        if user_id not in active_connections:
            active_connections[user_id] = set()
        active_connections[user_id].add(ws)

        logger.info(f"✓ WebSocket connected: user {user_id} (total: {len(active_connections[user_id])})")

        # Send welcome message
        ws.send(json.dumps({
            "type": "connected",
            "message": "WebSocket connected successfully",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }))

        # Keep connection alive and handle incoming messages
        while True:
            try:
                message = ws.receive(timeout=30)
                if message:
                    # Handle ping/pong or other client messages
                    data = json.loads(message)
                    if data.get("type") == "ping":
                        ws.send(json.dumps({"type": "pong"}))
            except Exception as e:
                # Connection closed or timeout
                break

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")

    finally:
        # Cleanup connection
        if user_id and user_id in active_connections:
            active_connections[user_id].discard(ws)
            if not active_connections[user_id]:
                del active_connections[user_id]
            logger.info(f"✗ WebSocket disconnected: user {user_id}")


def broadcast_to_user(user_id: str, event_data: dict):
    """
    Broadcast event to all WebSocket connections for a specific user
    """
    if user_id not in active_connections:
        return

    message = json.dumps({
        "type": "task_update",
        "event": event_data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    # Send to all connections for this user
    disconnected = set()
    for ws in active_connections[user_id]:
        try:
            ws.send(message)
            logger.debug(f"📤 Sent update to user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to send to connection: {str(e)}")
            disconnected.add(ws)

    # Remove disconnected connections
    for ws in disconnected:
        active_connections[user_id].discard(ws)


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get WebSocket connection statistics"""
    stats = {
        "total_users": len(active_connections),
        "total_connections": sum(len(conns) for conns in active_connections.values()),
        "users": {user_id: len(conns) for user_id, conns in active_connections.items()}
    }
    return stats, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
