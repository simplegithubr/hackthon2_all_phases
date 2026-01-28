<!--
SYNC IMPACT REPORT
Version change: none → 1.0.0 (INITIAL CONSTITUTION)
List of modified principles: N/A (initial creation)
Added sections:
- Security First (JWT)
- Multi-User Data Isolation
- Spec-Driven Development
- Monorepo Architecture
- Type Safety
- Coding Standards (Frontend & Backend)
- Claude Code Behavior Rules
Removed sections: N/A (initial creation)
Templates requiring updates:
  ✅ plan-template.md (constitution check section already in place)
  ✅ spec-template.md (already structured for spec-driven development)
  ✅ tasks-template.md (already organized by user stories)
  ⚠ CLAUDE.md (may need updates to align with new constitution principles)
Follow-up TODOs: None - all placeholders filled
-->

# Todo Full-Stack Web Application (Phase 2) Constitution

## Core Principles

### Security First (JWT)
Every API endpoint and protected route MUST enforce JWT authentication. JWTs are issued via Better Auth and MUST be validated on every backend request using the JWT verification skill. Expiration checking and signature verification are non-negotiable. No public APIs may expose user data without authentication.

### Multi-User Data Isolation
All user data MUST be isolated by `user_id`. Database queries MUST include a WHERE clause filtering by `user_id` for all user-owned resources (todos, preferences, settings). Never return data for one user to another. Cross-user data access is strictly prohibited without explicit authorization.

### Spec-Driven Development
All features MUST follow the spec-driven development workflow: spec → plan → tasks → implementation. No code may be written without a corresponding spec.md, plan.md, and tasks.md file. Changes to requirements must be reflected in the spec before implementation. This principle ensures traceability from user intent to code.

### Monorepo Architecture
The project uses a monorepo structure with `frontend/` (Next.js 16+) and `backend/` (FastAPI) directories. Frontend and backend share type definitions and contracts via `backend/src/models/` and TypeScript interfaces. The monorepo enables coordinated releases and shared development standards across both services.

### Type Safety
All code MUST be strictly typed: Python uses type hints (SQLModel, Pydantic), TypeScript uses strict mode. No `any` types are allowed in production code. Database models are the single source of truth for type definitions. Type safety prevents runtime errors and improves maintainability.

## Coding Standards

### Frontend (Next.js 16+, TypeScript, App Router)
- Use Server Components by default; Client Components only when interactivity required
- Follow the App Router conventions: `app/` directory, `layout.tsx`, `page.tsx`
- API calls go through frontend services (`frontend/src/services/`) which type-check backend responses
- No inline styles; use Tailwind CSS or a component library
- Error boundaries for route segments; loading states for async operations

### Backend (FastAPI, SQLModel, Python)
- All endpoints MUST use SQLModel models for request/response validation
- Async functions for all I/O operations (database, external APIs)
- Dependencies injected via FastAPI's dependency system
- Standardized error responses: HTTP status codes + structured error messages
- All database queries in repository pattern or service layer, not in route handlers

## Claude Code Behavior Rules

Claude Code MUST operate as an architect agent in a multi-agent system:
- Follow agent responsibilities strictly (architect delegates to backend, frontend, auth, database agents)
- Delegate tasks to sub-agents (api-designer, jwt-verifier, ui-layout, orm-modeler) when needed
- Use skills (jwt-auth, rest-api, sqlmodel, nextjs-app-router, better-auth) instead of re-inventing logic
- Never implement features without first finalizing architecture and skeleton
- Always validate against the constitution before suggesting changes
- Create PHRs for every significant interaction

What is NOT allowed:
- Skipping the spec → plan → tasks workflow
- Bypassing JWT authentication in any endpoint
- Writing code that violates multi-user data isolation
- Adding `any` types or ignoring type errors
- Hardcoding secrets or credentials (use environment variables)
- Modifying templates without updating the constitution if principles change

## Governance

Amendments to this constitution require:
1. Document the proposed change with rationale
2. Update version using semantic versioning:
   - MAJOR: Principle removal or redefinition that breaks backward compatibility
   - MINOR: New principle added or materially expanded guidance
   - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
3. Propagate changes to dependent templates and documentation
4. Record ratification date and update Last Amended date

All code reviews and planning sessions must verify compliance with these principles. Any principle violation must be explicitly justified in the plan's Complexity Tracking table. Use CLAUDE.md for runtime development guidance; the constitution is the source of truth for project governance.

**Version**: 1.0.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2025-12-31
