# Todo Chatbot Kubernetes Deployment

This directory contains Kubernetes manifests and Helm charts for deploying the Todo AI Chatbot application on Minikube.

## Architecture Overview

The application consists of three main components:
1. **Backend**: FastAPI application handling business logic and API requests
2. **Frontend**: Next.js application serving the user interface
3. **Database**: PostgreSQL database storing application data

## Deployment Options

### Option 1: Using Helm (Recommended)

The Helm chart provides a complete, configurable deployment:

```bash
# Install the Helm chart
helm install todo-chatbot ./helm/todo-chatbot

# Or upgrade an existing installation
helm upgrade todo-chatbot ./helm/todo-chatbot

# Uninstall
helm uninstall todo-chatbot
```

### Option 2: Using Raw Kubernetes Manifests

Apply individual Kubernetes resources:

```bash
kubectl apply -f k8s/database-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

## Service Configuration

- **Database**: ClusterIP service (internal access only)
- **Backend**: ClusterIP service (internal access only)
- **Frontend**: NodePort service (external access)

## Accessing the Application

After deployment, you can access the frontend using the NodePort:

```bash
# Get the NodePort for the frontend service
kubectl get svc todo-chatbot-frontend

# Access the application
minikube service todo-chatbot-frontend --url
```

## Environment Variables

The deployments are configured with appropriate environment variables for:
- Database connection
- API endpoints
- Security keys
- Application settings

## Scaling

- Backend: 1 replica (configured in values.yaml)
- Frontend: 2 replicas (configured in values.yaml)
- Database: 1 replica (configured in values.yaml)

## Image Configuration

All deployments use `imagePullPolicy: IfNotPresent` to work with locally built images.

## Prerequisites

- Minikube cluster running
- Docker images built locally (`todo-backend:latest`, `todo-frontend:latest`)
- Helm (for Helm deployment option)