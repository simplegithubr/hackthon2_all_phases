# Data Model: AI Todo Chatbot

## Existing Models (from Phase II)

### Task Model
- **Fields**:
  - id: int (primary key)
  - title: str (max 200, required)
  - description: Optional[str]
  - priority: str (high/medium/low, default: medium)
  - user_id: str (foreign key to users.id, indexed)
  - is_complete: bool (default: false)
  - created_at: datetime (default: utcnow)
  - updated_at: datetime (default: utcnow)
- **Relationships**: Belongs to User
- **Validation**: Title required, max length 200 chars

### User Model
- **Fields**:
  - id: str (primary key)
  - email: str (unique, indexed)
  - created_at: datetime (default: utcnow)
  - updated_at: datetime (default: utcnow)

## New Models (for AI Chatbot)

### Conversation Model
- **Fields**:
  - id: int (primary key)
  - user_id: str (foreign key to users.id, indexed)
  - created_at: datetime (default: utcnow)
  - updated_at: datetime (default: utcnow)
  - metadata: Optional[dict] (JSON for conversation context)
- **Relationships**: Belongs to User, has many Messages
- **Validation**: User_id required, metadata optional

### Message Model
- **Fields**:
  - id: int (primary key)
  - conversation_id: int (foreign key to conversations.id, indexed)
  - role: str (user/system/assistant, required)
  - content: str (required)
  - timestamp: datetime (default: utcnow)
  - metadata: Optional[dict] (JSON for message context)
- **Relationships**: Belongs to Conversation
- **Validation**: Role must be one of 'user', 'system', or 'assistant'

## State Transitions

### Task State Transitions
- Active → Completed: When task is marked complete via MCP tool
- Completed → Active: When completed task is marked incomplete via MCP tool

### Conversation State Transitions
- Created → Active: When first user message is received
- Active → Inactive: When conversation is dormant for extended period (for cleanup purposes)

## Validation Rules

### From Functional Requirements
- **FR-003**: All operations must be scoped to user_id (enforced via foreign keys and MCP tools)
- **FR-004**: Task ownership validation required before operations (enforced via MCP tools)
- **FR-005**: Conversation history maintained in database (Conversation and Message models)
- **FR-009**: Stateless server operation (server doesn't store state, uses database for context)