# Quickstart Guide: AI Todo Chatbot

## Overview
This guide walks through setting up and running the AI Todo Chatbot (Phase III) that integrates with the existing Phase II backend.

## Prerequisites
- Python 3.11+
- Poetry or pip for dependency management
- PostgreSQL database (existing Phase II setup)
- OpenAI API key
- Cohere API key

## Environment Setup

### 1. Clone and Navigate
```bash
cd backend  # Already in the backend directory
```

### 2. Install Dependencies
```bash
pip install openai cohere-toolkit  # Add to requirements.txt
poetry install  # If using poetry
```

### 3. Environment Variables
Create `.env` file in backend root:
```bash
OPENAI_API_KEY=your_openai_api_key
COHERE_API_KEY=your_cohere_api_key
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname  # Existing from Phase II
```

## Running the Application

### 1. Database Migrations
```bash
# Run existing Phase II migrations first
alembic upgrade head
```

### 2. Start the Server
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

### 3. Test the Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

## Configuration

### AI Model Settings
- Default model: gpt-4-turbo (can be changed in agent configuration)
- Temperature: 0.7 for balanced creativity and accuracy
- Timeout: 30 seconds for AI responses

### MCP Tools Configuration
- Tools are automatically registered with the AI agent
- All operations are user-scoped via JWT validation
- Database operations go through existing repositories

## Troubleshooting

### Common Issues
1. **JWT Authentication Failures**
   - Verify your JWT token is valid and not expired
   - Check that you're using the correct authorization header format

2. **AI Service Unavailable**
   - Verify API keys are correct and have sufficient quota
   - Check network connectivity to AI services

3. **Database Connection Issues**
   - Ensure database URL is correctly configured
   - Verify database is running and accessible

### Verification Steps
1. Test existing task endpoints to ensure Phase II functionality still works
2. Verify JWT authentication works with new chat endpoint
3. Test natural language commands and confirm MCP tools are called appropriately
4. Check conversation history is being saved and retrieved correctly

## Next Steps
- Implement the todo_orchestrator agent
- Register MCP tools with the AI agent
- Test end-to-end natural language task operations
- Verify user isolation and security requirements