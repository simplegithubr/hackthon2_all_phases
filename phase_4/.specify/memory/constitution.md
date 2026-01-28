<!--
SYNC IMPACT REPORT
Version change: 1.1.0 → 1.2.0 (MINOR: Phase IV Local Kubernetes Deployment addition)
List of modified principles:
- Todo AI Chatbot Constitution (Phase III) → Local Kubernetes Deployment Constitution (Phase IV)
Added sections:
  - Containerization Standards
  - Helm Chart Management
  - Minikube Deployment
  - AI-Assisted Operations
  - Zero-Cost Local Setup
  - Horizontal Scaling Requirements
  - Resilient Architecture
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md (updated constitution reference)
  ✅ spec-template.md (updated constitution reference)
  ✅ tasks-template.md (updated constitution reference)
  ✅ CLAUDE.md (updated to reflect new constitution principles)
Follow-up TODOs: None - all placeholders filled
-->

# Local Kubernetes Deployment Constitution (Phase IV)

## Core Principles

### Security First (JWT)
Every API endpoint and protected route MUST enforce JWT authentication. JWTs are issued via Better Auth and MUST be validated on every backend request using the JWT verification skill. Expiration checking and signature verification are non-negotiable. No public APIs may expose user data without authentication.

### Multi-User Data Isolation
All user data MUST be isolated by `user_id`. Database queries MUST include a WHERE clause filtering by `user_id` for all user-owned resources (todos, preferences, settings). Never return data for one user to another. Cross-user data access is strictly prohibited without explicit authorization.

### Spec-Driven Development
All features MUST follow the spec-driven development workflow: spec → plan → tasks → implementation. No code may be written without a corresponding spec.md, plan.md, and tasks.md file. Changes to requirements must be reflected in the spec before implementation. This principle ensures traceability from user intent to code.

### MCP Server Architecture
The AI Chatbot system MUST expose operations via MCP (Model Context Protocol) tools for natural language processing. All task operations (add, list, update, complete, delete) MUST be available as structured MCP tools. The server MUST remain stateless and execute operations against the existing Phase II database.

### Natural Language Processing for Task Management
The chatbot MUST interpret natural language user requests and map them to appropriate MCP tool invocations. The system MUST never guess or infer task_id from natural language - always use MCP tools for identification. All operations MUST be scoped to the authenticated user context.

### Monorepo Architecture
The project uses a monorepo structure with `frontend/` (Next.js 16+), `backend/` (FastAPI), and AI agent components. Frontend and backend share type definitions and contracts via `backend/src/models/` and TypeScript interfaces. The monorepo enables coordinated releases and shared development standards across all services.

### Type Safety
All code MUST be strictly typed: Python uses type hints (SQLModel, Pydantic), TypeScript uses strict mode. No `any` types are allowed in production code. Database models are the single source of truth for type definitions. Type safety prevents runtime errors and improves maintainability.

### Containerization Standards
All application components MUST be containerized using Docker. The system MUST use Gordon for Docker image creation to ensure consistency and proper multi-stage builds. Container images MUST follow semantic versioning and include proper labels. Images MUST be lightweight, secure, and built with minimal attack surface. All containers MUST run as non-root users where possible.

### Helm Chart Management
Kubernetes deployments MUST use Helm charts for packaging and configuration management. Charts MUST be generated using kubectl-ai or kagent for AI-assisted optimization. All configurations MUST be parameterized through values files to enable environment-specific deployments. Charts MUST include proper health checks, resource limits, and security contexts. Versioning of Helm charts MUST follow semantic versioning aligned with application versions.

### Minikube Deployment
All Kubernetes deployments MUST be compatible with local Minikube clusters. The deployment process MUST be fully automated and reproducible. Services MUST be accessible via NodePort or LoadBalancer configurations suitable for local development. Persistent storage MUST be properly configured for local development scenarios. Cluster resources MUST be optimized for local resource constraints while maintaining functionality.

### Statelessness Requirement
All server components MUST be stateless to enable horizontal scaling. Session data and temporary files MUST be stored in external services (Redis, database) or mounted volumes. Application MUST handle pod restarts and rescheduling gracefully. Configuration MUST be provided via environment variables or ConfigMaps, not baked into images.

### Horizontal Scaling Requirements
The system MUST support horizontal pod autoscaling based on CPU and memory metrics. Services MUST be designed to handle distributed load without shared state between instances. Database connections MUST be managed efficiently with connection pooling. Load balancing MUST distribute requests evenly across pod replicas.

### Resilient Architecture
The system MUST implement proper health checks (liveness and readiness probes) to ensure reliable service discovery and traffic routing. Circuit breaker patterns MUST be implemented for external service calls. Retry mechanisms with exponential backoff MUST be applied to transient failures. Graceful degradation strategies MUST be in place for partial system failures.

### AI-Assisted Operations
Kubernetes operations MUST leverage AI tools (Gordon, kubectl-ai, kagent) for intelligent configuration and optimization. Deployment processes MUST incorporate AI-driven resource recommendations. Monitoring and alerting MUST use AI-assisted anomaly detection. Troubleshooting workflows MUST integrate AI-powered diagnostics.

### Zero-Cost Local Setup
The entire deployment stack MUST run on local hardware without cloud costs. Resource consumption MUST be optimized for typical developer machines (8GB+ RAM, 4+ cores). Installation process MUST be automated and idempotent. Development cycle times MUST be optimized for rapid iteration.

### Testability Requirements
All Kubernetes configurations MUST include comprehensive test strategies. Service mesh configurations (if applicable) MUST support traffic mirroring for testing. Blue-green deployment patterns MUST be supported for safe rollouts. Rollback procedures MUST be tested and documented.

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

### AI Chatbot (MCP Tools, Natural Language Processing)
- MCP tools MUST be stateless and scoped to user_id
- Natural language processing MUST validate user intent before executing operations
- AI agents MUST never access database directly - always use MCP tools
- MCP tools MUST validate ownership before executing operations
- Error handling MUST be clear and user-friendly for natural language interactions

### Kubernetes Configuration (Helm, Docker, Minikube)
- All manifests MUST use YAML format with consistent indentation
- Helm templates MUST follow best practices: proper escaping, default values, validation
- Security contexts MUST be defined for all containers
- Resource requests and limits MUST be specified for all deployments
- Health checks (liveness/readiness) MUST be implemented for all services
- Environment-specific configurations MUST use values files, not hardcoded values
- Image pull policies MUST be appropriate for environment (Always for dev, IfNotPresent for prod)

## Claude Code Behavior Rules

Claude Code MUST operate as an architect agent in a multi-agent system:
- Follow agent responsibilities strictly (architect delegates to backend, frontend, auth, database, AI, and Kubernetes agents)
- Delegate tasks to sub-agents (api-designer, jwt-verifier, ui-layout, orm-modeler, todo-ai-orchestrator, task-manager-agent, kubernetes-deployer) when needed
- Use skills (jwt-auth, rest-api, sqlmodel, nextjs-app-router, better-auth, mcp-tools, containerization, helm-chart, minikube-deployment) instead of re-inventing logic
- Never implement features without first finalizing architecture and skeleton
- Always validate against the constitution before suggesting changes
- Create PHRs for every significant interaction

What is NOT allowed:
- Skipping the spec → plan → tasks workflow
- Bypassing JWT authentication in any endpoint
- Writing code that violates multi-user data isolation
- Adding `any` types or ignoring type errors
- Hardcoding secrets or credentials (use environment variables and Kubernetes secrets)
- Modifying templates without updating the constitution if principles change
- Direct database access from AI chatbot components - always use MCP tools
- Storing state in the MCP server - all operations must be stateless
- Deploying without proper containerization and Helm packaging
- Deploying to cloud platforms - Minikube only for Phase IV
- Implementing complex CI/CD pipelines - basic automation only

## Governance

Amendments to this constitution require:
1. Document the proposed change with rationale
2. Update version using semantic versioning:
   - MAJOR: Principle removal or redefinition that breaks backward compatibility
   - MINOR: New principle added or materially expanded guidance (e.g., Phase IV additions)
   - PATCH: Clarifications, wording, typo fixes, non-semantic refinements
3. Propagate changes to dependent templates and documentation
4. Record ratification date and update Last Amended date

All code reviews and planning sessions must verify compliance with these principles. Any principle violation must be explicitly justified in the plan's Complexity Tracking table. Use CLAUDE.md for runtime development guidance; the constitution is the source of truth for project governance.

**Version**: 1.2.0 | **Ratified**: 2025-12-31 | **Last Amended**: 2026-01-27