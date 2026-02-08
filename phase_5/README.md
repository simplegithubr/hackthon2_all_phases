# Phase 5: Kafka Event-Driven Architecture

**Status**: ✅ Deployed and Operational
**Last Updated**: 2026-02-08
**Version**: 1.0.0

---

## 📖 Overview

Phase 5 implements a complete event-driven microservices architecture using Kafka (Redpanda) for asynchronous task event processing. This phase extends the Todo application with real-time notifications, audit logging, recurring tasks, and WebSocket-based live updates.

### Key Features

- **Event Streaming**: Kafka-based event bus for decoupled service communication
- **Real-Time Notifications**: Email/SMS notifications for task events
- **Audit Logging**: Complete audit trail of all task operations
- **Recurring Tasks**: Scheduled task execution and management
- **Live Updates**: WebSocket-based real-time updates to connected clients
- **Service Mesh**: Dapr integration for service discovery and pub/sub

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Kafka Event Bus (Redpanda)                     │
│                     Topic: task-events                           │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Notification   │ │  Audit Log  │ │  WebSocket  │
    │    Service      │ │   Service   │ │   Service   │
    │    (8001)       │ │   (8003)    │ │   (8004)    │
    └─────────────────┘ └─────────────┘ └─────────────┘
              │               │               │
              ▼               ▼               ▼
       Send Emails/SMS   PostgreSQL DB   Broadcast to
                                          Connected Clients

    ┌─────────────────┐
    │   Recurring     │
    │  Task Service   │ ──► Publishes scheduled task events
    │    (8002)       │
    └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Minikube or Kubernetes cluster
- kubectl CLI
- Docker
- Dapr CLI (optional, for local development)

### Deployment

1. **Start Minikube** (if using local cluster):
```bash
minikube start
```

2. **Deploy all services**:
```bash
# Deploy infrastructure (Kafka, PostgreSQL)
kubectl apply -f k8s/kafka-deployment.yaml
kubectl apply -f k8s/postgres-deployment.yaml

# Deploy microservices
kubectl apply -f k8s/notification-service-deployment.yaml
kubectl apply -f k8s/recurring-task-service-deployment.yaml
kubectl apply -f k8s/audit-log-service-deployment.yaml
kubectl apply -f k8s/websocket-service-deployment.yaml
```

3. **Verify deployment**:
```bash
kubectl get pods
kubectl get svc
```

### Access Services

**Port Forwarding** (for local access):
```bash
kubectl port-forward svc/notification-service 8001:8001
kubectl port-forward svc/recurring-task-service 8002:8002
kubectl port-forward svc/audit-log-service 8003:8003
kubectl port-forward svc/websocket-service 8004:8004
```

**Health Checks**:
```bash
curl http://localhost:8001/health  # Notification Service
curl http://localhost:8002/health  # Recurring Task Service
curl http://localhost:8003/health  # Audit Log Service
curl http://localhost:8004/health  # WebSocket Service
```

---

## 📦 Services

### Notification Service (Port 8001)
Sends email and SMS notifications for task events.

### Recurring Task Service (Port 8002)
Manages scheduled and recurring tasks.

### Audit Log Service (Port 8003)
Maintains complete audit trail of all task operations.

### WebSocket Service (Port 8004)
Provides real-time updates to connected clients.

---

## 📡 Event Schema

All events follow this structure:

```json
{
  "event_type": "task.created",
  "task_id": "task-123",
  "user_id": "user-456",
  "timestamp": "2026-02-08T12:00:00Z",
  "payload": {
    // Event-specific data
  }
}
```

**Event Types**: task.created, task.updated, task.completed, task.deleted, task.recurring.triggered

---

## 🧪 Testing

```bash
# Run integration test
bash test-event-flow.sh

# Test WebSocket client
node test-websocket-client.js
```

---

## 📚 Documentation

- **[DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md)** - Complete deployment overview
- **[VERIFICATION_REPORT.md](./VERIFICATION_REPORT.md)** - Verification and test results
- **[INTEGRATION_TEST_GUIDE.md](./INTEGRATION_TEST_GUIDE.md)** - Testing guide

---

## 🎉 Summary

Phase 5 successfully implements a production-ready event-driven architecture with:

- ✅ 4 microservices deployed and operational
- ✅ Kafka event streaming infrastructure
- ✅ Dapr service mesh integration
- ✅ Real-time WebSocket capabilities
- ✅ Complete audit logging
- ✅ Notification system
- ✅ Recurring task management

**Status**: Ready for integration testing

---

**Last Updated**: 2026-02-08