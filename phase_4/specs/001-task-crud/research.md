# Research: Task CRUD Feature

**Feature**: 001-task-crud
**Date**: 2025-12-31
**Purpose**: Document technical decisions and best practices for Task CRUD implementation

## Technology Decisions

### Decision 1: Backend Framework - FastAPI

**Decision**: Use FastAPI for Python backend API layer

**Rationale**:
- Native async/await support for scalable I/O operations
- Built-in Pydantic validation (SQLModel compatible)
- Automatic OpenAPI documentation generation
- Fast development velocity suitable for hackathon
- Excellent ecosystem with authentication middleware libraries

**Alternatives Considered**:
- **Flask**: Too synchronous, requires additional libraries for async and validation
- **Django**: Too heavy for simple CRUD feature, over-engineered for hackathon timeline
- **Tornado**: Less active community, smaller ecosystem than FastAPI

---

### Decision 2: ORM - SQLModel

**Decision**: Use SQLModel (Pydantic + SQLAlchemy) for database models

**Rationale**:
- Single source of truth for types (works with both Pydantic validation and SQLAlchemy)
- Automatic type conversion between Python types and database types
- Native async support for database operations
- Constitution requires strict typing - SQLModel enforces this
- Simpler than pure SQLAlchemy for CRUD operations

**Alternatives Considered**:
- **SQLAlchemy Core**: More flexibility but no automatic validation, requires manual type mapping
- **Tortoise ORM**: Excellent async support but less compatible with Pydantic/FastAPI ecosystem
- **Django ORM**: Tied to Django framework, not compatible with FastAPI

---

### Decision 3: Frontend Framework - Next.js 16+ with App Router

**Decision**: Use Next.js 16+ with App Router (not Pages Router)

**Rationale**:
- Server Components by default (better performance, less client-side JavaScript)
- Built-in file-based routing simplifies navigation
- Server-side rendering improves SEO and initial page load
- App Router is current standard (Pages Router is legacy)
- Constitution requires App Router conventions

**Alternatives Considered**:
- **React SPA (Create React App)**: No server-side rendering, client-side only, slower initial load
- **Vite + React**: Fast development but no built-in routing or SSR
- **Next.js Pages Router**: Legacy approach, being deprecated

---

### Decision 4: Database - Neon Serverless PostgreSQL

**Decision**: Use Neon for PostgreSQL hosting

**Rationale**:
- Serverless architecture (pay-per-use, no server management)
- PostgreSQL is robust, reliable, supports full SQL features
- Neon's branching feature enables testing migrations safely
- Serverless Postgres is well-suited for hackathon (quick setup, no ops overhead)
- SQLModel has excellent PostgreSQL driver support (asyncpg)

**Alternatives Considered**:
- **Supabase**: Good but more complex, additional services (auth, storage) not needed
- **Railway**: Full platform (not just database), potentially overkill
- **Traditional VPS + PostgreSQL**: Requires manual setup, maintenance, not hackathon-friendly

---

### Decision 5: Authentication - Better Auth

**Decision**: Use Better Auth for authentication and JWT issuance

**Rationale**:
- Designed for Next.js 16+ App Router
- Native JWT support with token refresh
- Built-in user management (signup, login, sessions)
- Constitution specifies Better Auth as requirement
- Seamless integration with both frontend and backend

**Alternatives Considered**:
- **Auth0**: Third-party SaaS, adds dependency, cost, and latency
- **Custom JWT implementation**: Re-inventing authentication wheel, security risks
- **NextAuth.js**: Legacy version (v4), Less compatible with App Router

---

### Decision 6: Architecture Pattern - Layered (Repository Pattern)

**Decision**: Use repository pattern for database access layer

**Rationale**:
- Enforces user_id filtering at ONE place (repository layer)
- Improves testability (can mock repository for service tests)
- Separates business logic (service layer) from data access (repository)
- Constitution mandates repository pattern to prevent cross-user data leaks
- Easier to audit and verify all queries include user_id WHERE clause

**Alternatives Considered**:
- **Direct DB access in routes**: Violates constitution (no separation of concerns), harder to test
- **Active Record pattern**: Mixing business logic with data model, harder to enforce user_id filtering
- **Service-only pattern**: No dedicated data access layer, harder to audit queries

---

### Decision 7: Frontend-Backend Communication - REST API

**Decision**: Use RESTful API with JSON for frontend-backend communication

**Rationale**:
- Simple, widely understood standard
- Native support in FastAPI (automatic OpenAPI spec generation)
- Easy to test and debug
- Constitution mentions REST API skill, indicating this pattern is expected
- GraphQL would be overkill for simple CRUD operations

**Alternatives Considered**:
- **GraphQL**: Over-engineering for CRUD feature, adds complexity (resolvers, types, caching)
- **gRPC**: Binary protocol, less compatible with browser, requires additional tooling
- **Server Actions (Next.js)**: Couples frontend to backend, violates monorepo separation

---

### Decision 8: Frontend State Management - React Server Components + Client State

**Decision**: Use React Server Components for data fetching, local client state for interactivity

**Rationale**:
- Server Components fetch data directly (faster, less client JS)
- Client Components only for forms, toggles (minimal client-side state)
- No need for Redux/Zustand (too complex for simple CRUD)
- Next.js 16+ native support for Server Components

**Alternatives Considered**:
- **Client Components Only**: Slower initial load, more client-side JavaScript
- **Redux Toolkit**: Overkill for simple CRUD, adds boilerplate
- **Zustand**: Lighter than Redux but unnecessary when Server Components handle most state

---

### Decision 9: Frontend Styling - Tailwind CSS

**Decision**: Use Tailwind CSS for styling

**Rationale**:
- Utility-first approach speeds up development (no custom CSS files)
- Constitution specifies "no inline styles; use Tailwind CSS or component library"
- Tailwind is industry standard, excellent documentation
- Good for hackathon (fast iteration, no CSS files to maintain)

**Alternatives Considered**:
- **CSS Modules**: Component-scoped CSS, but requires writing custom CSS
- **Styled Components**: CSS-in-JS, adds runtime overhead
- **Shadcn UI**: Component library built on Tailwind (could use in Phase 3+)

---

## Best Practices Research

### Best Practice 1: JWT Token Management

**Implementation**:
- Store JWT in HTTP-only cookies (not localStorage) to prevent XSS attacks
- Frontend checks token expiry before making API requests
- Backend validates JWT signature and expiration on every request
- Implement token refresh via Better Auth to avoid forced logouts
- Clear token on logout

**Security Considerations**:
- Use strong secret key for JWT signing (environment variable)
- Set appropriate token expiry (e.g., 15 minutes for access, 7 days for refresh)
- Include user_id in JWT claims for authorization
- Verify token issuer (iss) claim

---

### Best Practice 2: Multi-User Data Isolation

**Implementation**:
- Enforce user_id filtering AT REPOSITORY LAYER ONLY
- Never pass user_id from service layer to repository
- Repository always receives user_id from JWT (auth context)
- All SELECT queries include `WHERE user_id = ?`
- All INSERT/UPDATE/DELETE queries validate user_id matches

**Testing Strategy**:
- Create contract tests that verify each repository method includes user_id
- Use test fixtures with multiple users to verify isolation
- Add database foreign key constraints (user_id → users.id)

---

### Best Practice 3: Error Handling

**Backend Error Responses**:
- 200 OK - Successful operation
- 201 Created - Resource created successfully
- 400 Bad Request - Validation error (e.g., empty title)
- 401 Unauthorized - Missing, invalid, or expired JWT token
- 403 Forbidden - User trying to access another user's data
- 404 Not Found - Task not found or not owned by user
- 500 Internal Server Error - Unexpected server error

**Frontend Error Handling**:
- 401 → Redirect to login page with message "Please sign in"
- 403 → Show error "You don't have permission to access this resource"
- 400 → Show validation error message (e.g., "Task title is required")
- 500 → Show generic error "Something went wrong. Please try again."
- Network errors → Show "Unable to connect. Check your internet."

---

### Best Practice 4: Type Safety Across Frontend-Backend

**Implementation**:
- SQLModel defines backend types (task.py)
- Generate TypeScript types from SQLModel OR manually sync (document in contracts/)
- Frontend service (tasks.ts) uses these TypeScript interfaces
- Contract tests verify backend responses match frontend types
- Run TypeScript strict mode to catch type errors at build time

**Tools**:
- SQLModel's `model_rebuild()` (if available) or manual sync
- Pydantic to TypeScript generators (e.g., `pydantic-to-typescript`)
- OpenAPI spec generation from FastAPI (`/openapi.json`)

---

### Best Practice 5: Performance Optimization

**Backend**:
- Use async database sessions (SQLAlchemy async mode)
- Add database indexes on `user_id` and `created_at` columns
- Implement pagination (e.g., 50 tasks per page) for large lists
- Use connection pooling (SQLAlchemy engine configuration)

**Frontend**:
- Server Components for initial data fetch (faster time-to-first-byte)
- Client Components only for interactive elements (forms, toggles)
- Optimize images and assets (if added in future phases)
- Use React.memo() for expensive re-renders (if needed)

---

## Integration Points

### Backend-Neon PostgreSQL Integration

**Connection String**:
```
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**Configuration**:
- Use environment variable `DATABASE_URL` (never hardcode)
- Enable SSL for production (Neon requires it)
- Use asyncpg driver for async SQLAlchemy
- Set pool size appropriately (e.g., 5-20 connections)

---

### Frontend-Better Auth Integration

**Installation**:
```bash
npm install better-auth
```

**Configuration**:
- Configure Better Auth provider (email/password, social login if needed)
- Set JWT issuer and secret
- Configure token expiry times
- Enable HTTP-only cookies

**Backend Integration**:
- Shared JWT secret between Better Auth (frontend) and FastAPI (backend)
- Backend validates JWTs issued by Better Auth

---

### Frontend-FastAPI Integration

**Base URL**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

**Service Layer**:
```typescript
// frontend/src/services/tasks.ts
class TaskService {
  private baseUrl = process.env.NEXT_PUBLIC_API_URL;

  async fetchTasks() {
    const response = await fetch(`${this.baseUrl}/tasks`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    // ...
  }
}
```

---

## Risks and Mitigations

### Risk 1: Cross-User Data Access

**Mitigation**:
- Enforce user_id filtering at repository layer ONLY (constitution requirement)
- Add automated tests verifying user_id WHERE clause in all queries
- Database foreign key constraints prevent orphaned tasks

### Risk 2: JWT Token Theft

**Mitigation**:
- Store JWT in HTTP-only cookies (not localStorage)
- Use HTTPS in production
- Set appropriate token expiry times
- Implement token refresh to minimize exposure window

### Risk 3: Database Connection Exhaustion

**Mitigation**:
- Configure connection pooling (SQLAlchemy engine)
- Use async database operations
- Close connections after use (context managers)
- Monitor connection count in production

### Risk 4: Frontend-Backend Type Mismatch

**Mitigation**:
- Maintain TypeScript types in contracts/ directory
- Run contract tests on every build
- Use OpenAPI spec for automated validation
- Manual review of type changes

---

## Conclusion

All technical decisions are justified with clear rationales. The chosen stack (FastAPI, SQLModel, Next.js 16+, Neon PostgreSQL, Better Auth) is well-suited for hackathon timeline while adhering to all constitution principles. Best practices documented ensure security, performance, and type safety.

**Status**: ✅ Ready for Phase 1 (Data Model & Contracts)
