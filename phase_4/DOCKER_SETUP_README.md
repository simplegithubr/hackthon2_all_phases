# Docker Setup for Todo AI Chatbot

This guide explains how to build and run the Todo AI Chatbot project using Docker.

## Project Structure
- `backend/` - FastAPI application (runs on port 8000)
- `frontend/` - Next.js application (runs on port 3000)

## Prerequisites
- Docker Desktop installed
- Docker Compose (included with Docker Desktop)

## Method 1: Individual Container Builds

### Build Images
```bash
# Build backend image
cd backend && docker build -t todo-backend:latest .

# Build frontend image
cd ../frontend && docker build -t todo-frontend:latest .
```

### Run Containers
```bash
# Run backend container
docker run -d --name todo-backend -p 8000:8000 todo-backend:latest

# Run frontend container
docker run -d --name todo-frontend -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000/api todo-frontend:latest
```

## Method 2: Docker Compose (Recommended)

### Build and Run
```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access Applications
- Backend API: http://localhost:8000
- Backend Documentation: http://localhost:8000/docs
- Frontend UI: http://localhost:3000

## Verification Commands

```bash
# Check running containers
docker ps

# View backend logs
docker logs todo-backend

# View frontend logs
docker logs todo-frontend

# Test health endpoint
curl http://localhost:8000/health
```

## Environment Variables

The applications support the following environment variables:

Backend (.env in backend directory):
- `JWT_SECRET` - Secret key for JWT tokens
- `DATABASE_URL` - PostgreSQL connection string
- `USE_AI_SERVICES` - Enable/disable AI services (true/false)

Frontend:
- `NEXT_PUBLIC_API_URL` - Backend API URL (default: http://localhost:8000/api)

## Troubleshooting

### Common Issues:

1. **Port already in use**
   ```bash
   # Stop all containers
   docker stop $(docker ps -aq)
   docker rm $(docker ps -aq)
   ```

2. **Build fails due to missing requirements**
   - Ensure `requirements.txt` exists in backend/
   - Ensure `package.json` exists in frontend/

3. **Health checks failing**
   - Check application logs for startup errors
   - Verify environment variables are set correctly

4. **Frontend can't connect to backend**
   - When using docker-compose, use `http://backend:8000/api` as NEXT_PUBLIC_API_URL
   - When running separately, use `http://host.docker.internal:8000/api` on Windows/Mac

### Cleanup
```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi todo-backend:latest todo-frontend:latest

# Remove unused resources
docker system prune -a
```

## Dockerfile Features

Both Dockerfiles include:
- Multi-stage builds for smaller production images
- Non-root user for security
- Health checks for container monitoring
- Optimized layer caching
- Proper cleanup of build dependencies