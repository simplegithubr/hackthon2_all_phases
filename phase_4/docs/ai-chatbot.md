# AI Todo Chatbot Documentation

## Overview
The AI Todo Chatbot is a natural language interface for managing todo tasks. It allows users to interact with their task lists using conversational commands instead of traditional UI controls.

## Architecture
The system follows the MCP (Model Context Protocol) architecture where all operations go through MCP tools exclusively:

- **Frontend**: Natural language input
- **AI Orchestrator**: Interprets user intent and calls appropriate tools
- **MCP Tools**: Interface with the existing backend
- **Backend**: Existing Phase II infrastructure

## Available Commands

### Task Creation
- "Add a task to buy groceries"
- "Create a task called 'finish report'"
- "Make a new task to call John"

### Task Listing
- "Show me my tasks"
- "List all my tasks"
- "What do I have to do?"
- "Show completed tasks"
- "Show pending tasks"

### Task Completion
- "Complete the grocery task"
- "Mark 'buy milk' as done"
- "Finish the meeting prep task"

### Task Updates
- "Update the title of task 1 to 'new title'"
- "Change description of grocery task to 'get organic food'"

### Task Deletion
- "Delete the old task"
- "Remove task 1"
- "Cancel the meeting task"

## MCP Tools

### add_task
- Parameters: `user_id`, `title`, `description`
- Creates a new task for the user

### list_tasks
- Parameters: `user_id`, `status` (optional: all, pending, completed)
- Lists tasks for the user

### complete_task
- Parameters: `user_id`, `task_id`
- Marks a task as completed

### delete_task
- Parameters: `user_id`, `task_id`
- Deletes a task

### update_task
- Parameters: `user_id`, `task_id`, `title`, `description`
- Updates a task

## Security
- All operations are scoped to the authenticated user
- User isolation is enforced at the database level
- MCP tools validate ownership before operations
- JWT authentication required for all endpoints

## Error Handling
- Invalid natural language returns helpful suggestions
- Permission errors are gracefully handled
- Network/service errors are caught and communicated to users

## Implementation Details
- Built with OpenAI GPT-4 Turbo for natural language understanding
- Uses function calling to execute precise operations
- Maintains conversation context across requests
- Stores conversation history in the database