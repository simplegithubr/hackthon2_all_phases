#!/bin/bash

# Phase 5 Integration Test - Event Flow Verification
# This script tests the complete event-driven architecture

set -e

echo "=========================================="
echo "Phase 5 Integration Test"
echo "Event Flow Verification"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test configuration
TEST_USER_ID="test-user-123"
TEST_TASK_ID="test-task-456"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Test Configuration:"
echo "  User ID: $TEST_USER_ID"
echo "  Task ID: $TEST_TASK_ID"
echo "  Timestamp: $TIMESTAMP"
echo ""

# Function to check if service is ready
check_service() {
    local service=$1
    local port=$2
    echo -n "Checking $service... "

    kubectl port-forward svc/$service $port:$port > /dev/null 2>&1 &
    PF_PID=$!
    sleep 2

    if curl -s http://localhost:$port/health > /dev/null; then
        echo -e "${GREEN}✓ Ready${NC}"
        kill $PF_PID 2>/dev/null || true
        return 0
    else
        echo -e "${RED}✗ Not Ready${NC}"
        kill $PF_PID 2>/dev/null || true
        return 1
    fi
}

# Step 1: Verify all services are healthy
echo "=========================================="
echo "Step 1: Service Health Checks"
echo "=========================================="
echo ""

check_service "notification-service" 8001
check_service "recurring-task-service" 8002
check_service "audit-log-service" 8003
check_service "websocket-service" 8004

echo ""

# Step 2: Check Kafka is ready
echo "=========================================="
echo "Step 2: Kafka Broker Verification"
echo "=========================================="
echo ""

KAFKA_POD=$(kubectl get pod -l app=kafka -o jsonpath='{.items[0].metadata.name}')
echo "Kafka Pod: $KAFKA_POD"

echo -n "Checking Kafka topics... "
if kubectl exec -it $KAFKA_POD -- rpk topic list 2>/dev/null | grep -q "task-events"; then
    echo -e "${GREEN}✓ task-events topic exists${NC}"
else
    echo -e "${YELLOW}⚠ Creating task-events topic${NC}"
    kubectl exec -it $KAFKA_POD -- rpk topic create task-events --partitions 1 --replicas 1
fi

echo ""

# Step 3: Publish test event to Kafka
echo "=========================================="
echo "Step 3: Publishing Test Event"
echo "=========================================="
echo ""

TEST_EVENT=$(cat <<EOF
{
  "event_type": "task.created",
  "task_id": "$TEST_TASK_ID",
  "user_id": "$TEST_USER_ID",
  "timestamp": "$TIMESTAMP",
  "payload": {
    "title": "Integration Test Task",
    "description": "This is a test task for Phase 5 integration testing",
    "status": "pending",
    "priority": "high"
  }
}
EOF
)

echo "Test Event:"
echo "$TEST_EVENT" | jq '.'
echo ""

echo -n "Publishing event to Kafka... "
echo "$TEST_EVENT" | kubectl exec -i $KAFKA_POD -- rpk topic produce task-events

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Event published successfully${NC}"
else
    echo -e "${RED}✗ Failed to publish event${NC}"
    exit 1
fi

echo ""

# Step 4: Wait for event processing
echo "=========================================="
echo "Step 4: Event Processing"
echo "=========================================="
echo ""

echo "Waiting 5 seconds for services to process event..."
sleep 5
echo ""

# Step 5: Verify event consumption
echo "=========================================="
echo "Step 5: Verifying Event Consumption"
echo "=========================================="
echo ""

echo "Checking service logs for event processing..."
echo ""

echo "--- Notification Service Logs ---"
kubectl logs -l app=notification-service -c notification-service --tail=10 | grep -i "task.created\|$TEST_TASK_ID" || echo "No matching logs found"
echo ""

echo "--- Audit Log Service Logs ---"
kubectl logs -l app=audit-log-service -c audit-log-service --tail=10 | grep -i "task.created\|$TEST_TASK_ID" || echo "No matching logs found"
echo ""

echo "--- WebSocket Service Logs ---"
kubectl logs -l app=websocket-service -c websocket-service --tail=10 | grep -i "task.created\|$TEST_TASK_ID" || echo "No matching logs found"
echo ""

# Step 6: Check Kafka consumer groups
echo "=========================================="
echo "Step 6: Consumer Group Status"
echo "=========================================="
echo ""

echo "Kafka Consumer Groups:"
kubectl exec -it $KAFKA_POD -- rpk group list 2>/dev/null || echo "Unable to list consumer groups"
echo ""

# Step 7: Verify audit log database entry
echo "=========================================="
echo "Step 7: Database Verification"
echo "=========================================="
echo ""

POSTGRES_POD=$(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}')
echo "PostgreSQL Pod: $POSTGRES_POD"
echo ""

echo "Checking audit_logs table for test event..."
kubectl exec -it $POSTGRES_POD -- psql -U postgres -d tododb -c "SELECT event_type, task_id, user_id, created_at FROM audit_logs WHERE task_id = '$TEST_TASK_ID' ORDER BY created_at DESC LIMIT 5;" 2>/dev/null || echo "Unable to query database (table may not exist yet)"

echo ""

# Step 8: Summary
echo "=========================================="
echo "Integration Test Summary"
echo "=========================================="
echo ""

echo -e "${GREEN}✓ All services are healthy${NC}"
echo -e "${GREEN}✓ Kafka broker is operational${NC}"
echo -e "${GREEN}✓ Test event published successfully${NC}"
echo -e "${YELLOW}⚠ Manual verification required for:${NC}"
echo "  - Check service logs above for event processing"
echo "  - Verify database entry was created"
echo "  - Confirm WebSocket broadcast (if clients connected)"
echo ""

echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Review service logs above for event processing"
echo "2. Connect a WebSocket client to test real-time updates"
echo "3. Verify notification was sent (check notification service logs)"
echo "4. Query audit_logs table to confirm persistence"
echo ""

echo "To manually verify:"
echo "  kubectl logs -l app=notification-service -c notification-service --tail=50"
echo "  kubectl logs -l app=audit-log-service -c audit-log-service --tail=50"
echo "  kubectl logs -l app=websocket-service -c websocket-service --tail=50"
echo ""

echo "Test completed at: $(date)"
