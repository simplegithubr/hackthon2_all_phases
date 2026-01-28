# PowerShell script to deploy Todo AI Chatbot to Minikube
# This script assumes:
# 1. Minikube is running
# 2. Docker images are already built (todo-backend:latest and todo-frontend:latest)

Write-Host "Starting deployment to Minikube..." -ForegroundColor Green

# Set Docker environment to use Minikube's Docker daemon
$env_output = minikube docker-env | Out-String
$env_vars = $env_output -split "`n" | Where-Object { $_ -match '^\$env:' }

foreach ($var in $env_vars) {
    if ($var -match '\$env:(\w+)="([^"]*)"') {
        $name = $matches[1]
        $value = $matches[2]
        Set-Item -Path "env:$name" -Value $value
    }
}

Write-Host "Building Docker images in Minikube context..." -ForegroundColor Yellow

# Change to backend directory and rebuild
Set-Location "../backend"
docker build -t todo-backend:latest .

# Change to frontend directory and rebuild
Set-Location "../frontend"
docker build -t todo-frontend:latest .

Write-Host "Deploying to Minikube..." -ForegroundColor Yellow

# Apply the Kubernetes manifests
kubectl apply -f ../k8s/backend-deployment.yaml
kubectl apply -f ../k8s/frontend-deployment.yaml

Write-Host "Waiting for deployments to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/todo-backend-deployment
kubectl rollout status deployment/todo-frontend-deployment

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Backend service: $(minikube service todo-backend-service --url)" -ForegroundColor Cyan
Write-Host "Frontend service: $(minikube service todo-frontend-service --url)" -ForegroundColor Cyan

Write-Host "To access the frontend in your browser, run: minikube service todo-frontend-service --url" -ForegroundColor Cyan