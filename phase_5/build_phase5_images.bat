@echo off
REM Build Docker images for Phase 5 consumer services

echo Building Phase 5 Consumer Services...

REM Build Notification Service
echo Building notification-service...
docker build -t notification-service:latest ./services/notification-service

REM Build Recurring Task Service
echo Building recurring-task-service...
docker build -t recurring-task-service:latest ./services/recurring-task-service

REM Build Audit Log Service
echo Building audit-log-service...
docker build -t audit-log-service:latest ./services/audit-log-service

REM Build WebSocket Service
echo Building websocket-service...
docker build -t websocket-service:latest ./services/websocket-service

echo.
echo All Phase 5 services built successfully!
echo.
echo Images created:
echo   - notification-service:latest
echo   - recurring-task-service:latest
echo   - audit-log-service:latest
echo   - websocket-service:latest
