#!/bin/bash

# Deployment script for Todo AI Chatbot
# This script handles deployment to either Minikube or Docker Desktop Kubernetes

set -e  # Exit on any error

echo "Checking for available Kubernetes clusters..."

# Check if minikube is running
if minikube status >/dev/null 2>&1; then
    echo "Minikube is running, proceeding with minikube deployment..."

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

elif kubectl cluster-info >/dev/null 2>&1; then
    echo "Kubernetes cluster detected, proceeding with direct kubectl deployment..."

    # For direct kubectl deployment, we need to make sure images are available
    # If using Docker Desktop Kubernetes, images built locally should be available
    # But we might need to tag and push to a registry, or use kind to load images

    echo "Loading images to Kubernetes cluster..."

    # Check if kind is available for loading images
    if command -v kind &> /dev/null; then
        # If using kind, load images
        kind load docker-image todo-backend:latest
        kind load docker-image todo-frontend:latest
    else
        echo "Kind not found, assuming Docker Desktop Kubernetes can access local images"
    fi

    echo "Deploying to Kubernetes cluster..."

    # Apply the Kubernetes manifests
    kubectl apply -f ../k8s/backend-deployment.yaml
    kubectl apply -f ../k8s/frontend-deployment.yaml

    echo "Waiting for deployments to be ready..."
    kubectl rollout status deployment/todo-backend-deployment --timeout=300s
    kubectl rollout status deployment/todo-frontend-deployment --timeout=300s

    echo "Deployment complete!"
    echo "Services:"
    kubectl get svc

else
    echo "No Kubernetes cluster found. Please start Minikube with: minikube start --driver=docker --memory=2048 --cpus=2"
    echo "Or ensure Docker Desktop Kubernetes is enabled."
    exit 1
fi