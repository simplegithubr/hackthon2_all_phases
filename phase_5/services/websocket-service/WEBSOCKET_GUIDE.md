# WebSocket Service Guide

## Overview

The WebSocket service bridges Kafka events to WebSocket connections, enabling real-time updates in the frontend.

## Architecture

```
Backend → Kafka (task-updates topic) → WebSocket Service → Frontend
```

**Flow:**
1. Backend publishes event to `task-updates` topic
2. Dapr delivers event to WebSocket service
3. WebSocket service broadcasts to connected clients
4. Frontend receives real-time update

## Features

- ✅ Real-time task updates via WebSocket
- ✅ User-specific event routing
- ✅ Multiple connections per user supported
- ✅ Automatic connection cleanup
- ✅ Health check and statistics endpoints
- ✅ Dapr pub/sub integration

## Endpoints

### WebSocket Connection
```
ws://localhost:8004/ws?user_id=<user_id>&token=<jwt_token>
```

**Query Parameters:**
- `user_id` (required) - User identifier
- `token` (optional) - JWT token for authentication

### HTTP Endpoints

**Health Check:**
```bash
GET /health
```

**Statistics:**
```bash
GET /stats
```

Returns:
```json
{
  "total_users": 2,
  "total_connections": 3,
  "users": {
    "user-123": 2,
    "user-456": 1
  }
}
```

## Message Format

### Server → Client

**Connection Established:**
```json
{
  "type": "connected",
  "message": "WebSocket connected successfully",
  "user_id": "user-123",
  "timestamp": "2026-02-07T12:00:00.000Z"
}
```

**Task Update:**
```json
{
  "type": "task_update",
  "event": {
    "event_type": "task.created",
    "user_id": "user-123",
    "task_id": "456",
    "title": "New Task",
    "timestamp": "2026-02-07T12:00:00.000Z"
  },
  "timestamp": "2026-02-07T12:00:00.000Z"
}
```

### Client → Server

**Ping (Keep-Alive):**
```json
{
  "type": "ping"
}
```

**Response:**
```json
{
  "type": "pong"
}
```

## Deployment

### Build Image

```bash
cd services/websocket-service
docker build -t websocket-service:latest .
```

### Deploy to Minikube

```bash
# Load image into Minikube
minikube image load websocket-service:latest

# Deploy
kubectl apply -f charts/phase5/websocket-service.yaml

# Verify
kubectl get pods -l app=websocket-service
```

### Update Dapr Component

Add `websocket-service` to pub/sub scopes in `dapr-components/pubsub-kafka.yaml`:

```yaml
scopes:
- backend
- notification-service
- recurring-task-service
- audit-log-service
- websocket-service  # ADD THIS
```

## Testing

### 1. Test WebSocket Connection

```bash
# Port forward
kubectl port-forward svc/websocket-service 8004:8004

# Connect with wscat (install: npm install -g wscat)
wscat -c "ws://localhost:8004/ws?user_id=test-user"

# You should see:
# Connected
# < {"type":"connected","message":"WebSocket connected successfully",...}
```

### 2. Test Event Flow

**Terminal 1 - WebSocket Client:**
```bash
wscat -c "ws://localhost:8004/ws?user_id=test-user"
```

**Terminal 2 - Create Task:**
```bash
# Create a task via backend API
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task"}'
```

**Terminal 1 should receive:**
```json
{
  "type": "task_update",
  "event": {
    "event_type": "task.created",
    "user_id": "test-user",
    "task_id": "123",
    "title": "Test Task"
  }
}
```

### 3. Check Statistics

```bash
curl http://localhost:8004/stats
```

## Frontend Integration

See `FRONTEND_INTEGRATION.md` for complete frontend WebSocket client implementation.

## Troubleshooting

### WebSocket connection fails

**Check service is running:**
```bash
kubectl get pods -l app=websocket-service
kubectl logs -l app=websocket-service -c websocket-service
```

**Check Dapr sidecar:**
```bash
kubectl logs -l app=websocket-service -c daprd
```

### Not receiving events

**Check Dapr subscription:**
```bash
curl http://localhost:8004/dapr/subscribe
```

**Check Kafka topic:**
```bash
# Verify backend is publishing to task-updates topic
kubectl logs -l app=backend -c backend | grep "task-updates"
```

**Check WebSocket service logs:**
```bash
kubectl logs -l app=websocket-service -c websocket-service -f
```

### Multiple connections per user

This is supported! Each browser tab/window can have its own connection. All connections for the same user will receive the same events.

## Production Considerations

### Authentication

Currently, the service accepts any connection with a `user_id`. In production:

1. Verify JWT token on connection
2. Extract user_id from token
3. Reject invalid tokens

```python
def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return user_id"""
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")  # user_id
    except:
        return None
```

### Scaling

For multiple replicas:
- Use Redis pub/sub to broadcast events across instances
- Or use sticky sessions to route users to same instance

### Monitoring

Add metrics:
- Active connections count
- Messages sent/received
- Connection duration
- Error rates

## Summary

The WebSocket service:
- ✅ Bridges Kafka → WebSocket for real-time updates
- ✅ Routes events to specific users
- ✅ Supports multiple connections per user
- ✅ Integrates with Dapr pub/sub
- ✅ Provides health check and statistics
- ✅ Ready for production with auth improvements
