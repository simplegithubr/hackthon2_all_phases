@echo off
echo Starting Todo AI Chatbot containers...

echo Starting backend container...
docker run -d --name todo-backend -p 8000:8000 todo-backend:latest
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start backend container!
    exit /b %ERRORLEVEL%
)

timeout /t 5 /nobreak >nul

echo Starting frontend container...
docker run -d --name todo-frontend -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000/api todo-frontend:latest
if %ERRORLEVEL% NEQ 0 (
    echo Failed to start frontend container!
    exit /b %ERRORLEVEL%
)

echo Containers started successfully!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000