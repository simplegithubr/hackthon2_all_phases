# Quickstart: Task CRUD Feature

**Feature**: 001-task-crud
**Purpose**: Onboarding guide for developers working on Task CRUD functionality

## Prerequisites

### Required Accounts

- **Neon PostgreSQL**: Create free account at https://neon.tech
  - Create a new project
  - Copy connection string (format: `postgresql://user:password@host:port/database?sslmode=require`)

- **Better Auth** (if implementing auth): Sign up at https://better-auth.com

### Required Tools

- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- Git (for version control)
- VS Code or similar editor (recommended)

### Environment Variables

Create `.env` files (from `.env.example` templates):

**Backend (backend/.env)**:
```bash
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
NEON_DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**Frontend (frontend/.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

---

## Getting Started

### Step 1: Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd hackthon2_phese2_todo

# Install Python backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install Node frontend dependencies
cd ../frontend
npm install
```

### Step 2: Configure Database

```bash
# Set Neon database URL in backend/.env
cd ../backend
cp .env.example .env
# Edit .env and set DATABASE_URL from Neon

# Run database migrations
alembic upgrade head
```

### Step 3: Start Backend Server

```bash
# From backend directory
cd backend

# Start FastAPI server
uvicorn src.main:app --reload --port 8000

# API documentation will be available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Step 4: Start Frontend Dev Server

```bash
# From frontend directory (new terminal)
cd frontend

# Start Next.js dev server
npm run dev

# Application will be available at:
# http://localhost:3000
```

---

## Development Workflow

### Creating a New Task

1. Navigate to http://localhost:3000
2. Click "Sign Up" (if Better Auth integrated) and create account
3. Enter task title (required) and description (optional) in form
4. Click "Create Task"
5. Task appears in list below form

### Viewing Tasks

1. After login, navigate to Tasks page (http://localhost:3000/tasks)
2. See list of all your tasks (sorted by creation date, newest first)
3. Completed tasks show with strikethrough and grayed out

### Updating a Task

1. Click "Edit" button on any task
2. Form pre-populates with existing title and description
3. Modify title and/or description
4. Click "Update Task"
5. Task refreshes with updated information

### Marking Task Complete

1. Click checkbox on task
2. Task toggles between complete/incomplete
3. Visual feedback shows new completion status

### Deleting a Task

1. Click "Delete" button (trash icon) on task
2. Confirmation dialog appears
3. Click "Confirm" to permanently delete
4. Task removed from list

---

## Testing Multi-User Isolation

### Scenario 1: User A Can't See User B's Tasks

1. Sign up as User A (email: user-a@example.com)
2. Create task: "User A's Task"
3. Sign out
4. Sign up as User B (email: user-b@example.com)
5. **Verify**: User B sees empty task list (User A's task not visible)
6. User B creates task: "User B's Task"
7. Sign out
8. Sign in as User A
9. **Verify**: User A still only sees "User A's Task" (User B's task not visible)

### Scenario 2: User A Can't Modify User B's Tasks

1. Sign up as User A and User B (separate browsers or incognito mode)
2. User A creates task: "User A's Task"
3. User B obtains task ID (e.g., via network tab in browser DevTools)
4. User B attempts to update task via API:
   ```bash
   curl -X PUT http://localhost:8000/api/tasks/<task-id> \
     -H "Authorization: Bearer <User-B-JWT>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Hacked Title"}'
   ```
5. **Verify**: API returns 403 Forbidden with permission denied message
6. User A verifies task title unchanged ("User A's Task")

---

## API Endpoints

### Authentication Required

All endpoints require JWT token in `Authorization` header:
```
Authorization: Bearer <JWT_TOKEN>
```

### Get User's Tasks

```bash
GET /api/tasks
Authorization: Bearer <JWT_TOKEN>

Response (200 OK):
{
  "tasks": [
    {
      "id": 1,
      "user_id": "user-123",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "is_complete": false,
      "created_at": "2025-12-31T10:00:00Z",
      "updated_at": "2025-12-31T10:00:00Z"
    }
  ]
}
```

### Create New Task

```bash
POST /api/tasks
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

Request Body:
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}

Response (201 Created):
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_complete": false,
  "created_at": "2025-12-31T10:00:00Z",
  "updated_at": "2025-12-31T10:00:00Z"
}
```

### Update Task

```bash
PUT /api/tasks/{id}
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

Request Body:
{
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, butter"
}

Response (200 OK):
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, butter",
  "is_complete": false,
  "created_at": "2025-12-31T10:00:00Z",
  "updated_at": "2025-12-31T10:05:00Z"
}
```

### Toggle Task Completion

```bash
PATCH /api/tasks/{id}/complete
Authorization: Bearer <JWT_TOKEN>

Response (200 OK):
{
  "id": 1,
  "user_id": "user-123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "is_complete": true,
  "created_at": "2025-12-31T10:00:00Z",
  "updated_at": "2025-12-31T10:10:00Z"
}
```

### Delete Task

```bash
DELETE /api/tasks/{id}
Authorization: Bearer <JWT_TOKEN>

Response (204 No Content)
```

---

## Error Scenarios

### Missing JWT Token

```bash
GET /api/tasks

Response (401 Unauthorized):
{
  "detail": "Authentication required"
}
```

### Invalid JWT Token

```bash
GET /api/tasks
Authorization: Bearer invalid-token

Response (401 Unauthorized):
{
  "detail": "Invalid or expired token"
}
```

### Task Title Too Long

```bash
POST /api/tasks
Authorization: Bearer <valid-jwt>
Content-Type: application/json

Request Body:
{
  "title": "x" * 201,  # > 200 characters
  "description": null
}

Response (400 Bad Request):
{
  "detail": "Task title cannot exceed 200 characters"
}
```

### Missing Task Title

```bash
POST /api/tasks
Authorization: Bearer <valid-jwt>
Content-Type: application/json

Request Body:
{
  "title": "",  # Empty
  "description": null
}

Response (400 Bad Request):
{
  "detail": "Task title is required"
}
```

### Task Not Found

```bash
GET /api/tasks/999999
Authorization: Bearer <valid-jwt>

Response (404 Not Found):
{
  "detail": "Task not found"
}
```

### Accessing Another User's Task

```bash
PUT /api/tasks/1
Authorization: Bearer <user-b-jwt>
Content-Type: application/json

Request Body:
{
  "title": "Hacked"
}

Response (403 Forbidden):
{
  "detail": "You don't have permission to access this task"
}
```

---

## Troubleshooting

### Database Connection Errors

**Error**: `sqlalchemy.exc.DBAPIError: (psycopg2.OperationalError) could not connect`

**Solution**:
1. Verify DATABASE_URL in backend/.env matches Neon connection string
2. Ensure Neon project is active (not paused)
3. Check network connectivity
4. Verify SSL mode is enabled (`sslmode=require`)

### JWT Token Errors

**Error**: `401 Unauthorized: Invalid or expired token`

**Solution**:
1. Check JWT_SECRET matches between Better Auth and FastAPI
2. Ensure token is not expired
3. Verify token is passed in `Authorization: Bearer <token>` header
4. Sign out and sign in again to get fresh token

### CORS Errors (Frontend to Backend)

**Error**: Browser console shows CORS policy violation

**Solution**:
1. Check FastAPI CORS middleware in backend/src/main.py
2. Ensure `NEXT_PUBLIC_API_URL` matches backend URL
3. Verify backend server is running on port 8000
4. Add frontend URL to CORS origins list in main.py

### Multi-User Isolation Failures

**Symptom**: User A can see User B's tasks

**Investigation**:
1. Check repository layer in backend/src/repositories/task_repository.py
2. Verify ALL queries include `WHERE user_id = ?` clause
3. Check FastAPI routes apply `get_current_user()` dependency
4. Review contract tests for user_id filtering

---

## Success Criteria Checklist

Verify the following before marking feature complete:

- [ ] Users can create a task in under 5 seconds from page load to confirmation
- [ ] Users can view their task list in under 2 seconds from page load
- [ ] Task updates (completion toggle, edit) complete and reflect in UI within 500ms
- [ ] 100% of user data requests filter by user_id (no cross-user data leaks)
- [ ] All protected endpoints reject requests with missing, invalid, or expired JWT tokens
- [ ] Users can successfully complete full create → view → update → complete → delete workflow
- [ ] 90% of first-time users can create their first task without assistance

---

## Next Steps

After completing quickstart:

1. Review [spec.md](spec.md) for detailed requirements
2. Read [data-model.md](data-model.md) for Task entity structure
3. Follow [tasks.md](tasks.md) to implement feature
4. Run contract tests in backend/tests/test_tasks_api.py
5. Validate against [constitution.md](../../.specify/memory/constitution.md)

---

## Support

- Backend API docs: http://localhost:8000/docs
- Feature specification: [spec.md](spec.md)
- Implementation plan: [plan.md](plan.md)
- Task list: [tasks.md](tasks.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
