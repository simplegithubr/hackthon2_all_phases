# Implementation Plan: Task CRUD

**Branch**: `001-task-crud` | **Date**: 2025-12-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-task-crud/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This plan implements CRUD operations for tasks in a Todo Full-Stack Web Application (Phase 2). The architecture follows the monorepo pattern with backend-first implementation: FastAPI backend with SQLModel ORM, Neon PostgreSQL database, and Next.js 16+ frontend with App Router. JWT authentication via Better Auth secures all endpoints. Multi-user data isolation is enforced at the database level through user_id filtering on all queries.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Pydantic (backend); Next.js 16+, React 19, Tailwind CSS (frontend)
**Storage**: Neon Serverless PostgreSQL
**Testing**: pytest (backend), Jest/React Testing Library (frontend)
**Target Platform**: Web browser (server-rendered via Next.js)
**Project Type**: Web application (monorepo)
**Performance Goals**: <2s page load, <500ms task updates, support 1000+ concurrent users
**Constraints**: <200ms p95 API response time, 100% JWT validation, no cross-user data access
**Scale/Scope**: Support unlimited users with isolated data, 1000+ tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Security First (JWT)**: Plan enforces JWT authentication on all task endpoints via FastAPI middleware. JWT verification skill will be used for token validation.
✅ **Multi-User Data Isolation**: All database queries include user_id WHERE clauses. Repository pattern prevents cross-user data leaks.
✅ **Spec-Driven Development**: This plan follows spec → plan → tasks workflow. No implementation until tasks.md is approved.
✅ **Monorepo Architecture**: Frontend (Next.js) and backend (FastAPI) in separate directories with shared type contracts.
✅ **Type Safety**: SQLModel/Pydantic for backend validation, TypeScript strict mode for frontend. No `any` types permitted.
✅ **Frontend Coding Standards**: Server Components by default, App Router conventions, service layer for API calls, Tailwind CSS.
✅ **Backend Coding Standards**: SQLModel for request/response, async I/O, dependency injection, repository pattern.
✅ **Claude Code Behavior**: Architect agent delegates to backend/frontend/auth/database agents and sub-agents (api-designer, jwt-verifier, ui-layout, orm-modeler). Skills used: jwt-auth, rest-api, sqlmodel, nextjs-app-router, better-auth.

**Result**: ✅ ALL CONSTITUTION GATES PASSED - No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/001-task-crud/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── tasks-api.yaml    # OpenAPI specification
│   └── types.ts         # TypeScript type definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py            # Task SQLModel definition
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py     # JWT validation dependency
│   │   └── task_service.py    # Business logic layer
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── task_repository.py # Database access with user_id filtering
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py       # Task CRUD endpoints
│   ├── db.py                  # Database connection
│   └── main.py                # FastAPI app entry
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Test fixtures
│   └── test_tasks_api.py       # Contract tests for task endpoints
├── requirements.txt
└── pyproject.toml

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx            # Landing/home
│   │   ├── tasks/
│   │   │   ├── page.tsx        # Task list page (Server Component)
│   │   │   └── components/
│   │   │       ├── TaskList.tsx      # Display tasks
│   │   │       ├── TaskForm.tsx      # Create/edit form
│   │   │       ├── TaskItem.tsx      # Single task display
│   │   │       └── DeleteConfirm.tsx # Delete confirmation
│   │   └── api/
│   │       └── tasks/
│   │           ├── route.ts       # API route handlers
│   │           └── types.ts      # Shared types
│   ├── services/
│   │   └── tasks.ts            # Task API service (typed)
│   └── types/
│       └── tasks.ts             # TypeScript interfaces
├── components/
│   └── ui/                    # Reusable UI components
├── tests/
│   └── tasks/
│       └── TaskList.test.tsx   # Component tests
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

**Structure Decision**: Monorepo with backend/ and frontend/ directories. Backend uses layered architecture (models → repositories → services → routes) for separation of concerns and testability. Frontend follows Next.js 16 App Router with Server Components by default and a dedicated services layer for API calls.

## Architecture Flow

### Backend-First Justification

Backend-first development is chosen for this feature because:

1. **API Contracts Drive Frontend**: Frontend components depend on stable API endpoints and response formats. Backend-first ensures contracts are defined before UI implementation.
2. **Database Schema Foundation**: Task entities and relationships must be defined before frontend can display them meaningfully.
3. **Testability Isolation**: Backend can be unit tested and contract-tested independently without frontend dependencies.
4. **JWT Authentication Layer**: Authentication must be in place before any protected data can be accessed, making it a blocking prerequisite.

### High-Level Flow

```
User Action (Frontend)
    ↓
[FastAPI JWT Middleware] → Validates JWT token, extracts user_id
    ↓
[FastAPI Route Handler] → Receives request, calls service layer
    ↓
[Service Layer] → Business logic, input validation via SQLModel
    ↓
[Repository Layer] → Database queries with user_id WHERE clause enforcement
    ↓
[Neon PostgreSQL] → Data persistence with user_id foreign key
    ↓
[SQLModel Response] → Typed response returned to frontend
    ↓
[Frontend Service Layer] → Type-safe API call, error handling
    ↓
[React Component] → State update, UI refresh
```

### Request Flow Example: Create Task

1. User fills form in `TaskForm.tsx` (Client Component)
2. `TaskForm` calls `tasks.createTask()` from `frontend/src/services/tasks.ts`
3. Frontend service makes POST request to `/api/tasks` with JWT in Authorization header
4. FastAPI middleware validates JWT, extracts `user_id`, attaches to request state
5. Route handler `POST /api/tasks` calls `TaskService.create_task()`
6. Service validates input via SQLModel, calls `TaskRepository.create()`
7. Repository executes `INSERT INTO tasks (title, description, user_id) VALUES (?, ?, ?)`
8. Neon PostgreSQL stores task with `user_id` foreign key
9. Repository returns created Task model
10. Service returns SQLModel to route
11. Route returns 201 with task JSON
12. Frontend receives response, updates state, `TaskList` re-renders

## Implementation Order

### Phase 1: Database Foundation (backend/src/db.py, models/task.py)

**Goal**: Establish data model and database connection

**Milestone**: Database schema defined, migrations ready

**Tasks** (to be detailed in tasks.md):
- Create Task SQLModel with user_id foreign key
- Set up Neon PostgreSQL connection (async session)
- Create initial migration
- Define validation constraints (title not null, max 200 chars)

### Phase 2: Repository Layer (backend/src/repositories/task_repository.py)

**Goal**: Database access with enforced user_id isolation

**Milestone**: All data queries filter by user_id

**Tasks**:
- Create TaskRepository with CRUD operations
- Implement `get_by_user(user_id)` - returns only user's tasks
- Implement `create(task, user_id)` - associates task to user
- Implement `update(id, task, user_id)` - validates ownership
- Implement `delete(id, user_id)` - validates ownership
- Implement `toggle_complete(id, user_id)` - validates ownership

### Phase 3: Authentication Service (backend/src/services/auth_service.py)

**Goal**: JWT validation dependency for FastAPI

**Milestone**: JWT middleware validates tokens on protected routes

**Tasks**:
- Create `get_current_user()` dependency
- Decode JWT, validate signature and expiry
- Extract user_id from JWT claims
- Return 401 if token invalid/missing/expired
- Return 403 if user tries to access another user's data

### Phase 4: Task Service Layer (backend/src/services/task_service.py)

**Goal**: Business logic and orchestration

**Milestone**: Service layer handles CRUD with validation

**Tasks**:
- Create TaskService with repository dependency
- Implement `create_task(title, description, user_id)`
- Implement `get_user_tasks(user_id)` - list all user's tasks
- Implement `update_task(id, title, description, user_id)`
- Implement `delete_task(id, user_id)` with confirmation requirement
- Implement `toggle_task_complete(id, user_id)`

### Phase 5: API Routes (backend/src/api/routes/tasks.py)

**Goal**: RESTful endpoints with JWT protection

**Milestone**: All task endpoints protected and documented

**Tasks**:
- Define routes using api-designer skill:
  - `GET /api/tasks` - list user's tasks
  - `POST /api/tasks` - create new task
  - `PUT /api/tasks/{id}` - update task
  - `DELETE /api/tasks/{id}` - delete task
  - `PATCH /api/tasks/{id}/complete` - toggle completion
- Apply `get_current_user()` dependency to all routes
- Return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Add OpenAPI documentation
- Contract tests for each endpoint

### Phase 6: Frontend API Services (frontend/src/services/tasks.ts)

**Goal**: Type-safe API client for backend

**Milestone**: Frontend can call backend with typed responses

**Tasks**:
- Create TaskService class with typed methods
- Implement `fetchTasks()` - GET /api/tasks
- Implement `createTask(task)` - POST /api/tasks
- Implement `updateTask(id, task)` - PUT /api/tasks/{id}
- Implement `deleteTask(id)` - DELETE /api/tasks/{id}
- Implement `toggleComplete(id)` - PATCH /api/tasks/{id}/complete
- Handle JWT token from localStorage/cookies
- Add error handling (401 redirect to login, 500 show user-friendly message)

### Phase 7: Frontend Components (frontend/src/app/tasks/)

**Goal**: Task management UI

**Milestone**: Users can view, create, edit, delete, and complete tasks

**Tasks**:
- Create `TaskList` Server Component - loads and displays tasks
- Create `TaskForm` Client Component - create/edit form with validation
- Create `TaskItem` Client Component - single task display
- Create `DeleteConfirm` Client Component - delete confirmation dialog
- Implement empty state for no tasks
- Add visual distinction for completed tasks (strikethrough, grayed out)
- Error boundaries for route segments
- Loading states for async operations

### Phase 8: Integration & Testing

**Goal**: End-to-end workflow validation

**Milestone**: Full CRUD workflow works correctly

**Tasks**:
- Test multi-user isolation (User A can't see User B's tasks)
- Test JWT expiration (redirect to login on expired token)
- Test network error handling
- Verify all success criteria (performance, security, usability)
- Quickstart validation (new user can complete full workflow)

## Agent Responsibility Mapping

### Architect Agent (Primary)

**Responsibilities**:
- Coordinate overall implementation plan
- Delegate to specialized agents
- Validate constitution compliance
- Review agent outputs for consistency

### Backend Agent

**Responsibilities**:
- Implement backend phases 1-5 (database, repository, auth, service, routes)
- Use skills: sqlmodel, jwt-auth, rest-api
- Delegate to sub-agents:
  - `orm-modeler` - Define Task SQLModel
  - `api-designer` - Design RESTful endpoints
  - `jwt-verifier` - Validate JWT implementation

### Frontend Agent

**Responsibilities**:
- Implement frontend phases 6-7 (services, components)
- Use skills: nextjs-app-router, better-auth
- Delegate to sub-agents:
  - `ui-layout` - Design component layouts
  - `api-designer` - Ensure frontend contracts match backend

### Auth Agent

**Responsibilities**:
- Integrate Better Auth with backend
- Implement JWT issuance on authentication
- Configure JWT validation middleware
- Use skills: better-auth, jwt-auth

### Database Agent

**Responsibilities**:
- Set up Neon PostgreSQL connection
- Create migrations for Task model
- Verify user_id foreign key constraints
- Use skills: sqlmodel

## Risk Areas and Mitigation

### Risk 1: Multi-User Data Isolation Violation

**Description**: Accidental cross-user data access if user_id filtering is missed in a query.

**Mitigation**:
- Enforce user_id filtering at repository layer ONLY (never in services or routes)
- Add automated tests that verify each query includes user_id WHERE clause
- Use SQLModel's relationship validation to enforce foreign key constraints

**Impact**: High (security/privacy)

### Risk 2: JWT Token Management

**Description**: Expired or invalid JWT tokens causing user confusion.

**Mitigation**:
- Frontend checks token expiry before making requests
- Backend returns 401 for expired tokens with clear "Token expired" message
- Frontend automatically redirects to login on 401
- Implement token refresh via Better Auth

**Impact**: Medium (user experience)

### Risk 3: Database Schema Migrations

**Description**: Breaking changes to Task model in production.

**Mitigation**:
- Use SQLModel's migration framework
- Test migrations on staging environment first
- Keep migrations reversible
- Document schema changes in data-model.md

**Impact**: Medium (deployment complexity)

### Risk 4: Frontend-Backend Contract Drift

**Description**: TypeScript interfaces become out-of-sync with SQLModel definitions.

**Mitigation**:
- Auto-generate TypeScript types from SQLModel (or manual sync documented)
- Contract tests verify backend responses match frontend types
- Regular review of contracts/ directory
- Keep API versioning strategy in mind for future changes

**Impact**: Low-Medium (development friction)

### Risk 5: Performance Degradation with Large Task Lists

**Description**: Users with 1000+ tasks experience slow page loads.

**Mitigation**:
- Implement pagination (e.g., 50 tasks per page)
- Add database indexes on user_id and created_at
- Consider caching frequently accessed task lists
- Monitor query performance in production

**Impact**: Low (user experience, can be addressed post-hackathon)

## Hackathon Timeline Milestones

### Milestone 1: Foundation (Day 1, 4 hours)

**Deliverable**: Backend database and repository layer ready

**Completion Criteria**:
- Task SQLModel defined with user_id foreign key
- Neon PostgreSQL connection working
- TaskRepository implements all CRUD operations with user_id filtering
- Unit tests pass for repository layer

### Milestone 2: Backend API Complete (Day 1, 8 hours)

**Deliverable**: All task endpoints protected and functional

**Completion Criteria**:
- JWT authentication middleware working
- TaskService layer complete
- All 5 API endpoints implemented (GET, POST, PUT, DELETE, PATCH)
- Contract tests pass for all endpoints
- OpenAPI documentation generated

### Milestone 3: Frontend Service Layer (Day 2, 4 hours)

**Deliverable**: Frontend can communicate with backend

**Completion Criteria**:
- TaskService (frontend) implements all API methods
- TypeScript types match backend responses
- JWT token handling implemented
- Error handling for network and auth errors
- Integration tests pass (frontend calls backend successfully)

### Milestone 4: UI Components (Day 2, 8 hours)

**Deliverable**: Full task management UI working

**Completion Criteria**:
- TaskList displays tasks (empty state included)
- TaskForm creates and edits tasks
- TaskItem shows task details and completion toggle
- DeleteConfirm removes tasks
- Visual distinction for completed tasks
- All user stories (P1-P3) independently testable

### Milestone 5: Integration & Polish (Day 2, 10 hours)

**Deliverable**: Production-ready feature

**Completion Criteria**:
- Multi-user isolation verified (users see only their data)
- JWT expiration handling tested
- All success criteria met (performance targets achieved)
- Quickstart passes (new user completes full workflow)
- Code reviewed against constitution
- Documentation updated

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. All principles are followed.

## Dependencies

### External Dependencies

- **Neon PostgreSQL**: Serverless database hosting (account required)
- **Better Auth**: Authentication provider (JWT issuance, session management)
- **GitHub Actions** (optional): CI/CD for testing and deployment

### Internal Dependencies

- This feature assumes Better Auth integration is complete or will be implemented in parallel
- Frontend depends on backend API contracts being stable
- All phases depend on database schema being finalized first

## Next Steps

1. Review this plan and approve architecture approach
2. Generate tasks.md via `/sp.tasks` to create actionable implementation tasks
3. Begin Phase 1: Database Foundation (backend agent)
4. Execute tasks in milestone order (Milestone 1 → Milestone 5)
5. Validate against success criteria at each milestone checkpoint
