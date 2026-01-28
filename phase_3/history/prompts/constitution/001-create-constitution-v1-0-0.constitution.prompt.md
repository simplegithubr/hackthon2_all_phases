---
id: 001
title: Create Constitution v1.0.0
stage: constitution
date: 2025-12-31
surface: agent
model: claude-sonnet-4.5
feature: none
branch: master
user: unknown
command: sp/constitution
labels: ["constitution", "governance", "initial"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

sp/constitution Create a project constitution for Phase 2 of a Todo Full-Stack Web Application.

Context:
- This is Phase 2 of a hackathon project

Tech Stack:
- Frontend: Next.js 16+ (App Router, TypeScript)
- Backend: Python FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Better Auth with JWT
- Architecture: Monorepo (frontend + backend)

Constitution Must Define:
1. Core project principles
2. Coding standards (frontend & backend)
3. Security rules (JWT required everywhere)
4. Multi-user data isolation rules
5. Spec-driven development rules
6. What is allowed vs not allowed
7. How Claude Code should behave in this repo

Output:
- A clear, enforceable constitution
- Written in professional but simple language
- Saved as: specs/constitution.md

## Response snapshot

Created the project constitution at `.specify/memory/constitution.md` (v1.0.0) with:

Core Principles:
1. Security First (JWT) - JWT required on every endpoint, no public APIs without auth
2. Multi-User Data Isolation - All user data filtered by user_id, no cross-user access
3. Spec-Driven Development - spec → plan → tasks → implementation workflow mandatory
4. Monorepo Architecture - Frontend (Next.js) and Backend (FastAPI) in monorepo, shared types
5. Type Safety - Strict typing (Python type hints, TypeScript strict mode), no `any` types

Coding Standards:
- Frontend: Server Components by default, App Router conventions, no inline styles, error boundaries
- Backend: SQLModel for validation, async I/O, dependency injection, repository pattern

Claude Code Behavior Rules:
- Operate as architect agent, delegate to sub-agents
- Use skills instead of re-inventing
- Never implement without architecture/skeleton
- Validate against constitution
- Create PHRs

Not Allowed:
- Skipping spec-driven workflow
- Bypassing JWT auth
- Multi-user data isolation violations
- `any` types
- Hardcoded secrets

Governance: Semantic versioning (MAJOR/MINOR/PATCH), template updates required, compliance verification

## Outcome

- ✅ Impact: Initial constitution created with all required governance principles for Todo Full-Stack App (Phase 2)
- 🧪 Tests: none
- 📁 Files: 1 file created/updated (.specify/memory/constitution.md)
- 🔁 Next prompts: none
- 🧠 Reflection: Constitution defines clear, enforceable rules aligned with tech stack and multi-agent system. Templates already aligned; CLAUDE.md may need updates.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
