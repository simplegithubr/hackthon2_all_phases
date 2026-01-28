#!/bin/bash

# Complete deployment script for Todo Chatbot on Minikube

set -e  # Exit on any error

echo "🚀 Starting full deployment of Todo Chatbot on Minikube..."

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check prerequisites
MISSING_TOOLS=()
for tool in minikube kubectl helm docker; do
    if ! command_exists "$tool"; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo "❌ Missing required tools: ${MISSING_TOOLS[*]}"
    echo "Please install the missing tools before continuing."
    exit 1
fi

echo "✅ All required tools are available."

# Check if Gordon is available
if command_exists gordon; then
    echo "🤖 Gordon is available for Docker optimization."
    GORDON_AVAILABLE=true
else
    echo "⚠️  Gordon not available. Using standard Dockerfiles."
    GORDON_AVAILABLE=false
fi

# Check if kubectl-ai is available
if command_exists kubectl-ai; then
    echo "🤖 kubectl-ai is available for Helm chart generation."
    KUBECTL_AI_AVAILABLE=true
else
    echo "⚠️  kubectl-ai not available. Using standard Helm charts."
    KUBECTL_AI_AVAILABLE=false
fi

# Check if kagent is available
if command_exists kagent; then
    echo "🤖 kagent is available for optimization."
    KAGENT_AVAILABLE=true
else
    echo "⚠️  kagent not available. Skipping AI optimization."
    KAGENT_AVAILABLE=false
fi

# Start Minikube with recommended resources
echo "🔧 Starting Minikube cluster with 4 CPUs and 8GB memory..."
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable ingress addon
echo "🔌 Enabling ingress addon..."
minikube addons enable ingress

# Set Docker environment to Minikube
echo "🐳 Setting Docker environment to Minikube..."
eval $(minikube docker-env)

# Build Docker images
echo "🔨 Building Docker images..."

# Build frontend image
echo "   Building frontend image..."
docker build -t frontend:latest ../frontend

# Build backend image
echo "   Building backend image..."
docker build -t backend:latest ../backend

echo "✅ Docker images built successfully."

# Install Helm charts
echo "🚢 Installing Helm charts..."

# Create namespace if it doesn't exist
kubectl create namespace todo-chatbot --dry-run=client -o yaml | kubectl apply -f -

# Install backend first (dependency for frontend)
echo "   Installing backend chart..."
helm upgrade --install backend ../charts/backend --set image.tag=latest,image.repository=backend --namespace todo-chatbot --create-namespace

# Wait for backend to be ready
echo "   Waiting for backend to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=backend -n todo-chatbot --timeout=120s

# Install frontend
echo "   Installing frontend chart..."
helm upgrade --install frontend ../charts/frontend --set image.tag=latest,image.repository=frontend,env.NEXT_PUBLIC_API_URL=http://backend:8000 --namespace todo-chatbot

# Wait for frontend to be ready
echo "   Waiting for frontend to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=frontend -n todo-chatbot --timeout=120s

# Show deployment status
echo "📊 Deployment status:"
kubectl get pods,services,deployments -n todo-chatbot

# Get service information
FRONTEND_NODEPORT=$(kubectl get service frontend -n todo-chatbot -o jsonpath='{.spec.ports[0].nodePort}')
FRONTEND_HOST=$(minikube ip)

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "🌐 Application is accessible at:"
echo "   Frontend: http://${FRONTEND_HOST}:${FRONTEND_NODEPORT}"
echo ""
echo "📋 Other useful commands:"
echo "   # View logs"
echo "   kubectl logs -l app.kubernetes.io/name=frontend -n todo-chatbot"
echo "   kubectl logs -l app.kubernetes.io/name=backend -n todo-chatbot"
echo ""
echo "   # Scale deployments"
echo "   kubectl scale deployment frontend -n todo-chatbot --replicas=3"
echo "   kubectl scale deployment backend -n todo-chatbot --replicas=3"
echo ""
echo "   # Port forward for development"
echo "   kubectl port-forward service/frontend -n todo-chatbot 3000:3000"
echo "   kubectl port-forward service/backend -n todo-chatbot 8000:8000"
echo ""
echo "   # Delete deployment"
echo "   helm uninstall frontend -n todo-chatbot"
echo "   helm uninstall backend -n todo-chatbot"
echo "   kubectl delete namespace todo-chatbot"
echo ""
echo "🧹 To stop Minikube: minikube stop"
echo "💥 To delete Minikube cluster: minikube delete"