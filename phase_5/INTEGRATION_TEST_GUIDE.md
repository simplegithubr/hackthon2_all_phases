# Phase 5 Integration Testing Guide

This guide provides step-by-step instructions for testing the complete event-driven architecture.

---

## 🎯 Test Objectives

1. Verify Kafka event publishing works
2. Confirm all services consume events correctly
3. Validate notification delivery
4. Check audit log persistence
5. Test real-time WebSocket broadcasts

---

## 📋 Prerequisites

### Required Tools
- `kubectl` - Kubernetes CLI
- `curl` - HTTP client
- `jq` - JSON processor (optional, for pretty output)
- `node` - Node.js runtime (for WebSocket client)

### Required Services Running
- Minikube cluster
- All Phase 5 services deployed
- Kafka broker operational

### Verify Prerequisites
```bash
# Check cluster
kubectl cluster-info

# Check all pods are running
kubectl get pods

# Verify services
kubectl get svc
```

---

## 🧪 Test Scenarios

### Test 1: Basic Event Flow

**Objective**: Verify that a task event flows through the entire system.

**Steps**:

1. **Start port forwarding for all services** (in separate terminals):
```bash
# Terminal 1
kubectl port-forward svc/notification-service 8001:8001

# Terminal 2
kubectl port-forward svc/audit-log-service 8003:8003

# Terminal 3
kubectl port-forward svc/websocket-service 8004:8004
```

2. **Run the integration test script**:
```bash
cd E:\hackthon2_all_phase\phase_5
bash test-event-flow.sh
```

3. **Review the output** for:
   - ✓ All health checks pass
   - ✓ Event published to Kafka
   - ✓ Services processed the event (check logs)

**Expected Results**:
- Notification service logs show event received
- Audit log service persists event to database
- WebSocket service broadcasts to connected clients

---

### Test 2: Real-Time WebSocket Updates

**Objective**: Verify WebSocket clients receive real-time task updates.

**Steps**:

1. **Install Node.js dependencies** (if not already installed):
```bash
npm install ws
```

2. **Start port forwarding for WebSocket service**:
```bash
kubectl port-forward svc/websocket-service 8004:8004
```

3. **Run the WebSocket test client** (in a separate terminal):
```bash
node test-websocket-client.js
```

4. **Publish a test event** (in another terminal):
```bash
# Get Kafka pod name
KAFKA_POD=$(kubectl get pod -l app=kafka -o jsonpath='{.items[0].metadata.name}')

# Publish test event
echo '{
  "event_type": "task.created",
  "task_id": "ws-test-001",
  "user_id": "test-user-123",
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "payload": {
    "title": "WebSocket Test Task",
    "status": "pending"
  }
}' | kubectl exec -i $KAFKA_POD -- rpk topic produce task-events
```

5. **Verify** the WebSocket client receives the event.

**Expected Results**:
- WebSocket client shows "Connected to WebSocket server"
- Event appears in the client console
- Event includes all expected fields

---

### Test 3: Notification Service

**Objective**: Verify notification service processes events correctly.

**Steps**:

1. **Check notification service logs**:
```bash
kubectl logs -l app=notification-service -c notification-service --tail=50 -f
```

2. **Publish a task.created event**:
```bash
KAFKA_POD=$(kubectl get pod -l app=kafka -o jsonpath='{.items[0].metadata.name}')

echo '{
  "event_type": "task.created",
  "task_id": "notif-test-001",
  "user_id": "test-user-456",
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "payload": {
    "title": "Notification Test Task",
    "description": "Testing notification delivery",
    "status": "pending"
  }
}' | kubectl exec -i $KAFKA_POD -- rpk topic produce task-events
```

3. **Watch the logs** for notification processing.

**Expected Results**:
- Logs show event received from Kafka
- Notification prepared for delivery
- Email/SMS notification logged (actual delivery depends on configuration)

---

### Test 4: Audit Log Persistence

**Objective**: Verify audit log service persists events to PostgreSQL.

**Steps**:

1. **Publish multiple test events**:
```bash
KAFKA_POD=$(kubectl get pod -l app=kafka -o jsonpath='{.items[0].metadata.name}')

# Event 1: task.created
echo '{
  "event_type": "task.created",
  "task_id": "audit-test-001",
  "user_id": "test-user-789",
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "payload": {"title": "Audit Test Task 1"}
}' | kubectl exec -i $KAFKA_POD -- rpk topic produce task-events

# Event 2: task.updated
echo '{
  "event_type": "task.updated",
  "task_id": "audit-test-001",
  "user_id": "test-user-789",
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "payload": {"title": "Audit Test Task 1 - Updated"}
}' | kubectl exec -i $KAFKA_POD -- rpk topic produce task-events

# Event 3: task.completed
echo '{
  "event_type": "task.completed",
  "task_id": "audit-test-001",
  "user_id": "test-user-789",
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "payload": {"completed_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}
}' | kubectl exec -i $KAFKA_POD -- rpk topic produce task-events
```

2. **Wait 5 seconds** for processing.

3. **Query the audit_logs table**:
```bash
POSTGRES_POD=$(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}')

kubectl exec -it $POSTGRES_POD -- psql -U postgres -d tododb -c "
SELECT
  event_type,
  task_id,
  user_id,
  created_at
FROM audit_logs
WHERE task_id = 'audit-test-001'
ORDER BY created_at DESC;
"
```

**Expected Results**:
- All 3 events appear in the database
- Events are in chronological order
- All fields are correctly populated

---

### Test 5: Recurring Task Service

**Objective**: Verify recurring task service generates scheduled events.

**Steps**:

1. **Check recurring task service logs**:
```bash
kubectl logs -l app=recurring-task-service -c recurring-task-service --tail=50 -f
```

2. **Create a test recurring task** (via API or database):
```bash
# This would typically be done through the backend API
# For now, we can verify the service is ready to process recurring tasks
kubectl port-forward svc/recurring-task-service 8002:8002

curl http://localhost:8002/health
```

3. **Monitor logs** for scheduled task execution.

**Expected Results**:
- Service is healthy and running
- Scheduler is active
- Ready to process recurring task definitions

---

## 🔍 Verification Checklist

After running all tests, verify:

- [ ] All services respond to health checks
- [ ] Kafka broker accepts and stores events
- [ ] Notification service receives and processes events
- [ ] Audit log service persists events to database
- [ ] WebSocket service broadcasts to connected clients
- [ ] Recurring task service is operational
- [ ] No error messages in service logs
- [ ] Consumer groups are active in Kafka

---

## 📊 Monitoring During Tests

### View Service Logs
```bash
# All services
kubectl logs -l app=notification-service -c notification-service --tail=50
kubectl logs -l app=audit-log-service -c audit-log-service --tail=50
kubectl logs -l app=websocket-service -c websocket-service --tail=50
kubectl logs -l app=recurring-task-service -c recurring-task-service --tail=50

# Dapr sidecars
kubectl logs -l app=notification-service -c daprd --tail=50
```

### Monitor Kafka
```bash
KAFKA_POD=$(kubectl get pod -l app=kafka -o jsonpath='{.items[0].metadata.name}')

# List topics
kubectl exec -it $KAFKA_POD -- rpk topic list

# View topic details
kubectl exec -it $KAFKA_POD -- rpk topic describe task-events

# Consume messages (see all events)
kubectl exec -it $KAFKA_POD -- rpk topic consume task-events --offset start

# List consumer groups
kubectl exec -it $KAFKA_POD -- rpk group list

# Describe consumer group
kubectl exec -it $KAFKA_POD -- rpk group describe <group-name>
```

### Check Database
```bash
POSTGRES_POD=$(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}')

# Connect to database
kubectl exec -it $POSTGRES_POD -- psql -U postgres -d tododb

# Useful queries:
# SELECT COUNT(*) FROM audit_logs;
# SELECT event_type, COUNT(*) FROM audit_logs GROUP BY event_type;
# SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;
```

---

## 🐛 Troubleshooting

### Issue: Events not being consumed

**Symptoms**: Events published to Kafka but services don't process them.

**Diagnosis**:
```bash
# Check Dapr pub/sub component
kubectl get component kafka-pubsub -o yaml

# Check service subscriptions
kubectl get subscription

# Check Dapr sidecar logs
kubectl logs <pod-name> -c daprd
```

**Solutions**:
- Verify Dapr pub/sub component is configured correctly
- Check service subscriptions are registered
- Ensure Kafka broker is accessible from pods

### Issue: WebSocket connection fails

**Symptoms**: WebSocket client cannot connect.

**Diagnosis**:
```bash
# Check WebSocket service
kubectl get svc websocket-service
kubectl get pod -l app=websocket-service

# Check logs
kubectl logs -l app=websocket-service -c websocket-service
```

**Solutions**:
- Verify port-forward is running: `kubectl port-forward svc/websocket-service 8004:8004`
- Check WebSocket service is listening on correct port
- Ensure no firewall blocking connection

### Issue: Database connection errors

**Symptoms**: Audit log service cannot connect to PostgreSQL.

**Diagnosis**:
```bash
# Check PostgreSQL service
kubectl get svc postgres
kubectl get pod -l app=postgres

# Test connection from audit-log pod
kubectl exec -it <audit-log-pod> -- nc -zv postgres 5432
```

**Solutions**:
- Verify PostgreSQL is running
- Check DATABASE_URL environment variable
- Ensure database and tables are created

---

## 📈 Performance Testing

### Load Test Event Publishing

```bash
# Publish 100 events rapidly
for i in {1..100}; do
  echo "{
    \"event_type\": \"task.created\",
    \"task_id\": \"load-test-$i\",
    \"user_id\": \"test-user-load\",
    \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
    \"payload\": {\"title\": \"Load Test Task $i\"}
  }" | kubectl exec -i $KAFKA_POD -- rpk topic produce task-events
done

# Monitor consumer lag
kubectl exec -it $KAFKA_POD -- rpk group describe <consumer-group>
```

### Monitor Resource Usage

```bash
# Install metrics-server first
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View resource usage
kubectl top pods
kubectl top nodes
```

---

## ✅ Success Criteria

Integration tests are successful when:

1. **Event Publishing**: Events successfully published to Kafka
2. **Event Consumption**: All services receive and process events
3. **Notification Delivery**: Notifications logged/sent correctly
4. **Audit Persistence**: Events stored in PostgreSQL
5. **Real-Time Updates**: WebSocket clients receive broadcasts
6. **No Errors**: No error messages in service logs
7. **Performance**: Events processed within acceptable time (<5 seconds)

---

## 📝 Test Report Template

After completing tests, document results:

```markdown
# Integration Test Results

**Date**: YYYY-MM-DD
**Tester**: [Name]
**Environment**: Minikube Local

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Basic Event Flow | ✅ PASS | All services processed event |
| WebSocket Updates | ✅ PASS | Client received broadcast |
| Notification Service | ✅ PASS | Notification logged |
| Audit Log Persistence | ✅ PASS | 3 events stored in DB |
| Recurring Task Service | ✅ PASS | Service healthy |

## Issues Found

None

## Recommendations

[Any recommendations for improvements]
```

---

## 🔗 Related Documentation

- [DEPLOYMENT_SUMMARY.md](./DEPLOYMENT_SUMMARY.md) - Deployment overview
- [VERIFICATION_REPORT.md](./VERIFICATION_REPORT.md) - Verification results
- Service READMEs in respective directories

---

*Last Updated: 2026-02-08*
