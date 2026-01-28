# Prompt History Record (PHR)

| ID | TITLE | STAGE | DATE_ISO | SURFACE |
|----|-------|-------|----------|---------|
| 003 | Fix AuthService API connectivity | green | 2026-01-06 | agent |

## Metadata
- **MODEL**: claude-sonnet-4-5-20250929
- **FEATURE**: task-crud
- **BRANCH**: main
- **USER**: sagardeveloper

## Command
`AuthService was returning 404 because it was using a local localhost URL and missing the /api prefix when deployed.`

## Problem/Context
The logs showed 404 Not Found for `/auth/signup`. This was because the frontend was calling the root of the server instead of the `/api` prefixed routes, and the default URL was pointing to localhost.

## Proposed Changes
- Updated `AuthService` constructor to use `NEXT_PUBLIC_API_URL`.
- Defaulted the URL to the production HuggingFace space URL.

## Files Affected
- `frontend/src/services/auth.ts`

## Tests Run
- Verified path consistency with `backend/src/main.py`.

## Prompt Text
The user provided logs showing 404 errors for signup requests.

## Response Text
I have updated the AuthService to use the correct absolute API URL and ensure the /api prefix is applied.

## Outcome/Evaluation
The authentication requests should now correctly hit the HuggingFace backend at `/api/auth/signup`.
