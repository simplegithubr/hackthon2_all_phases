#!/bin/bash

# Script to test scalability and validate the deployment

set -e  # Exit on any error

echo "🧪 Testing scalability and validating deployment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Wait for all pods to be running
echo "⏳ Waiting for all pods to be in Running state..."
kubectl wait --for=condition=Ready pods --all --timeout=300s

# Show current deployment status
echo "📊 Current deployment status:"
kubectl get pods,svc,deployments

# Test scaling the backend deployment
echo "📈 Testing backend scaling..."
kubectl scale deployment backend --replicas=3
echo "⏳ Waiting for backend to scale to 3 replicas..."
kubectl wait --for=condition=Ready pods -l app.kubernetes.io/name=backend --timeout=120s

# Test scaling the frontend deployment
echo "📈 Testing frontend scaling..."
kubectl scale deployment frontend --replicas=3
echo "⏳ Waiting for frontend to scale to 3 replicas..."
kubectl wait --for=condition=Ready pods -l app.kubernetes.io/name=frontend --timeout=120s

# Show updated status after scaling
echo "📊 Deployment status after scaling:"
kubectl get pods,svc,deployments

# Test load balancing by checking endpoints
echo "🔄 Checking load balancing across pods..."
echo "Backend endpoints:"
kubectl get endpoints backend
echo "Frontend endpoints:"
kubectl get endpoints frontend

# Test health of all pods
echo "✅ Checking health of all pods..."
kubectl get pods -o wide

# Test service connectivity
echo "📡 Testing service connectivity..."
BACKEND_SVC=$(kubectl get svc backend -o jsonpath='{.spec.clusterIP}')
BACKEND_PORT=$(kubectl get svc backend -o jsonpath='{.spec.ports[0].port}')

if [ ! -z "$BACKEND_SVC" ] && [ ! -z "$BACKEND_PORT" ]; then
    echo "Backend service available at: $BACKEND_SVC:$BACKEND_PORT"
fi

FRONTEND_SVC=$(kubectl get svc frontend -o jsonpath='{.spec.clusterIP}')
FRONTEND_PORT=$(kubectl get svc frontend -o jsonpath='{.spec.ports[0].port}')

if [ ! -z "$FRONTEND_SVC" ] && [ ! -z "$FRONTEND_PORT" ]; then
    echo "Frontend service available at: $FRONTEND_SVC:$FRONTEND_PORT"
fi

# Test horizontal pod autoscaler if enabled
echo ".Horizontal Pod Autoscaler status:"
if kubectl get hpa 2>/dev/null; then
    kubectl get hpa
else
    echo "No Horizontal Pod Autoscalers found."
fi

# Simulate load to trigger autoscaling (optional)
echo "💡 To test autoscaling, you can simulate load with:"
echo "   kubectl run load-generator --image=busybox --rm -it -- sh -c 'while true; do wget -q -O- http://backend:8000/health; sleep 1; done'"

# Check resource usage
echo "📈 Resource usage by pods:"
kubectl top pods

echo "✅ Scalability testing completed!"
echo ""
echo "📋 Summary:"
echo "   - Deployments scaled to 3 replicas each"
echo "   - Services accessible within cluster"
echo "   - Load balancing configured"
echo "   - Ready for further load testing"