# API Contract: AI Chatbot Endpoint

## Endpoint: POST /api/chat

### Purpose
Process natural language input from users and return appropriate responses with task operations.

### Request
- **Path**: `/api/chat`
- **Method**: `POST`
- **Authentication**: JWT Bearer token required (via existing auth dependency)
- **Headers**:
  - `Authorization: Bearer {jwt_token}`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "message": "Natural language command (required)",
    "conversation_id": "Optional conversation identifier"
  }
  ```
- **Validation**:
  - `message` is required and must be non-empty string
  - `conversation_id` is optional, if provided must be valid integer

### Response
- **Success**: `200 OK`
  ```json
  {
    "response": "AI-generated response text",
    "conversation_id": "Assigned or existing conversation ID",
    "task_operations": [
      {
        "operation": "add|list|update|complete|delete",
        "status": "success|failed",
        "result": "Operation result details"
      }
    ]
  }
  ```
- **Errors**:
  - `400 Bad Request`: Invalid request format
  - `401 Unauthorized`: Invalid or missing JWT
  - `403 Forbidden`: User attempting to access another user's data
  - `500 Internal Server Error`: Service unavailable

### Processing Flow
1. Authenticate user via JWT
2. Validate request format
3. Load conversation history from database (if conversation_id provided)
4. Process natural language with AI agent
5. Execute MCP tool calls as needed
6. Store new message in conversation history
7. Return AI response with operation results

## MCP Tools Contract

### add_task
- **Input**: `{ "user_id": string, "title": string, "description": string }`
- **Output**: `{ "task_id": int, "status": "created", "title": string }`

### list_tasks
- **Input**: `{ "user_id": string, "status": "all|pending|completed" }`
- **Output**: `{ "tasks": [{"id": int, "title": string, "is_complete": bool, "priority": string}] }`

### complete_task
- **Input**: `{ "user_id": string, "task_id": int }`
- **Output**: `{ "task_id": int, "status": "completed", "title": string }`

### delete_task
- **Input**: `{ "user_id": string, "task_id": int }`
- **Output**: `{ "task_id": int, "status": "deleted", "title": string }`

### update_task
- **Input**: `{ "user_id": string, "task_id": int, "title": string, "description": string }`
- **Output**: `{ "task_id": int, "status": "updated", "title": string }`