#!/bin/bash

# Minikube setup and deployment script for Todo Chatbot

set -e  # Exit on any error

echo "🚀 Starting Minikube setup for Todo Chatbot deployment..."

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube is not installed. Please install Minikube first."
    echo "Installation instructions: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install Helm first."
    exit 1
fi

# Start Minikube cluster with adequate resources
echo "🔧 Starting Minikube cluster..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Verify cluster is running
echo "🔍 Verifying cluster status..."
kubectl cluster-info

# Enable ingress addon for external access (optional)
echo "🔌 Enabling ingress addon..."
minikube addons enable ingress

# Build Docker images inside Minikube's Docker environment
echo "🐳 Building Docker images in Minikube environment..."
eval $(minikube docker-env)

# Build frontend image
echo "🔨 Building frontend Docker image..."
docker build -t frontend:latest ../frontend

# Build backend image
echo "🔨 Building backend Docker image..."
docker build -t backend:latest ../backend

# Verify images were built
echo "✅ Docker images built successfully:"
docker images | grep -E "(frontend|backend)"

# Install backend Helm chart first (it's a dependency for frontend)
echo "🚢 Installing backend Helm chart..."
helm install backend ../charts/backend --set image.tag=latest

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend --timeout=120s

# Install frontend Helm chart
echo "🚢 Installing frontend Helm chart..."
helm install frontend ../charts/frontend --set image.tag=latest

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=frontend --timeout=120s

# Get the frontend service NodePort
FRONTEND_PORT=$(kubectl get service frontend -o jsonpath='{.spec.ports[0].nodePort}')
echo "🌐 Frontend is available at: $(minikube ip):${FRONTEND_PORT}"

# Get the backend service ClusterIP
BACKEND_IP=$(kubectl get service backend -o jsonpath='{.spec.clusterIP}')
BACKEND_PORT=$(kubectl get service backend -o jsonpath='{.spec.ports[0].port}')
echo "🔗 Backend is available at: ${BACKEND_IP}:${BACKEND_PORT}"

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 To access the application:"
echo "   Frontend: $(minikube ip):${FRONTEND_PORT}"
echo "   Backend API: $(minikube ip):$(kubectl get service backend -o jsonpath='{.spec.ports[0].nodePort}') (if service is exposed)"
echo ""
echo "🔄 To view logs:"
echo "   Frontend: kubectl logs -l app.kubernetes.io/name=frontend"
echo "   Backend: kubectl logs -l app.kubernetes.io/name=backend"
echo ""
echo "🧹 To cleanup: minikube delete"