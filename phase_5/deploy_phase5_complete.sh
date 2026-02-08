#!/bin/bash
set -e

echo "=== Phase 5 Complete Deployment ==="

# Build all images
echo "Building images..."
docker build -t phase_4-backend:latest ./backend
docker build -t phase_4-frontend:latest ./frontend
docker build -t notification-service:latest ./services/notification-service
docker build -t recurring-task-service:latest ./services/recurring-task-service
docker build -t audit-log-service:latest ./services/audit-log-service
docker build -t websocket-service:latest ./services/websocket-service

# Apply Dapr components (if they exist)
echo "Applying Dapr components..."
if [ -f dapr/components/pubsub.yaml ]; then
  kubectl apply -f dapr/components/pubsub.yaml
else
  echo "Warning: dapr/components/pubsub.yaml not found, skipping..."
fi

# Deploy infrastructure
echo "Deploying infrastructure..."
kubectl apply -f k8s/database-deployment.yaml
kubectl apply -f k8s/kafka-deployment.yaml

# Wait for infrastructure
echo "Waiting for infrastructure..."
kubectl wait --for=condition=ready pod -l app=postgres -n todo-app --timeout=120s || echo "Postgres not ready"
kubectl wait --for=condition=ready pod -l app=kafka -n todo-app --timeout=120s || echo "Kafka not ready"

# Deploy services
echo "Deploying services..."
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/notification-service-deployment.yaml
kubectl apply -f k8s/recurring-task-service-deployment.yaml
kubectl apply -f k8s/audit-log-service-deployment.yaml
kubectl apply -f k8s/websocket-service-deployment.yaml

# Wait for services
echo "Waiting for services..."
kubectl wait --for=condition=ready pod -l app=todo-backend -n todo-app --timeout=120s || echo "Backend not ready"
kubectl wait --for=condition=ready pod -l app=todo-frontend -n todo-app --timeout=120s || echo "Frontend not ready"
kubectl wait --for=condition=ready pod -l app=notification-service -n todo-app --timeout=120s || echo "Notification service not ready"
kubectl wait --for=condition=ready pod -l app=recurring-task-service -n todo-app --timeout=120s || echo "Recurring task service not ready"
kubectl wait --for=condition=ready pod -l app=audit-log-service -n todo-app --timeout=120s || echo "Audit log service not ready"
kubectl wait --for=condition=ready pod -l app=websocket-service -n todo-app --timeout=120s || echo "WebSocket service not ready"

echo "=== Deployment Complete ==="
echo ""
echo "Services:"
kubectl get svc -n todo-app
echo ""
echo "Pods:"
kubectl get pods -n todo-app
