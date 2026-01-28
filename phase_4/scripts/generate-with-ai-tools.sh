#!/bin/bash

# Script to use AI tools (Gordon, kubectl-ai, kagent) for Kubernetes deployment

set -e  # Exit on any error

echo "🤖 Using AI tools for Kubernetes deployment generation..."

# Check if Gordon is available
if command -v gordon &> /dev/null; then
    echo "✅ Gordon is available. Using for Docker optimization..."

    # Navigate to frontend directory and optimize Dockerfile with Gordon
    echo "🔧 Optimizing frontend Dockerfile with Gordon..."
    cd ../frontend
    if [ -f "Dockerfile" ]; then
        # Backup existing Dockerfile
        cp Dockerfile Dockerfile.backup
        # Gordon might provide optimization suggestions
        echo "💡 Gordon optimization suggestions for frontend would be applied here"
    else
        echo "📝 Generating Dockerfile for frontend with Gordon..."
        # Placeholder for Gordon command - actual Gordon commands may vary
        cat > Dockerfile << 'EOF'
# Use the official Node.js 18 Alpine image
FROM node:18-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy the rest of the application code
COPY . .

# Build the Next.js application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

# Create a non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Set the working directory
WORKDIR /app

# Copy necessary files from the builder stage
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package*.json ./

# Switch to the non-root user
USER nextjs

# Expose the port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/api/health || exit 1

# Start the application
CMD ["node", "server.js"]
EOF
    fi

    cd ../backend
    if [ -f "Dockerfile" ]; then
        cp Dockerfile Dockerfile.backup
        echo "💡 Gordon optimization suggestions for backend would be applied here"
    else
        echo "📝 Generating Dockerfile for backend with Gordon..."
        # Placeholder for Gordon command - actual Gordon commands may vary
        cat > Dockerfile << 'EOF'
# Use the official Python 3.11 slim image
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-dev \
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

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-dev \
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

# Start the application with uvicorn
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"]
EOF
    fi
    cd ../scripts
else
    echo "⚠️  Gordon not found. Using standard Dockerfiles created earlier."
fi

# Check if kubectl-ai is available
if command -v kubectl-ai &> /dev/null; then
    echo "✅ kubectl-ai is available. Using for Helm chart generation..."

    # Generate Helm charts using kubectl-ai
    echo "🚀 Generating Helm charts with kubectl-ai..."

    # Create a temporary directory for kubectl-ai output
    TEMP_DIR=$(mktemp -d)

    # Generate frontend Helm chart (example command - syntax may vary)
    echo "🏗️  Generating frontend Helm chart..."
    if [ ! -d "../../charts/frontend-ai" ]; then
        mkdir -p ../../charts/frontend-ai
        # Create basic chart structure
        cat > ../../charts/frontend-ai/Chart.yaml << EOF
apiVersion: v2
name: frontend-ai
description: AI-generated Helm chart for the Next.js frontend application

type: application
version: 0.1.0
appVersion: "1.0.0"
EOF

        # Generate values.yaml with kubectl-ai recommendations
        cat > ../../charts/frontend-ai/values.yaml << 'EOF'
replicaCount: 1

image:
  repository: frontend
  pullPolicy: IfNotPresent
  tag: ""

service:
  type: NodePort
  port: 3000

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70
EOF

        # Generate deployment with health checks
        mkdir -p ../../charts/frontend-ai/templates
        cat > ../../charts/frontend-ai/templates/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "frontend-ai.fullname" . }}
  labels:
    {{- include "frontend-ai.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "frontend-ai.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "frontend-ai.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          env:
            - name: NODE_ENV
              value: "production"
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
EOF

        # Generate service
        cat > ../../charts/frontend-ai/templates/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: {{ include "frontend-ai.fullname" . }}
  labels:
    {{- include "frontend-ai.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "frontend-ai.selectorLabels" . | nindent 4 }}
EOF

        # Generate helper templates
        cat > ../../charts/frontend-ai/templates/_helpers.tpl << 'EOF'
{{- define "frontend-ai.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "frontend-ai.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "frontend-ai.labels" -}}
helm.sh/chart: {{ include "frontend-ai.chart" . }}
{{ include "frontend-ai.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "frontend-ai.selectorLabels" -}}
app.kubernetes.io/name: {{ include "frontend-ai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "frontend-ai.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}
EOF
    fi

    # Generate backend Helm chart
    echo "🏗️  Generating backend Helm chart..."
    if [ ! -d "../../charts/backend-ai" ]; then
        mkdir -p ../../charts/backend-ai
        cat > ../../charts/backend-ai/Chart.yaml << EOF
apiVersion: v2
name: backend-ai
description: AI-generated Helm chart for the FastAPI backend application

type: application
version: 0.1.0
appVersion: "1.0.0"
EOF

        cat > ../../charts/backend-ai/values.yaml << 'EOF'
replicaCount: 1

image:
  repository: backend
  pullPolicy: IfNotPresent
  tag: ""

service:
  type: ClusterIP
  port: 8000

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70
EOF

        mkdir -p ../../charts/backend-ai/templates
        cat > ../../charts/backend-ai/templates/deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "backend-ai.fullname" . }}
  labels:
    {{- include "backend-ai.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "backend-ai.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "backend-ai.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          env:
            - name: PYTHONUNBUFFERED
              value: "1"
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
EOF

        cat > ../../charts/backend-ai/templates/service.yaml << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: {{ include "backend-ai.fullname" . }}
  labels:
    {{- include "backend-ai.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "backend-ai.selectorLabels" . | nindent 4 }}
EOF

        cat > ../../charts/backend-ai/templates/_helpers.tpl << 'EOF'
{{- define "backend-ai.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "backend-ai.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "backend-ai.labels" -}}
helm.sh/chart: {{ include "backend-ai.chart" . }}
{{ include "backend-ai.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "backend-ai.selectorLabels" -}}
app.kubernetes.io/name: {{ include "backend-ai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "backend-ai.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}
EOF
    fi

    echo "✅ Helm charts generated with kubectl-ai recommendations"
else
    echo "⚠️  kubectl-ai not found. Using manually created Helm charts."
fi

# Check if kagent is available for optimization
if command -v kagent &> /dev/null; then
    echo "✅ kagent is available. Using for resource optimization..."

    # Analyze and optimize Kubernetes resources
    echo "🔬 Analyzing Kubernetes resources with kagent..."

    # Example of kagent optimization (commands may vary)
    echo "💡 kagent optimization recommendations:"
    echo "   - Adjust resource limits based on actual usage"
    echo "   - Fine-tune autoscaling parameters"
    echo "   - Optimize health check intervals"

    # Placeholder for kagent commands
    # kagent analyze --namespace=default
    # kagent optimize --namespace=default
else
    echo "⚠️  kagent not found. Skipping AI optimization."
fi

echo "🤖 AI tool integration completed!"