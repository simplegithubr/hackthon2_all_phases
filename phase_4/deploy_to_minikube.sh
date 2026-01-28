#!/bin/bash

# Script to deploy Todo AI Chatbot to Minikube
# This script assumes:
# 1. Minikube is running
# 2. Docker images are already built (todo-backend:latest and todo-frontend:latest)

set -e  # Exit on any error

echo "Starting deployment to Minikube..."

# Set Docker environment to use Minikube's Docker daemon
eval $(minikube docker-env)

echo "Building Docker images in Minikube context..."
# Rebuild images in Minikube's context so they're available to the cluster
cd ../backend
docker build -t todo-backend:latest .

cd ../frontend
docker build -t todo-frontend:latest .

echo "Deploying to Minikube..."

# Apply the Kubernetes manifests
kubectl apply -f ../k8s/backend-deployment.yaml
kubectl apply -f ../k8s/frontend-deployment.yaml

echo "Waiting for deployments to be ready..."
kubectl rollout status deployment/todo-backend-deployment
kubectl rollout status deployment/todo-frontend-deployment

echo "Deployment complete!"
echo "Backend service: $(minikube service todo-backend-service --url)"
echo "Frontend service: $(minikube service todo-frontend-service --url)"

echo "To access the frontend in your browser, run: minikube service todo-frontend-service --url"