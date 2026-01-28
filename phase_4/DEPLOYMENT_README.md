# Todo AI Chatbot - Docker + Kubernetes Deployment Guide

## Overview
This guide provides instructions for deploying the Todo AI Chatbot (FastAPI backend + Next.js frontend) using Docker containers and Kubernetes.

## Prerequisites
- Docker Desktop with Kubernetes enabled OR Minikube
- kubectl
- Helm (optional)
- Node.js and npm (for initial setup)

## Docker Setup

### Backend Dockerfile (`backend/Dockerfile`)
```Dockerfile
# Multi-stage build for Python FastAPI application
# Builder stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser appuser

# Set the working directory
WORKDIR /app

# Copy the application code
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application with uvicorn (removed --reload for production)
CMD ["sh", "-c", "python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"]
```

### Frontend Dockerfile (`frontend/Dockerfile`)
```Dockerfile
# Multi-stage build for Next.js application
# Builder stage
FROM node:18-alpine AS builder

# Install curl for health checks
RUN apk add --no-cache --update curl

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY next.config.js ./

# Install dependencies (including devDependencies for build)
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Create standalone output
RUN npm install -g @vercel/ncc && \
    npx @vercel/ncc build server.js -o dist

# Production stage
FROM node:18-alpine AS runner

# Install curl for health checks
RUN apk add --no-cache --update curl

# Create a non-root user
RUN addgroup -g 1001 -S nextjs && \
    adduser -S nextjs -u 1001

# Set working directory
WORKDIR /app

# Copy node modules and app files from builder
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["node", "server.js"]
```

## Building Docker Images

### Build Backend Image
```bash
cd backend
docker build -t todo-backend:latest .
```

### Build Frontend Image
```bash
cd frontend
docker build -t todo-frontend:latest .
```

## Running Containers Locally

### Create Docker Network
```bash
docker network create todo-network
```

### Run PostgreSQL Container
```bash
docker run -d \
  --name todo-postgres \
  --network todo-network \
  -e POSTGRES_DB=todo_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15
```

### Run Backend Container
```bash
docker run -d \
  --name todo-backend \
  --network todo-network \
  -e DATABASE_URL="postgresql+asyncpg://postgres:password@todo-postgres:5432/todo_db" \
  -e JWT_SECRET="mysecretkey" \
  -e OPENROUTER_API_KEY="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" \
  -e DEV_MODE="true" \
  -p 8000:8000 \
  todo-backend:latest
```

### Run Frontend Container
```bash
docker run -d \
  --name todo-frontend \
  --network todo-network \
  -e NEXT_PUBLIC_API_URL="http://todo-backend:8000/api" \
  -p 3000:3000 \
  todo-frontend:latest
```

## Kubernetes Deployment

### Kubernetes Manifests

#### Backend Deployment (`k8s/backend-deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend-deployment
  labels:
    app: todo-backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: todo-backend
        image: todo-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql+asyncpg://postgres:password@todo-postgres-service:5432/todo_db"
        - name: JWT_SECRET
          value: "mysecretkey"
        - name: OPENROUTER_API_KEY
          value: "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"
        - name: DEV_MODE
          value: "true"
---
apiVersion: v1
kind: Service
metadata:
  name: todo-backend-service
spec:
  selector:
    app: todo-backend
  ports:
    - protocol: TCP
      port: 8000
      targetPort: 8000
  type: NodePort
```

#### Frontend Deployment (`k8s/frontend-deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend-deployment
  labels:
    app: todo-frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: todo-frontend
        image: todo-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://todo-backend-service:8000/api"
---
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend-service
spec:
  selector:
    app: todo-frontend
  ports:
    - protocol: TCP
      port: 3000
      targetPort: 3000
  type: NodePort
```

## Minikube Deployment

### Start Minikube
```bash
minikube start --driver=docker --memory=2048 --cpus=2
```

### Deploy using kubectl
```bash
# Set Docker environment to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images in Minikube context
cd backend && docker build -t todo-backend:latest . && cd ..
cd frontend && docker build -t todo-frontend:latest . && cd ..

# Apply Kubernetes manifests
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# Wait for deployments to be ready
kubectl rollout status deployment/todo-backend-deployment
kubectl rollout status deployment/todo-frontend-deployment
```

### Verify Deployment
```bash
kubectl get pods
kubectl get svc
minikube service todo-frontend-service --url
```

## Helm Chart Deployment

### Helm Chart Structure
```
helm/todo-chatbot/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── backend.yaml
│   └── frontend.yaml
└── charts/
```

### Deploy using Helm
```bash
# Add the local chart
cd helm/todo-chatbot

# Install the chart
helm install todo-chatbot .

# Or upgrade if already installed
helm upgrade --install todo-chatbot .
```

## Verification Commands

### Check Pods
```bash
kubectl get pods
```

### Check Services
```bash
kubectl get svc
```

### Get Service URLs
```bash
minikube service todo-frontend-service --url
```

## Troubleshooting

### Common Issues and Solutions

1. **Minikube won't start**
   - Ensure Docker Desktop is running
   - Try with less memory: `minikube start --driver=docker --memory=2048`
   - Check Docker resources allocation in Docker Desktop settings

2. **Images not found in Kubernetes**
   - Make sure to build images in the correct Docker context
   - For Minikube: `eval $(minikube docker-env)` before building
   - For Kind: `kind load docker-image <image-name>`

3. **Backend can't connect to PostgreSQL**
   - Check environment variables in deployment
   - Verify service names and ports
   - Ensure PostgreSQL is running and accessible

4. **Frontend can't connect to backend**
   - Verify NEXT_PUBLIC_API_URL is set correctly
   - Check if backend service is accessible via Kubernetes DNS

5. **Health checks failing**
   - Check application logs: `kubectl logs <pod-name>`
   - Verify health endpoints are accessible

6. **Port conflicts**
   - Use different NodePort numbers if needed
   - Check for existing services on the same ports

### Debugging Commands

```bash
# Check pod logs
kubectl logs deployment/todo-backend-deployment
kubectl logs deployment/todo-frontend-deployment

# Describe pods for detailed info
kubectl describe pod <pod-name>

# Execute commands inside pods
kubectl exec -it <pod-name> -- /bin/sh

# Port forward for local testing
kubectl port-forward service/todo-frontend-service 3000:3000
kubectl port-forward service/todo-backend-service 8000:8000
```

## Cleanup

### Stop and remove containers
```bash
docker stop todo-frontend todo-backend todo-postgres
docker rm todo-frontend todo-backend todo-postgres
docker network rm todo-network
```

### Delete Kubernetes resources
```bash
kubectl delete -f k8s/
# Or delete Helm release
helm uninstall todo-chatbot
```

### Stop Minikube
```bash
minikube stop
```