---

description: "Task list for Task CRUD feature implementation"
---

# Tasks: Task CRUD


**Input**: Design documents from `/specs/001-task-crud/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are optional for this feature - only include tests if explicitly requested during implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` at repository root
- **Frontend**: `frontend/src/` at repository root
- **Tests**: `backend/tests/` and `frontend/tests/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create monorepo directory structure: backend/, frontend/
- [ ] T002 Initialize Python backend project with pyproject.toml and requirements.txt (FastAPI, SQLModel, Pydantic, asyncpg)
- [ ] T003 Initialize Next.js 16+ frontend project with TypeScript strict mode
- [ ] T004 [P] Configure Python linting (ruff) and formatting (black)
- [ ] T005 [P] Configure TypeScript linting (ESLint) and formatting (Prettier)
- [ ] T006 [P] Create .env.example template for backend (DATABASE_URL, JWT_SECRET, NEON_DATABASE_URL)
- [ ] T007 [P] Create .env.local.example template for frontend (NEXT_PUBLIC_API_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation (Database Agent)

- [ ] T008 Create backend/src/db.py with async SQLAlchemy engine and session management (Database Agent)
- [ ] T009 Create backend/src/models/__init__.py (Database Agent)
- [ ] T010 Create backend/src/models/task.py with Task SQLModel (TaskCreate, TaskUpdate, Task, TaskRead) (Database Agent)
- [ ] T011 Create database migration script for tasks table with user_id foreign key (Database Agent)

### Authentication Foundation (Auth Agent)

- [ ] T012 Create backend/src/services/auth_service.py with get_current_user() dependency (Auth Agent)
- [ ] T013 Implement JWT token decoding, signature validation, and expiry checking in auth_service.py (Auth Agent)
- [ ] T014 Configure FastAPI to extract user_id from JWT claims and attach to request state (Auth Agent)

### Backend API Structure (Backend Agent)

- [ ] T015 Create backend/src/api/__init__.py (Backend Agent)
- [ ] T016 Create backend/src/api/dependencies.py with get_current_user dependency injection (Backend Agent)
- [ ] T017 Create backend/src/api/routes/__init__.py (Backend Agent)
- [ ] T018 Create backend/src/services/__init__.py (Backend Agent)
- [ ] T019 Create backend/src/repositories/__init__.py (Backend Agent)
- [ ] T020 Create backend/src/main.py with FastAPI app and CORS middleware (Backend Agent)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View My Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can view their personal list of tasks, showing only tasks belonging to them

**Independent Test**: Users can sign up, log in, and see an empty or populated task list. Each user sees only their own tasks, never tasks from other users.

### Backend Implementation (US1)

- [ ] T021 Create backend/src/repositories/task_repository.py with get_by_user(user_id) method (Backend Agent)
- [ ] T022 Implement user_id WHERE clause filtering in task_repository.get_by_user() (Backend Agent)
- [ ] T023 Create backend/src/services/task_service.py with get_user_tasks(user_id) method (Backend Agent)
- [ ] T024 Create backend/src/api/routes/tasks.py with GET /api/tasks endpoint (Backend Agent)
- [ ] T025 Apply get_current_user dependency to GET /api/tasks endpoint (Backend Agent)
- [ ] T026 Return 404 if no tasks found for user in GET /api/tasks endpoint (Backend Agent)
- [ ] T027 Return appropriate HTTP status codes (200, 401, 500) in GET /api/tasks endpoint (Backend Agent)

### Frontend Services (US1)

- [ ] T028 Create frontend/src/types/tasks.ts with Task interface (Frontend Agent)
- [ ] T029 Create frontend/src/services/tasks.ts with TaskService class (Frontend Agent)
- [ ] T030 Implement fetchTasks() method in frontend/src/services/tasks.ts (Frontend Agent)
- [ ] T031 Add JWT token handling (extract from cookies) in frontend/src/services/tasks.ts (Frontend Agent)
- [ ] T032 Add error handling (401 redirect to login, 500 user message) in frontend/src/services/tasks.ts (Frontend Agent)

### Frontend Components (US1)

- [ ] T033 Create frontend/src/app/tasks/page.tsx as Server Component (Frontend Agent)
- [ ] T034 Create frontend/src/app/tasks/components/TaskList.tsx to display tasks (Frontend Agent)
- [ ] T035 Implement empty state message in TaskList.tsx (Frontend Agent)
- [ ] T036 Add visual distinction for completed tasks (strikethrough, grayed out) in TaskList.tsx (Frontend Agent)
- [ ] T037 Add loading state for async task fetching in TaskList.tsx (Frontend Agent)
- [ ] T038 Add error boundary for route segment in frontend/src/app/tasks/page.tsx (Frontend Agent)

**Checkpoint**: At this point, users can view their tasks independently. User Story 1 should be fully functional and testable.

---

## Phase 4: User Story 2 - Create New Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks by providing a title (required) and optional description

**Independent Test**: Users can create a task through the UI, task appears in their list, and is persisted across sessions.

### Backend Implementation (US2)

- [ ] T039 Implement create(task, user_id) method in backend/src/repositories/task_repository.py (Backend Agent)
- [ ] T040 Implement create_task(title, description, user_id) method in backend/src/services/task_service.py (Backend Agent)
- [ ] T041 Validate task title is not empty in task_service.create_task() (Backend Agent)
- [ ] T042 Validate task title max 200 characters in task_service.create_task() (Backend Agent)
- [ ] T043 Add POST /api/tasks endpoint to backend/src/api/routes/tasks.py (Backend Agent)
- [ ] T044 Apply get_current_user dependency to POST /api/tasks endpoint (Backend Agent)
- [ ] T045 Return 201 with created task on POST /api/tasks success (Backend Agent)
- [ ] T046 Return 400 validation error for missing title in POST /api/tasks endpoint (Backend Agent)
- [ ] T047 Return 400 validation error for title > 200 chars in POST /api/tasks endpoint (Backend Agent)

### Frontend Services (US2)

- [ ] T048 Add TaskCreate interface to frontend/src/types/tasks.ts (Frontend Agent)
- [ ] T049 Implement createTask(task) method in frontend/src/services/tasks.ts (Frontend Agent)
- [ ] T050 Add title validation in frontend TaskForm before API call (Frontend Agent)

### Frontend Components (US2)

- [ ] T051 Create frontend/src/app/tasks/components/TaskForm.tsx as Client Component (Frontend Agent)
- [ ] T052 Implement form with title input (required) and description textarea (optional) in TaskForm.tsx (Frontend Agent)
- [ ] T053 Add client-side validation (title not empty, max 200 chars) in TaskForm.tsx (Frontend Agent)
- [ ] T054 Call tasks.createTask() on form submit in TaskForm.tsx (Frontend Agent)
- [ ] T055 Refresh task list after successful creation in TaskList.tsx (Frontend Agent)
- [ ] T056 Show error messages for validation failures in TaskForm.tsx (Frontend Agent)

**Checkpoint**: At this point, Users 1 and 2 (View and Create) should both work independently.

---

## Phase 5: User Story 3 - Update Task Details (Priority: P2)

**Goal**: Users can modify an existing task's title and description

**Independent Test**: Users can edit a task's title and description, save changes, and see the updated information immediately in their task list.

### Backend Implementation (US3)

- [ ] T057 Implement update(id, task, user_id) method in backend/src/repositories/task_repository.py (Backend Agent)
- [ ] T058 Add user_id validation in repository update to verify ownership (Backend Agent)
- [ ] T059 Implement update_task(id, title, description, user_id) method in backend/src/services/task_service.py (Backend Agent)
- [ ] T060 Add PUT /api/tasks/{id} endpoint to backend/src/api/routes/tasks.py (Backend Agent)
- [ ] T061 Apply get_current_user dependency to PUT /api/tasks/{id} endpoint (Backend Agent)
- [ ] T062 Return 403 if user tries to update another user's task in PUT endpoint (Backend Agent)
- [ ] T063 Return 404 if task not found in PUT /api/tasks/{id} endpoint (Backend Agent)
- [ ] T064 Return 400 validation error for empty title in PUT endpoint (Backend Agent)

### Frontend Services (US3)

- [ ] T065 Add TaskUpdate interface to frontend/src/types/tasks.ts (Frontend Agent)
- [ ] T066 Implement updateTask(id, task) method in frontend/src/services/tasks.ts (Frontend Agent)

### Frontend Components (US3)

- [ ] T067 Modify TaskForm.tsx to support edit mode (accept initial task data) (Frontend Agent)
- [ ] T068 Populate form fields with existing task data in edit mode (Frontend Agent)
- [ ] T069 Call tasks.updateTask() on form submit in edit mode (Frontend Agent)
- [ ] T070 Show 403 "permission denied" error for cross-user update attempts (Frontend Agent)

**Checkpoint**: User Stories 1, 2, and 3 (View, Create, Update) should all work independently.

---

## Phase 6: User Story 4 - Mark Task Complete (Priority: P2)

**Goal**: Users can mark tasks as complete or incomplete with visual feedback

**Independent Test**: Users can toggle a task's completion status and see the change reflected immediately with appropriate visual styling.

### Backend Implementation (US4)

- [ ] T071 Implement toggle_complete(id, user_id) method in backend/src/repositories/task_repository.py (Backend Agent)
- [ ] T072 Add user_id validation in repository toggle_complete (Backend Agent)
- [ ] T073 Implement toggle_task_complete(id, user_id) method in backend/src/services/task_service.py (Backend Agent)
- [ ] T074 Add PATCH /api/tasks/{id}/complete endpoint to backend/src/api/routes/tasks.py (Backend Agent)
- [ ] T075 Apply get_current_user dependency to PATCH /api/tasks/{id}/complete endpoint (Backend Agent)
- [ ] T076 Return 403 if user tries to toggle another user's task in PATCH endpoint (Backend Agent)
- [ ] T077 Return 200 with updated task on successful toggle (Backend Agent)

### Frontend Services (US4)

- [ ] T078 Implement toggleComplete(id) method in frontend/src/services/tasks.ts (Frontend Agent)

### Frontend Components (US4)

- [ ] T079 Add checkbox or toggle button to TaskItem.tsx (Frontend Agent)
- [ ] T080 Call tasks.toggleComplete() on toggle click in TaskItem.tsx (Frontend Agent)
- [ ] T081 Update task.is_complete and refresh display in TaskItem.tsx (Frontend Agent)

**Checkpoint**: User Stories 1-4 (View, Create, Update, Complete) should all work independently.

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Users can permanently delete tasks with confirmation

**Independent Test**: Users can delete a task, confirm the action, and see the task removed from their list.

### Backend Implementation (US5)

- [ ] T082 Implement delete(id, user_id) method in backend/src/repositories/task_repository.py (Backend Agent)
- [ ] T083 Add user_id validation in repository delete (Backend Agent)
- [ ] T084 Implement delete_task(id, user_id) method in backend/src/services/task_service.py (Backend Agent)
- [ ] T085 Add DELETE /api/tasks/{id} endpoint to backend/src/api/routes/tasks.py (Backend Agent)
- [ ] T086 Apply get_current_user dependency to DELETE /api/tasks/{id} endpoint (Backend Agent)
- [ ] T087 Return 403 if user tries to delete another user's task in DELETE endpoint (Backend Agent)
- [ ] T088 Return 204 No Content on successful deletion (Backend Agent)

### Frontend Services (US5)

- [ ] T089 Implement deleteTask(id) method in frontend/src/services/tasks.ts (Frontend Agent)

### Frontend Components (US5)

- [ ] T090 Create frontend/src/app/tasks/components/DeleteConfirm.tsx as Client Component (Frontend Agent)
- [ ] T091 Add delete button/icon to TaskItem.tsx (Frontend Agent)
- [ ] T092 Show DeleteConfirm modal on delete button click in TaskItem.tsx (Frontend Agent)
- [ ] T093 Confirm deletion in DeleteConfirm.tsx (Frontend Agent)
- [ ] T094 Call tasks.deleteTask() on confirmation (Frontend Agent)
- [ ] T095 Refresh task list after successful deletion (Frontend Agent)

**Checkpoint**: All user stories (View, Create, Update, Complete, Delete) should now be independently functional.

---

## Phase 8: Integration & Polish (Cross-Cutting Concerns)

**Purpose**: Improvements that affect multiple user stories

### Backend Integration (Backend Agent)

- [ ] T096 Add OpenAPI documentation to backend/src/main.py (Backend Agent)
- [ ] T097 Create backend/tests/conftest.py with test fixtures (Backend Agent)
- [ ] T098 Create backend/tests/test_tasks_api.py with contract tests for all endpoints (Backend Agent)
- [ ] T099 Test multi-user isolation in contract tests (user A can't see user B's tasks) (Backend Agent)
- [ ] T100 Test JWT expiration handling in contract tests (redirect to login on 401) (Backend Agent)

### Frontend Integration (Frontend Agent)

- [ ] T101 Create frontend/src/app/layout.tsx root layout with Tailwind CSS integration (Frontend Agent)
- [ ] T102 Configure Tailwind CSS in frontend/tailwind.config.ts (Frontend Agent)
- [ ] T103 Create frontend/src/app/page.tsx landing page (Frontend Agent)
- [ ] T104 Add network error handling across all frontend services (Frontend Agent)
- [ ] T105 Test complete user workflow (create → view → update → complete → delete) (Frontend Agent)

### Documentation & Validation

- [ ] T106 Create specs/001-task-crud/contracts/tasks-api.yaml OpenAPI specification (Backend Agent)
- [ ] T107 Create specs/001-task-crud/contracts/types.ts TypeScript type definitions (Backend Agent)
- [ ] T108 Create specs/001-task-crud/quickstart.md with onboarding steps (Backend Agent)
- [ ] T109 Verify all success criteria from spec.md are met (performance targets, security, usability) (Backend Agent)
- [ ] T110 Validate code against constitution (JWT enforced, multi-user isolation, type safety) (Backend Agent)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1/US2 → US3/US4 → US5)
- **Integration (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (View)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (Create)**: Can start after Foundational - Integrates with US1 but independently testable
- **User Story 3 (Update)**: Can start after Foundational - Integrates with US1/US2 but independently testable
- **User Story 4 (Complete)**: Can start after Foundational - Depends on US1 (TaskList), independently testable
- **User Story 5 (Delete)**: Can start after Foundational - Depends on US1 (TaskList), independently testable

### Within Each User Story

- Repository methods before Service methods
- Service methods before API routes
- Backend services before Frontend services
- Frontend services before Frontend components
- Story complete before moving to next priority

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T004, T005, T006, T007 can run in parallel

**Foundational Phase (Phase 2)**:
- Backend foundation (T008-T011), Auth foundation (T012-T014), API structure (T015-T020) can run in parallel

**User Story 1 (View)**:
- Backend implementation (T021-T027) can start before frontend
- Frontend services (T028-T032) and components (T033-T038) parallel within frontend

**User Story 2 (Create)**:
- Backend implementation (T039-T047) and Frontend services (T048-T050) parallel

**User Story 3 (Update)**:
- Backend implementation (T057-T064) and Frontend services (T065-T066) parallel

**User Story 4 (Complete)**:
- Backend implementation (T071-T077) and Frontend services (T078) parallel

**User Story 5 (Delete)**:
- Backend implementation (T082-T088) and Frontend services (T089) parallel

**Integration Phase (Phase 8)**:
- Backend integration (T096-T100) and Frontend integration (T101-T105) can run in parallel
- T106, T107, T108, T109, T110 can run in parallel

---

## Parallel Example: User Story 1 (View)

```bash
# Backend - can run sequentially:
T021: Create task_repository.py with get_by_user()
T022: Implement user_id WHERE clause filtering
T023: Create task_service.py with get_user_tasks()
T024: Create GET /api/tasks endpoint
T025: Apply get_current_user dependency
T026: Return 404 for no tasks
T027: Return appropriate HTTP status codes

# Frontend Services - can run in parallel with Backend after T023:
T028: Create Task interface in types/tasks.ts
T029: Create TaskService class in services/tasks.ts
T030: Implement fetchTasks() method
T031: Add JWT token handling
T032: Add error handling

# Frontend Components - can run in parallel with Frontend Services:
T033: Create tasks/page.tsx Server Component
T034: Create TaskList.tsx component
T035: Implement empty state
T036: Add visual distinction for completed tasks
T037: Add loading state
T038: Add error boundary
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (View)
4. Complete Phase 4: User Story 2 (Create)
5. **STOP and VALIDATE**: Test View and Create independently
6. Deploy/demo MVP

**Deliverable**: Users can sign up, see task list, and create tasks (functional MVP)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (View) → Test independently → Deploy/Demo
3. Add User Story 2 (Create) → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 (Update) → Test independently → Deploy/Demo
5. Add User Story 4 (Complete) → Test independently → Deploy/Demo
6. Add User Story 5 (Delete) → Test independently → Deploy/Demo
7. Complete Integration & Polish → Production-ready

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A (Backend Agent): User Stories 1-5 backend implementation
   - Developer B (Frontend Agent): User Stories 1-5 frontend services
   - Developer C (Frontend Agent): User Stories 1-5 frontend components
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Backend-first approach: All user stories start with backend implementation
- Agent labels indicate responsible AI agent (Backend, Frontend, Auth, Database)
- Multi-user isolation is enforced at repository layer ONLY (T022, T058, T071, T082)
- JWT authentication is required on ALL API endpoints (T025, T044, T061, T075, T086)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Verify against constitution before completing each phase
