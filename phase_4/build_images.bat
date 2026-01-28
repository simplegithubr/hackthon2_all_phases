@echo off
echo Building Todo AI Chatbot Docker images...

echo Building backend image...
cd backend
docker build -t todo-backend:latest .
if %ERRORLEVEL% NEQ 0 (
    echo Backend build failed!
    exit /b %ERRORLEVEL%
)

echo Building frontend image...
cd ../frontend
docker build -t todo-frontend:latest .
if %ERRORLEVEL% NEQ 0 (
    echo Frontend build failed!
    exit /b %ERRORLEVEL%
)

echo Build completed successfully!