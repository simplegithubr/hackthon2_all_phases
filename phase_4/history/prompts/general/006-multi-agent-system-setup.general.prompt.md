---
id: 006
title: Multi-Agent System Setup
stage: general
date: 2025-12-31
surface: agent
model: claude-sonnet-4.5
feature: none
branch: master
user: unknown
command: none
labels: ["system-setup", "multi-agent"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - none
tests:
 - none
---

## Prompt

You are operating in a multi-agent system.

Primary Agent:
- architect.agent.md

Available Agents:
- backend.agent.md
- frontend.agent.md
- auth.agent.md
- database.agent.md

Available Sub-Agents:
- api-designer
- jwt-verifier
- ui-layout
- orm-modeler

Available Skills:
- jwt-auth
- rest-api
- sqlmodel
- nextjs-app-router
- better-auth

Rules:
- Follow agent responsibilities strictly
- Delegate tasks to sub-agents when needed
- Use skills instead of re-inventing logic
- Do not implement features yet
- First finalize architecture & skeleton

## Response snapshot

Acknowledged the multi-agent system structure. Operating as the architect agent with:
- Primary role coordination
- Team: backend, frontend, auth, database agents
- Sub-agents: api-designer, jwt-verifier, ui-layout, orm-modeler
- Skills: jwt-auth, rest-api, sqlmodel, nextjs-app-router, better-auth

Confirmed understanding of rules:
1. Strict adherence to agent responsibilities
2. Delegate to sub-agents when appropriate
3. Leverage existing skills
4. Focus on architecture & skeleton first (no feature implementation)

## Outcome

- ✅ Impact: Multi-agent system context established for architect agent operations
- 🧪 Tests: none
- 📁 Files: none
- 🔁 Next prompts: none
- 🧠 Reflection: System setup information; architect agent ready to coordinate within defined constraints

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
