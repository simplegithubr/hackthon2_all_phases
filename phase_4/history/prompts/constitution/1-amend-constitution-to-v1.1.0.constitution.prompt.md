---
id: 1
title: Amend constitution to v1.1.0
stage: constitution
date: 2026-01-13
surface: agent
model: sonnet-4-5
feature: none
branch: main
user: Claude
command: sp.constitution
labels: ["governance", "constitution", "phase-3", "todo-chatbot"]
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

```text
You are operating under the Todo AI Chatbot Constitution.

This constitution defines the immutable rules, boundaries, and
operating principles for the AI-powered Todo Chatbot system.

This system is an extension of an already existing Phase II
Full-Stack Todo Application (FastAPI + SQLModel + Neon PostgreSQL).

The AI Chatbot MUST integrate with the existing backend.
NO duplicate logic, schemas, or database models may be created.

────────────────────────────────────────
CORE PURPOSE
────────────────────────────────────────

The purpose of this system is to allow authenticated users
to manage their todo tasks using natural language.

The chatbot must support:
- Creating tasks
- Listing tasks
- Updating tasks
- Completing tasks
- Deleting tasks
- Maintaining conversation history
- Resuming conversations after restart

All operations MUST be executed via
```

## Response snapshot

Updated the project constitution to version 1.1.0 to reflect the Todo AI Chatbot (Phase III) system. The changes include:

1. Renamed the constitution from "Todo Full-Stack Web Application (Phase 2) Constitution" to "Todo AI Chatbot Constitution (Phase III)"
2. Added new principles:
   - MCP Server Architecture: Specifies that the AI Chatbot system must expose operations via MCP tools
   - Natural Language Processing for Task Management: Defines requirements for interpreting natural language requests
3. Added AI Chatbot specific coding standards section
4. Updated Claude Code Behavior Rules to include AI agents and MCP tools
5. Added new restrictions:
   - Direct database access from AI chatbot components is prohibited
   - Storing state in the MCP server is prohibited
6. Updated the version to 1.1.0 with MINOR increment reflecting the Phase III additions

The update follows the existing template structure while incorporating the specific requirements for the AI chatbot system that integrates with the existing Phase II backend.

## Outcome

- ✅ Impact: Updated constitution to reflect Phase III Todo AI Chatbot requirements
- 🧪 Tests: none
- 📁 Files: 1 file updated (.specify/memory/constitution.md)
- 🔁 Next prompts: Will likely follow up with spec, plan, and tasks for Phase III implementation
- 🧠 Reflection: Constitution properly updated to govern the new AI chatbot functionality while maintaining compatibility with existing Phase II backend

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): standard constitution update
- Next experiment (smallest change to try): Begin Phase III spec development