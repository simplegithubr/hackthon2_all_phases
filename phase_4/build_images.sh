# Build Docker images for Todo AI Chatbot

# Build backend image
cd backend && docker build -t todo-backend:latest .

# Build frontend image
cd ../frontend && docker build -t todo-frontend:latest .