# Claude Code Rules - Todo AI Chatbot Extension

This file extends the main Claude Code Rules for AI Chatbot specific functionality.

## AI Chatbot Specific Guidelines

### MCP Server Interaction
- All database interactions MUST go through MCP tools only
- Never access database directly from AI agents
- Always verify user_id scope in MCP tool calls
- Handle MCP tool errors gracefully

### Natural Language Processing
- Interpret user intent from natural language commands
- Map natural language to appropriate MCP tool calls
- Support various phrasings for the same operation
- Provide helpful error messages for unrecognized commands

### Conversation Management
- Maintain conversation context across requests
- Store conversation history in database
- Use conversation_id to continue existing conversations
- Handle conversation state appropriately

### Task Operations Mapping
- "Add task..." → add_task MCP tool
- "Show tasks", "list tasks", "what are my tasks" → list_tasks MCP tool
- "Complete task...", "mark task as done" → complete_task MCP tool
- "Delete task...", "remove task..." → delete_task MCP tool
- "Update task...", "change task..." → update_task MCP tool

### Error Handling
- Provide user-friendly error messages
- Never expose internal system errors to users
- Suggest alternatives when operations fail
- Maintain conversation flow even during errors