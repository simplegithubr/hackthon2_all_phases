#!/bin/bash
# Deploy Phase 5 services to Kubernetes

echo "Deploying Phase 5 Consumer Services to Kubernetes..."

# Apply Dapr pub/sub component
echo "Applying Dapr pub/sub component..."
kubectl apply -f dapr/components/pubsub.yaml

# Deploy Notification Service
echo "Deploying notification-service..."
kubectl apply -f k8s/notification-service-deployment.yaml

# Deploy Recurring Task Service
echo "Deploying recurring-task-service..."
kubectl apply -f k8s/recurring-task-service-deployment.yaml

# Deploy Audit Log Service
echo "Deploying audit-log-service..."
kubectl apply -f k8s/audit-log-service-deployment.yaml

# Deploy WebSocket Service
echo "Deploying websocket-service..."
kubectl apply -f k8s/websocket-service-deployment.yaml

echo ""
echo "✅ Phase 5 services deployed successfully!"
echo ""
echo "Check deployment status:"
echo "  kubectl get pods -l app=notification-service"
echo "  kubectl get pods -l app=recurring-task-service"
echo "  kubectl get pods -l app=audit-log-service"
echo "  kubectl get pods -l app=websocket-service"
echo ""
echo "View logs:"
echo "  kubectl logs -l app=notification-service -c notification-service -f"
echo "  kubectl logs -l app=recurring-task-service -c recurring-task-service -f"
echo "  kubectl logs -l app=audit-log-service -c audit-log-service -f"
echo "  kubectl logs -l app=websocket-service -c websocket-service -f"
